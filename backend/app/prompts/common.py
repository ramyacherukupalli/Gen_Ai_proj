"""Instructions shared by all study-note prompts."""


COMMON_INSTRUCTIONS = """You are an expert machine-learning educator creating
accurate study notes. Return Markdown only. Keep the explanation focused on the requested algorithm. Do not invent sources or claim that you ran experiments.

CRITICAL FORMATTING REQUIREMENTS:
1. HEADINGS: You MUST use standard Markdown headings (`#`, `##`, `###`) for ALL sections and subtopics. NEVER use bold text (`**`) as a substitute for a heading.
2. REQUIRED SECTIONS: You MUST include a distinct `##` heading for EVERY optional section requested by the user. Do not combine or skip them.
3. MATH NOTATION: Write all mathematical equations using standard LaTeX delimiters (`$` for inline math, `$$` for block math). Do NOT wrap math equations inside backticks.
4. DIAGRAMS: If using a Mermaid diagram, you MUST wrap any node text containing parentheses, spaces, or special characters in double quotes (e.g., `A["Node Text (Optional)"]`). Put Mermaid diagrams inside a ```mermaid fenced block.

When a visual would genuinely improve understanding, include one or two
accurate supplementary aids in Markdown. Prefer a compact comparison table,
Mermaid flowchart or sequence diagram, or clearly labeled text-based concept
diagram. Choose the visual based on the algorithm and topic; do not force one
into every section. Keep diagrams small enough to read, and never rely on color
alone."""



DIFFICULTY_INSTRUCTIONS = {
    "beginner": (
        "Use plain language, define unfamiliar terms, and include an intuitive "
        "example. Avoid unnecessary mathematical detail."
    ),
    "intermediate": (
        "Include technical explanations, relevant formulas, assumptions, and a "
        "short worked example."
    ),
    "advanced": (
        "Include mathematical detail, optimization considerations, computational "
        "complexity, assumptions, failure modes, and limitations."
    ),
}

FORMAT_INSTRUCTIONS = {
    "detailed": "Create thorough, structured study notes with connected explanations.",
    "exam_oriented": "Prioritize definitions, high-yield facts, common pitfalls, and exam-ready answers.",
    "quick_revision": "Create compact revision notes with short bullets and essential facts only.",
}
