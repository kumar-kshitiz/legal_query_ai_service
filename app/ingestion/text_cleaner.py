import re


def clean_text(text: str) -> str:

    # Normalize Windows/Mac line endings
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Remove spaces/tabs at start and end of lines
    lines = []

    for line in text.split("\n"):
        line = line.strip()
        lines.append(line)

    text = "\n".join(lines)

    # Replace multiple spaces inside a line
    text = re.sub(r"[ \t]+", " ", text)

    # Remove lines containing only page numbers
    text = re.sub(
        r"(?m)^\s*\d+\s*$",
        "",
        text
    )

    # Replace excessive blank lines with maximum 2 line breaks
    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text
    )

    return text.strip()