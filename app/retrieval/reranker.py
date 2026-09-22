import re


STOP_WORDS = {
    "what",
    "is",
    "the",
    "for",
    "a",
    "an",
    "of",
    "in",
    "to",
    "law",
    "does",
    "say",
    "about"
}


def get_keywords(query: str) -> set[str]:

    words = re.findall(
        r"[a-zA-Z]+",
        query.lower()
    )

    return {
        w
        for w in words
        if w not in STOP_WORDS
    }


def get_heading(text: str) -> str:

    # Example:
    # 303. Theft.—Whoever...
    #
    # Returns:
    # theft

    text = text.lower().strip()

    text = re.sub(
        r"^\d+[a-zA-Z]?\.\s*",
        "",
        text
    )

    # Split heading from actual provision
    parts = re.split(
        r"—|––|--",
        text,
        maxsplit=1
    )

    return parts[0].strip()


def rerank_results(
    query: str,
    results: list
):

    keywords = get_keywords(query)

    ranked = []


    for result in results:

        text = result.payload.get(
            "text",
            ""
        )

        heading = get_heading(text)

        lexical_score = 0.0


        for word in keywords:

            # Strong boost for exact heading
            if heading == word:
                lexical_score += 0.20

            # Smaller boost if term occurs
            # somewhere in heading
            elif word in heading:
                lexical_score += 0.10


        final_score = (
            result.score
            +
            lexical_score
        )


        ranked.append(
            (
                final_score,
                result
            )
        )


    ranked.sort(
        key=lambda x: x[0],
        reverse=True
    )


    unique_results = []
    seen_sections = set()

    for score, result in ranked:

        section = str(
            result.payload.get("section")
        )

        if section in seen_sections:
            continue

        seen_sections.add(section)
        unique_results.append(result)


    return unique_results