import os
import html

import streamlit as st


st.set_page_config(
    page_title="TokenLite",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def load_css():
    css_path = os.path.join(
        "assets",
        "style.css",
    )

    if os.path.exists(css_path):
        with open(
            css_path,
            "r",
            encoding="utf-8",
        ) as file:
            st.html(
                f"<style>{file.read()}</style>"
            )


def get_extension(filename):
    extension = os.path.splitext(
        filename
    )[1].replace(
        ".",
        "",
    ).upper()

    return extension or "FILE"


def normalize_removed_items(items):

    if not items:
        return []

    labels = []

    for item in items:

        if isinstance(item, dict):

            label = (
                item.get("label")
                or item.get("type")
                or item.get("category")
                or item.get("reason")
                or item.get("text")
                or ""
            )

        else:
            label = str(item)

        label = str(label).strip()

        if not label:
            continue

        if label not in labels:
            labels.append(label)

    return labels


def shorten_label(text, max_length=90):

    text = " ".join(
        str(text).split()
    )

    if len(text) <= max_length:
        return text

    return (
        text[:max_length - 3].rstrip()
        + "..."
    )


load_css()


result = st.session_state.get(
    "tokenlite_result"
)


if not result:

    st.html(
        """
        <div class="empty-result">

            <div class="empty-icon">
                ⚡
            </div>

            <h1>
                No document available
            </h1>

            <p>
                Upload and optimize a document
                to view the results.
            </p>

        </div>
        """
    )

    if st.button(
        "← Upload a document",
        type="primary",
        use_container_width=True,
    ):
        st.switch_page(
            "app.py"
        )

    st.stop()


filename = result.get(
    "filename",
    "Document",
)

converted_output = result.get(
    "converted_output",
    "",
)

optimized_output = result.get(
    "optimized_output",
    "",
)

converted_analysis = result.get(
    "converted_analysis",
    {},
)

optimized_analysis = result.get(
    "optimized_analysis",
    {},
)

optimization = result.get(
    "optimization",
    {},
)

removed_items = normalize_removed_items(
    optimization.get(
        "removed_items",
        [],
    )
)

content_preserved = optimization.get(
    "content_preserved",
    False,
)


converted_tokens = converted_analysis.get(
    "tokens",
    0,
)

optimized_tokens = optimized_analysis.get(
    "tokens",
    0,
)


extension = get_extension(
    filename
)


if removed_items:

    visible_items = [
        shorten_label(item)
        for item in removed_items[:4]
    ]

    cleaned_summary = " • ".join(
        visible_items
    )

    if len(removed_items) > 4:
        cleaned_summary += (
            f" • +{len(removed_items) - 4} more"
        )

else:

    cleaned_summary = (
        "No removable document-level "
        "artifacts were detected."
    )


st.html(
    """
    <div class="site-header">

        <div class="brand">

            <div class="brand-icon">
                ⚡
            </div>

            <div>

                <div class="brand-name">
                    TokenLite
                </div>

                <div class="brand-tagline">
                    Intelligent document optimization
                </div>

            </div>

        </div>

    </div>
    """
)


st.html(
    """
    <div class="result-title compact-result-title">

        <div class="eyebrow">
            OPTIMIZATION COMPLETE
        </div>

        <h1>
            Your document is
            <span>ready.</span>
        </h1>


    </div>
    """
)


st.html(
    f"""
    <div class="result-file-card compact-file-card">

        <div class="result-file-icon">
            {html.escape(extension[:4])}
        </div>

        <div class="result-file-details">

            <div class="result-file-name">
                {html.escape(filename)}
            </div>

            <div class="result-file-meta">
                {html.escape(extension)}
                <span>•</span>
                Document processed successfully
            </div>

        </div>

        <div class="complete-badge">
            Complete
        </div>

    </div>
    """
)


st.html(
    """
    <div class="section-label compact-section-label">
        OUTPUTS
    </div>

    <div class="output-intro compact-intro">
        TokenLite provides two versions of your document
        so you can choose what you need.
    </div>
    """
)


converted_col, optimized_col = st.columns(
    2,
    gap="large",
)


with converted_col:

    st.html(
        f"""
        <div class="download-card compact-output-card converted-card">

            <div class="download-icon">
                📄
            </div>

            <div class="download-content">

                <div class="download-title">
                    Converted Output
                </div>

                <div class="download-description">
                    Your document converted into clean,
                    usable text.
                </div>

                <div class="output-token-info">
                    {converted_tokens:,} tokens
                </div>

            </div>

        </div>
        """
    )

    st.download_button(
        "↓  Download Converted Output",
        data=converted_output,
        file_name=(
            f"{os.path.splitext(filename)[0]}"
            "_converted.txt"
        ),
        mime="text/plain",
        use_container_width=True,
        key="download_converted",
    )


with optimized_col:

    st.html(
        f"""
        <div class="download-card optimized-download compact-output-card optimized-card">

            <div class="download-icon">
                ⚡
            </div>

            <div class="download-content">

                <div class="download-title">
                    Optimized Converted Output
                </div>

                <div class="download-description">
                    The converted text after safe
                    document-level artifact cleanup.
                </div>

                <div class="output-token-info">
                    {optimized_tokens:,} tokens
                </div>

                <div class="cleaned-section">

                    <div class="cleaned-label">
                        Cleaned
                    </div>

                    <div class="cleaned-items">
                        {html.escape(cleaned_summary)}
                    </div>

                </div>

            </div>

        </div>
        """
    )

    st.download_button(
        "↓  Download Optimized Converted Output",
        data=optimized_output,
        file_name=(
            f"{os.path.splitext(filename)[0]}"
            "_optimized.txt"
        ),
        mime="text/plain",
        use_container_width=True,
        key="download_optimized",
    )


if content_preserved:

    st.html(
        """
        <div class="success-message compact-success">

            <div class="success-icon">
                ✓
            </div>

            <div>

                <strong>
                    Meaningful content preserved
                </strong>

                <span>
                    Safe document-level cleanup was applied
                    without removing meaningful information.
                </span>

            </div>

        </div>
        """
    )

else:

    st.html(
        """
        <div class="warning-message compact-success">

            <div class="warning-icon">
                !
            </div>

            <div>

                <strong>
                    Review the optimized output
                </strong>

                <span>
                    The optimizer could not confirm complete
                    content preservation automatically.
                </span>

            </div>

        </div>
        """
    )


st.html(
    """
    <div class="section-label compact-preview-label">
        REVIEW OUTPUT
    </div>

    """
)


with st.expander(
    "View converted document"
):

    converted_tab, optimized_tab = st.tabs(
        [
            "Converted Output",
            "Optimized Converted Output",
        ]
    )

    with converted_tab:

        st.text_area(
            "Converted document",
            value=converted_output,
            height=420,
            disabled=True,
            label_visibility="collapsed",
        )

    with optimized_tab:

        st.text_area(
            "Optimized converted document",
            value=optimized_output,
            height=420,
            disabled=True,
            label_visibility="collapsed",
        )


if st.button(
    "← Process another document",
    use_container_width=True,
    key="process_another",
):

    st.session_state.pop(
        "tokenlite_result",
        None,
    )

    st.switch_page(
        "app.py"
    )


st.html(
    """
    <footer class="site-footer result-footer compact-footer">

        <span>
            ⚡ TokenLite
        </span>

        <span>
            Safe document optimization
        </span>

    </footer>
    """
)