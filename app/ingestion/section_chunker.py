import re


def get_act_body(text: str) -> str:
    marker = "BE it enacted by Parliament"

    pos = text.find(marker)

    if pos == -1:
        raise ValueError(
            "Could not detect beginning of Act body."
        )

    return text[pos:]


def extract_sections(text: str) -> list[dict]:

    text = get_act_body(text)

    lines = text.split("\n")

    sections = []

    current_section = None
    current_chapter = None

    # For BNS sections 1, 2, 3 ... 358
    expected_section = 1

    section_pattern = re.compile(
        r"^(\d{1,3})\.\s*(.*)"
    )

    chapter_pattern = re.compile(
        r"^CHAPTER\s+([IVXLCDM]+)$",
        re.IGNORECASE
    )

    for line in lines:

        line = line.strip()

        if not line:
            continue

        # Detect chapter
        chapter_match = chapter_pattern.match(line)

        if chapter_match:
            current_chapter = line.upper()
            continue

        section_match = section_pattern.match(line)

        if section_match:

            section_number = int(
                section_match.group(1)
            )

            # Accept only the section number
            # that should logically come next.
            if section_number == expected_section:

                # Save previous section
                if current_section:

                    current_section["text"] = "\n".join(
                        current_section["content"]
                    ).strip()

                    del current_section["content"]

                    sections.append(
                        current_section
                    )

                first_line = section_match.group(2)

                current_section = {
                    "section": str(section_number),
                    "chapter": current_chapter,
                    "content": [
                        f"{section_number}. {first_line}"
                    ]
                }

                expected_section += 1

                continue

        # Everything else belongs to
        # the current section.
        if current_section:
            current_section["content"].append(
                line
            )

    # Save final section
    if current_section:

        current_section["text"] = "\n".join(
            current_section["content"]
        ).strip()

        del current_section["content"]

        sections.append(
            current_section
        )

    return sections