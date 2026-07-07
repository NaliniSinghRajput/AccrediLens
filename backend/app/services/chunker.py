from dataclasses import dataclass

from app.services.pdf_parser import ExtractedParagraph


@dataclass
class PreparedChunk:
    page_number: int
    section_title: str
    paragraph_start: int
    paragraph_end: int
    source_type: str
    text: str
    token_count: int


def approx_tokens(text: str) -> int:
    return max(1, int(len(text.split()) * 1.3))


def make_chunks(
    paragraphs: list[ExtractedParagraph],
    min_tokens: int = 300,
    max_tokens: int = 600,
    overlap_tokens: int = 80,
) -> list[PreparedChunk]:
    chunks: list[PreparedChunk] = []
    buffer: list[ExtractedParagraph] = []
    buffer_tokens = 0
    current_key: tuple[int, str, str] | None = None

    def flush() -> None:
        nonlocal buffer, buffer_tokens
        if not buffer:
            return
        text = "\n\n".join(item.text for item in buffer)
        chunks.append(
            PreparedChunk(
                page_number=buffer[0].page_number,
                section_title=buffer[0].section_title,
                paragraph_start=buffer[0].paragraph_number,
                paragraph_end=buffer[-1].paragraph_number,
                source_type=buffer[0].source_type,
                text=text,
                token_count=approx_tokens(text),
            )
        )
        overlap: list[ExtractedParagraph] = []
        overlap_count = 0
        for item in reversed(buffer):
            item_tokens = approx_tokens(item.text)
            if overlap_count + item_tokens > overlap_tokens:
                break
            overlap.insert(0, item)
            overlap_count += item_tokens
        buffer = overlap
        buffer_tokens = overlap_count

    for para in paragraphs:
        if para.source_type == "references":
            continue
        para_tokens = approx_tokens(para.text)
        key = (para.page_number, para.section_title, para.source_type)

        if para.source_type in {"table", "figure caption", "abstract"}:
            flush()
            chunks.append(
                PreparedChunk(
                    page_number=para.page_number,
                    section_title=para.section_title,
                    paragraph_start=para.paragraph_number,
                    paragraph_end=para.paragraph_number,
                    source_type=para.source_type,
                    text=para.text,
                    token_count=para_tokens,
                )
            )
            current_key = None
            buffer = []
            buffer_tokens = 0
            continue

        if current_key and current_key != key:
            flush()
            buffer = []
            buffer_tokens = 0

        current_key = key
        if buffer and buffer_tokens + para_tokens > max_tokens:
            flush()

        buffer.append(para)
        buffer_tokens += para_tokens

        if buffer_tokens >= min_tokens:
            flush()

    if buffer:
        text = "\n\n".join(item.text for item in buffer)
        chunks.append(
            PreparedChunk(
                page_number=buffer[0].page_number,
                section_title=buffer[0].section_title,
                paragraph_start=buffer[0].paragraph_number,
                paragraph_end=buffer[-1].paragraph_number,
                source_type=buffer[0].source_type,
                text=text,
                token_count=approx_tokens(text),
            )
        )

    return chunks
