import os
import re
import tempfile
import unicodedata
from collections import defaultdict

from markitdown import MarkItDown

try:
    import fitz
except ImportError:
    fitz = None


class ConvertedText(str):
    """String-compatible converted output with source-document metadata."""

    def __new__(cls, value, source_artifacts=None, source_page_count=None):
        obj = str.__new__(cls, value or "")
        obj.source_artifacts = source_artifacts or {}
        obj.source_page_count = source_page_count
        return obj


def normalize_source_text(text):
    value = unicodedata.normalize("NFKC", str(text or ""))
    value = value.replace("\u00ad", "")
    value = value.replace("\u200b", "")
    value = value.replace("\ufeff", "")
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def artifact_signature(text):
    value = normalize_source_text(text).lower()

    value = re.sub(
        r"\d{1,4}\s*\|\s*p\s*a\s*g\s*e\b",
        "{PAGE_PIPE}",
        value,
        flags=re.IGNORECASE,
    )

    value = re.sub(
        r"\bpage\s+\d{1,4}\s+of\s+\d{1,4}\b",
        "page {PAGE_OF_TOTAL}",
        value,
        flags=re.IGNORECASE,
    )

    value = re.sub(
        r"\bpage\s*\d{1,4}\b",
        "page {PAGE}",
        value,
        flags=re.IGNORECASE,
    )

    value = re.sub(
        r"\b\d{1,4}\s*/\s*\d{1,4}\b",
        "{PAGE_SLASH_TOTAL}",
        value,
    )

    return value


def build_artifact_regex(text):
    value = normalize_source_text(text)

    value = re.sub(
        r"\d{1,4}\s*\|\s*p\s*a\s*g\s*e\b",
        "{PAGE_PIPE}",
        value,
        flags=re.IGNORECASE,
    )

    value = re.sub(
        r"\bpage\s+\d{1,4}\s+of\s+\d{1,4}\b",
        "page {PAGE_OF_TOTAL}",
        value,
        flags=re.IGNORECASE,
    )

    value = re.sub(
        r"\bpage\s* \d{1,4}\b",
        "page {PAGE}",
        value,
        flags=re.IGNORECASE,
    )

    value = re.sub(
        r"\b\d{1,4}\s*/\s*\d{1,4}\b",
        "{PAGE_SLASH_TOTAL}",
        value,
    )

    parts = re.split(
        r"(\{PAGE_PIPE\}|\{PAGE_OF_TOTAL\}|\{PAGE_SLASH_TOTAL\}|\{PAGE\})",
        value,
    )

    pattern = []

    for part in parts:
        if part == "{PAGE_PIPE}":
            pattern.append(
                r"\d{1,4}\s*\|\s*p\s*a\s*g\s*e"
            )

        elif part == "{PAGE_OF_TOTAL}":
            pattern.append(
                r"\d{1,4}\s+of\s+\d{1,4}"
            )

        elif part == "{PAGE_SLASH_TOTAL}":
            pattern.append(
                r"\d{1,4}\s*/\s*\d{1,4}"
            )

        elif part == "{PAGE}":
            pattern.append(
                r"\d{1,4}"
            )

        elif part:
            literal = re.escape(part)
            literal = literal.replace(
                r"\ ",
                r"\s+",
            )
            pattern.append(literal)

    return re.compile(
        r"(?im)^\s*" + "".join(pattern) + r"\s*$"
    )


def is_page_number_only(text):
    return bool(
        re.fullmatch(
            r"\d{1,4}",
            normalize_source_text(text),
        )
    )


def is_page_marker(text):
    value = normalize_source_text(text)

    patterns = [
        r"page\s+\d{1,4}",
        r"page\s+\d{1,4}\s+of\s+\d{1,4}",
        r"\d{1,4}\s*\|\s*p\s*a\s*g\s*e",
        r"\d{1,4}\s*\|\s*page",
        r"page\s*\d{1,4}\s*/\s*\d{1,4}",
        r"\d{1,4}\s*/\s*\d{1,4}",
    ]

    return any(
        re.fullmatch(
            pattern,
            value,
            re.IGNORECASE,
        )
        for pattern in patterns
    )


def extract_pdf_source_artifacts(path):
    """
    Analyze the original PDF directly.

    Repeated text is considered an artifact only when:
    - it occurs near the same page edge
    - it appears on at least 60% of the pages
    - it is sufficiently long to be meaningful
    - its changing page number can be normalized
    """

    if fitz is None:
        return {}, None

    try:
        document = fitz.open(path)
    except Exception:
        return {}, None

    page_count = len(document)

    candidates = defaultdict(
        lambda: defaultdict(set)
    )

    examples = {}

    try:
        for page_number, page in enumerate(
            document,
            start=1,
        ):
            page_height = float(
                page.rect.height or 1
            )

            blocks = page.get_text(
                "blocks",
                sort=True,
            )

            for block in blocks:
                if len(block) < 5:
                    continue

                x0, y0, x1, y1, block_text = block[:5]

                block_text = str(
                    block_text or ""
                )

                if not block_text.strip():
                    continue

                top_ratio = float(y0) / page_height
                bottom_ratio = float(y1) / page_height

                if bottom_ratio <= 0.20:
                    position = "header"

                elif top_ratio >= 0.80:
                    position = "footer"

                else:
                    continue

                for line in block_text.splitlines():
                    line = normalize_source_text(line)

                    if not line:
                        continue

                    if is_page_number_only(line):
                        continue

                    if len(line) < 15:
                        continue

                    if len(line) > 500:
                        continue

                    signature = artifact_signature(
                        line
                    )

                    candidates[
                        signature
                    ][
                        position
                    ].add(page_number)

                    examples.setdefault(
                        (
                            signature,
                            position,
                        ),
                        line,
                    )

    finally:
        document.close()

    if page_count < 2:
        return {
            "repeated": set(),
            "artifacts": [],
            "page_numbers": set(),
        }, page_count

    required_pages = max(
        3,
        int(
            page_count * 0.60 + 0.999
        ),
    )

    artifacts = []
    repeated_signatures = set()

    for signature, positions in candidates.items():

        for position, pages in positions.items():

            if len(pages) < required_pages:
                continue

            example = examples[
                (
                    signature,
                    position,
                )
            ]

            regex = build_artifact_regex(
                example
            )

            repeated_signatures.add(
                signature
            )

            artifacts.append(
                {
                    "text": example,
                    "normalized": signature,
                    "pattern": regex.pattern,
                    "occurrences": len(pages),
                    "pages": sorted(pages),
                    "type": f"repeated page {position}",
                }
            )

    return {
        "repeated": repeated_signatures,
        "artifacts": artifacts,
        "page_numbers": set(),
    }, page_count


def extract_source_artifacts(
    path,
    extension,
):
    extension = extension.lower().lstrip(".")

    if extension == "pdf":
        return extract_pdf_source_artifacts(
            path
        )

    return {}, None


def convert_document(uploaded_file):
    file_extension = os.path.splitext(
        uploaded_file.name
    )[1].lower()

    document_type = file_extension.lstrip(".")

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=file_extension,
    ) as temp_file:

        temp_file.write(
            uploaded_file.getbuffer()
        )

        temp_path = temp_file.name

    try:
        (
            source_artifacts,
            source_page_count,
        ) = extract_source_artifacts(
            temp_path,
            document_type,
        )

        result = MarkItDown().convert(
            temp_path
        )

        return ConvertedText(
            result.markdown or "",
            source_artifacts=source_artifacts,
            source_page_count=source_page_count,
        )

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def convert_to_markdown(uploaded_file):
    return convert_document(
        uploaded_file
    )