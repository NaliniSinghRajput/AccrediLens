import type { Answer } from "@/lib/api";

const SECTION_TITLES = [
  "Evidence Found",
  "Criterion Mapping",
  "Evidence Gaps",
  "Recommended Actions",
  "Proposed Decision",
  "Human Review Status",
] as const;

type AnswerSection = {
  title: string;
  body: string;
};

function parseAnswer(text: string): AnswerSection[] {
  const expression = new RegExp(
    `(${SECTION_TITLES.join("|")})\\s*:?\\s*`,
    "gi"
  );

  const matches = Array.from(text.matchAll(expression));

  if (matches.length === 0) {
    return [{ title: "Answer", body: text.trim() }];
  }

  const sections: AnswerSection[] = [];
  const openingText = text.slice(0, matches[0].index ?? 0).trim();

  if (openingText) {
    sections.push({ title: "Answer", body: openingText });
  }

  matches.forEach((match, index) => {
    const start = (match.index ?? 0) + match[0].length;
    const end =
      index + 1 < matches.length
        ? matches[index + 1].index ?? text.length
        : text.length;

    const matchedTitle = match[1];
    const canonicalTitle =
      SECTION_TITLES.find(
        (title) => title.toLowerCase() === matchedTitle.toLowerCase()
      ) ?? matchedTitle;

    sections.push({
      title: canonicalTitle,
      body: text.slice(start, end).trim(),
    });
  });

  return sections;
}

function formatInline(text: string) {
  const parts = text.split(
    /(\*\*[^*]+\*\*|\[SOURCE\s+\d+(?:\s*,\s*SOURCE\s+\d+)*\])/gi
  );

  return parts.map((part, index) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return <strong key={index}>{part.slice(2, -2)}</strong>;
    }

    if (/^\[SOURCE/i.test(part)) {
      return (
        <span
          key={index}
          style={{
            background: "#e8f0ff",
            borderRadius: 6,
            color: "#174ea6",
            fontSize: "0.85em",
            fontWeight: 700,
            padding: "2px 6px",
          }}
        >
          {part}
        </span>
      );
    }

    return <span key={index}>{part}</span>;
  });
}

function SectionBody({ section }: { section: AnswerSection }) {
  const listSection = [
    "Evidence Found",
    "Evidence Gaps",
    "Recommended Actions",
  ].includes(section.title);

  const normalized = section.body.replace(/\s+-\s+/g, "\n- ");
  const lines = normalized
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean);

  const listItems = lines
    .filter((line) => line.startsWith("-"))
    .map((line) => line.replace(/^-\s*/, ""));

  if (listSection && listItems.length > 0) {
    return (
      <ul style={{ marginBottom: 0, paddingLeft: 22 }}>
        {listItems.map((item, index) => (
          <li key={index} style={{ marginBottom: 8 }}>
            {formatInline(item)}
          </li>
        ))}
      </ul>
    );
  }

  return (
    <p style={{ lineHeight: 1.65, marginBottom: 0, whiteSpace: "pre-wrap" }}>
      {formatInline(section.body)}
    </p>
  );
}

export function AnswerCard({
  answer,
  defaultOpen = false,
}: {
  answer: Answer;
  defaultOpen?: boolean;
}) {
  const sections = parseAnswer(answer.answer);

  const decisionSection = sections.find(
    (section) => section.title === "Proposed Decision"
  );

  const decision =
    decisionSection?.body.match(
      /Supported|Partially Supported|Insufficient Evidence/i
    )?.[0] ?? "";

  const decisionColour = decision.toLowerCase().includes("insufficient")
    ? "#b42318"
    : decision.toLowerCase().includes("partially")
      ? "#b54708"
      : "#067647";

  return (
    <details className="card" open={defaultOpen}>
      <summary
        style={{
          cursor: "pointer",
          listStyle: "none",
          userSelect: "none",
        }}
      >
        <p className="muted" style={{ marginTop: 0 }}>
          {new Date(answer.created_at).toLocaleString()} |{" "}
          {answer.mode.toUpperCase()} | Confidence: {answer.confidence}
        </p>

        <div
          style={{
            alignItems: "center",
            display: "flex",
            gap: 10,
            justifyContent: "space-between",
          }}
        >
          <h2 style={{ margin: 0 }}>
            {answer.mode === "agent"
              ? "Accreditation Analysis"
              : "Answer"}
          </h2>

          {decision && (
            <span
              style={{
                background: `${decisionColour}18`,
                border: `1px solid ${decisionColour}55`,
                borderRadius: 999,
                color: decisionColour,
                fontSize: 13,
                fontWeight: 700,
                padding: "5px 10px",
              }}
            >
              {decision}
            </span>
          )}
        </div>

        <p className="muted" style={{ marginBottom: 0 }}>
          Click to expand or collapse
        </p>
      </summary>

      <div style={{ display: "grid", gap: 18, marginTop: 22 }}>
        {sections.map((section, index) => {
          const isDecision =
            section.title === "Proposed Decision" ||
            section.title === "Human Review Status";

          return (
            <section
              key={`${section.title}-${index}`}
              style={{
                background: isDecision ? "#f8fafc" : "transparent",
                border: isDecision ? "1px solid #e2e8f0" : "none",
                borderRadius: 10,
                padding: isDecision ? 14 : 0,
              }}
            >
              <h3 style={{ marginBottom: 8, marginTop: 0 }}>
                {section.title}
              </h3>
              <SectionBody section={section} />
            </section>
          );
        })}

        {answer.tutor_explanation && (
          <section>
            <h3>Tutor Explanation</h3>
            <p style={{ lineHeight: 1.65, whiteSpace: "pre-wrap" }}>
              {answer.tutor_explanation}
            </p>
          </section>
        )}

        <section>
          <h3>References</h3>

          {answer.sources.length === 0 ? (
            <p className="muted">
              No sufficiently relevant passage was found in the uploaded PDF.
            </p>
          ) : (
            answer.sources.map((source, index) => (
              <div
                className="source"
                key={`${answer.id}-${source.chunk_id}`}
              >
                <strong>
                  Source {index + 1}: Page {source.page_number}, Section:{" "}
                  {source.section_title}, Paragraph{" "}
                  {source.paragraph_start}-{source.paragraph_end}
                </strong>

                <p className="muted">
                  Type: {source.source_type} ? Chunk: {source.chunk_id} ?
                  Score: {source.score}
                </p>

                <pre>{source.text_excerpt}</pre>
              </div>
            ))
          )}
        </section>
      </div>
    </details>
  );
}
