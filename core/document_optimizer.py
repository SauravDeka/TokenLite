import re
import unicodedata


PAGE_MARKER_PATTERNS = [
    re.compile(
        r"^\s*page\s+\d{1,4}\s*$",
        re.IGNORECASE,
    ),
    re.compile(
        r"^\s*page\s+\d{1,4}\s+of\s+\d{1,4}\s*$",
        re.IGNORECASE,
    ),
    re.compile(
        r"^\s*page\s+\d{1,4}\s*/\s*\d{1,4}\s*$",
        re.IGNORECASE,
    ),
    re.compile(
        r"^\s*\d{1,4}\s*\|\s*p\s*a\s*g\s*e\s*$",
        re.IGNORECASE,
    ),
    re.compile(
        r"^\s*\d{1,4}\s*\|\s*page\s*$",
        re.IGNORECASE,
    ),
    re.compile(
        r"^\s*\d{1,4}\s*/\s*\d{1,4}\s*$",
        re.IGNORECASE,
    ),
]


PROTECTED_LABELS = {
    "objective",
    "objectives",
    "prerequisite",
    "prerequisites",
    "course outcome",
    "course outcomes",
    "detailed syllabus",
    "reference book",
    "reference books",
    "textbook",
    "textbooks",
    "contents",
    "introduction",
    "methodology",
    "annexure",
    "appendix",
    "conclusion",
}


def normalize_text(text):
    value = unicodedata.normalize(
        "NFKC",
        str(text or ""),
    )

    value = value.replace(
        "\u00ad",
        "",
    )

    value = value.replace(
        "\u200b",
        "",
    )

    value = value.replace(
        "\ufeff",
        "",
    )

    value = value.replace(
        "\r\n",
        "\n",
    )

    value = value.replace(
        "\r",
        "\n",
    )

    return value


def normalize_line(line):
    value = normalize_text(
        line
    )

    value = re.sub(
        r"\s+",
        " ",
        value,
    )

    return value.strip().lower()


def is_page_marker(line):
    value = str(line or "").strip()

    return any(
        pattern.fullmatch(value)
        for pattern in PAGE_MARKER_PATTERNS
    )


def is_standalone_number(line):
    return bool(
        re.fullmatch(
            r"\d{1,4}",
            str(line or "").strip(),
        )
    )


def is_protected_content(line):
    value = normalize_line(
        line
    )

    if not value:
        return True

    if value.endswith(":"):
        return True

    if value in PROTECTED_LABELS:
        return True

    if value.startswith("|"):
        return True

    if re.match(
        r"^[-*+]\s+",
        value,
    ):
        return True

    return False


def collect_source_artifacts(text):
    metadata = getattr(
        text,
        "source_artifacts",
        None,
    )

    if not isinstance(
        metadata,
        dict,
    ):
        return [], set()

    return (
        list(
            metadata.get(
                "artifacts",
                [],
            )
        ),
        set(
            metadata.get(
                "page_numbers",
                set(),
            )
        ),
    )


def remove_source_artifacts(
    text,
    artifacts,
):
    optimized = text
    removed = []

    for artifact in artifacts:

        pattern_text = artifact.get(
            "pattern"
        )

        if not pattern_text:
            continue

        try:
            pattern = re.compile(
                pattern_text,
                re.IGNORECASE
                | re.MULTILINE,
            )
        except re.error:
            continue

        matches = list(
            pattern.finditer(
                optimized
            )
        )

        if not matches:
            continue

        # An artifact must occur multiple times in
        # the converted output before it can be removed.
        if len(matches) < 3:
            continue

        optimized, count = pattern.subn(
            "",
            optimized,
        )

        if count:
            removed.append(
                {
                    **artifact,
                    "occurrences": count,
                }
            )

    return optimized, removed


def remove_explicit_page_markers(
    lines
):
    result = []
    removed = []

    for line in lines:

        if is_page_marker(line):
            removed.append(
                line.strip()
            )

        else:
            result.append(
                line
            )

    return result, removed


def detect_page_number_sequence(
    lines,
    page_count,
):
    if not page_count or page_count < 3:
        return set()

    candidates = []

    for index, line in enumerate(
        lines
    ):

        if is_standalone_number(
            line
        ):

            candidates.append(
                (
                    index,
                    int(
                        str(line).strip()
                    ),
                )
            )

    if not candidates:
        return set()

    targets = [
        list(
            range(
                1,
                page_count + 1,
            )
        ),
        list(
            range(
                1,
                page_count,
            )
        ),
    ]

    best = []

    for target in targets:

        position = 0
        indexes = []

        for index, number in candidates:

            if position >= len(target):
                break

            if number == target[position]:

                indexes.append(
                    index
                )

                position += 1

        if position == len(target):
            return set(indexes)

        if len(indexes) > len(best):
            best = indexes

    minimum = max(
        5,
        int(
            page_count * 0.60
            + 0.999
        ),
    )

    if len(best) >= minimum:
        return set(best)

    return set()


def collapse_blank_lines(
    lines
):
    result = []
    blank = False

    for line in lines:

        if str(line).strip():

            result.append(
                str(line).rstrip()
            )

            blank = False

        elif not blank:

            result.append(
                ""
            )

            blank = True

    while (
        result
        and not result[0].strip()
    ):
        result.pop(0)

    while (
        result
        and not result[-1].strip()
    ):
        result.pop()

    return result


def optimize_document(text):
    original_text = normalize_text(
        text
    )

    if not original_text.strip():
        return {
            "original_text": original_text,
            "optimized_text": original_text,
            "removed_items": [],
            "removed_artifacts": [],
            "removed_artifact_count": 0,
            "content_preserved": True,
            "changed": False,
        }

    (
        source_artifacts,
        source_page_numbers,
    ) = collect_source_artifacts(
        text
    )

    page_count = getattr(
        text,
        "source_page_count",
        None,
    )

    optimized_text, removed_artifacts = (
        remove_source_artifacts(
            original_text,
            source_artifacts,
        )
    )

    lines = optimized_text.split(
        "\n"
    )

    (
        lines,
        removed_page_markers,
    ) = remove_explicit_page_markers(
        lines
    )

    page_number_indexes = (
        detect_page_number_sequence(
            lines,
            page_count,
        )
    )

    if page_number_indexes:

        filtered = []

        for index, line in enumerate(
            lines
        ):

            if index in page_number_indexes:
                continue

            filtered.append(
                line
            )

        lines = filtered

    lines = collapse_blank_lines(
        lines
    )

    optimized_text = "\n".join(
        lines
    ).strip()

    removed_items = list(
        removed_artifacts
    )

    if removed_page_markers:

        removed_items.append(
            {
                "text": "Explicit PDF page markers",
                "type": "page marker",
                "occurrences": len(
                    removed_page_markers
                ),
                "pages": [],
            }
        )

    if page_number_indexes:

        removed_items.append(
            {
                "text": "Sequential PDF page numbers",
                "type": "page number",
                "occurrences": len(
                    page_number_indexes
                ),
                "pages": [],
            }
        )

    removed_count = sum(
        int(
            item.get(
                "occurrences",
                1,
            )
        )
        for item in removed_items
    )

    return {
        "original_text": original_text,
        "optimized_text": optimized_text,
        "removed_items": removed_items,
        "removed_artifacts": removed_items,
        "removed_artifact_count": removed_count,
        "content_preserved": True,
        "changed": (
            optimized_text
            != original_text
        ),
    }