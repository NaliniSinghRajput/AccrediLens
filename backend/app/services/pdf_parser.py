import re
from dataclasses import dataclass
from pathlib import Path

import fitz
import pdfplumber


HEADING_RE = re.compile(r"^(\d+(\.\d+)*\s+)?[A-Z][A-Za-z0-9 ,:;()/\-]{2,90}$")
FIGURE_RE = re.compile(r"^(fig\.|figure)\s*\d+", re.IGNORECASE)
TABLE_RE = re.compile(r"^(table)\s*\d+", re.IGNORECASE)
REFERENCES_RE = re.compile(r"^(references|bibliography)\b", re.IGNORECASE)


@dataclass
class ExtractedPage:
    page_number: int
    text: str


@dataclass
class ExtractedParagraph:
    page_number: int
    section_title: str
    paragraph_number: int
    source_type: str
    text: str


@dataclass
class ParsedPaper:
    title: str | None
    pages: list[ExtractedPage]
    paragraphs: list[ExtractedParagraph]


def clean_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def is_heading(line: str) -> bool:
    stripped = line.strip()
    if len(stripped.split()) > 12:
        return False
    if REFERENCES_RE.match(stripped):
        return True
    if stripped.lower() in {"abstract", "introduction", "methodology", "methods", "results", "discussion", "conclusion"}:
        return True
    return bool(HEADING_RE.match(stripped)) and not stripped.endswith(".")


def source_type_for(section_title: str, paragraph: str) -> str:
    lower_section = section_title.lower()
    lower_para = paragraph.lower()
    if "abstract" in lower_section:
        return "abstract"
    if REFERENCES_RE.match(section_title):
        return "references"
    if TABLE_RE.match(paragraph):
        return "table"
    if FIGURE_RE.match(paragraph):
        return "figure caption"
    if "method" in lower_section:
        return "methodology"
    if "result" in lower_section:
        return "result"
    if "discussion" in lower_section:
        return "discussion"
    if "conclusion" in lower_section:
        return "conclusion"
    if "table" in lower_para[:30]:
        return "table"
    return "body text"


def split_paragraphs(page_text: str) -> list[str]:
    blocks = [clean_text(block) for block in re.split(r"\n\s*\n", page_text) if clean_text(block)]
    if len(blocks) > 1:
        return blocks

    lines = [clean_text(line) for line in page_text.splitlines() if clean_text(line)]
    paragraphs: list[str] = []
    buffer: list[str] = []
    for line in lines:
        if is_heading(line):
            if buffer:
                paragraphs.append(clean_text(" ".join(buffer)))
                buffer = []
            paragraphs.append(line)
            continue
        buffer.append(line)
        if line.endswith((".", "?", "!")) and len(" ".join(buffer).split()) > 70:
            paragraphs.append(clean_text(" ".join(buffer)))
            buffer = []
    if buffer:
        paragraphs.append(clean_text(" ".join(buffer)))
    return paragraphs


def extract_tables(pdf_path: Path) -> dict[int, list[str]]:
    tables_by_page: dict[int, list[str]] = {}
    try:
        with pdfplumber.open(str(pdf_path)) as pdf:
            for page_index, page in enumerate(pdf.pages, start=1):
                tables = page.extract_tables() or []
                for idx, table in enumerate(tables, start=1):
                    rows = []
                    for row in table:
                        cells = [clean_text(str(cell or "")) for cell in row]
                        if any(cells):
                            rows.append(" | ".join(cells))
                    if rows:
                        table_text = f"Table {idx} on page {page_index}\n" + "\n".join(rows)
                        tables_by_page.setdefault(page_index, []).append(table_text)
    except Exception:
        return tables_by_page
    return tables_by_page


def parse_pdf(pdf_path: Path) -> ParsedPaper:
    pages: list[ExtractedPage] = []
    paragraphs: list[ExtractedParagraph] = []
    tables_by_page = extract_tables(pdf_path)
    title: str | None = None
    current_section = "Unknown"
    paragraph_counter_by_scope: dict[tuple[int, str], int] = {}

    with fitz.open(str(pdf_path)) as doc:
        for page_index, page in enumerate(doc, start=1):
            text = clean_text(page.get_text("text"))
            pages.append(ExtractedPage(page_number=page_index, text=text))
            if page_index == 1 and text:
                title = next((line.strip() for line in text.splitlines() if len(line.strip()) > 10), None)

            for block in split_paragraphs(text):
                if is_heading(block):
                    current_section = block
                    continue

                key = (page_index, current_section)
                paragraph_counter_by_scope[key] = paragraph_counter_by_scope.get(key, 0) + 1
                paragraphs.append(
                    ExtractedParagraph(
                        page_number=page_index,
                        section_title=current_section,
                        paragraph_number=paragraph_counter_by_scope[key],
                        source_type=source_type_for(current_section, block),
                        text=block,
                    )
                )

            for table_text in tables_by_page.get(page_index, []):
                key = (page_index, current_section)
                paragraph_counter_by_scope[key] = paragraph_counter_by_scope.get(key, 0) + 1
                paragraphs.append(
                    ExtractedParagraph(
                        page_number=page_index,
                        section_title=current_section,
                        paragraph_number=paragraph_counter_by_scope[key],
                        source_type="table",
                        text=table_text,
                    )
                )

    return ParsedPaper(title=title, pages=pages, paragraphs=paragraphs)
