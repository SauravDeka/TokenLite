import os
import html

import streamlit as st

from core.markdown_converter import convert_to_markdown
from core.token_analyzer import analyze_text
from core.document_optimizer import optimize_document


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


def format_file_size(size):
    if size < 1024:
        return f"{size} B"

    if size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"

    return f"{size / (1024 * 1024):.2f} MB"


load_css()


if "uploader_version" not in st.session_state:
    st.session_state["uploader_version"] = 0


st.html(
    """
    <div class="app-shell">

        <header class="site-header">

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

        </header>


        <main class="hero">

            <div class="eyebrow">
                DOCUMENT OPTIMIZATION
            </div>

            <h1>
                Make documents
                <span>LLM-ready.</span>
            </h1>

            <p>
                Reduce unnecessary token usage while
                keeping meaningful document content intact.
            </p>

        </main>

    </div>
    """
)


st.html(
    """
    <div class="upload-section">

        <div class="upload-heading">
            Upload your document
        </div>

        <div class="upload-description">
            Choose a document to analyze and optimize.
        </div>

    </div>
    """
)


uploader_key = (
    f"tokenlite_uploader_"
    f"{st.session_state['uploader_version']}"
)


uploaded_file = st.file_uploader(
    "Upload document",
    type=[
        "pdf",
        "docx",
        "pptx",
        "xlsx",
        "txt",
        "html",
        "htm",
        "csv",
        "json",
        "xml",
    ],
    label_visibility="collapsed",
    key=uploader_key,
)


if uploaded_file:

    st.html(
        """
        <style>
        [data-testid="stFileUploader"] {
            display: none !important;
        }
        </style>
        """
    )


    extension = get_extension(
        uploaded_file.name
    )


    st.html(
        f"""
        <div class="file-card">

            <div class="file-type">
                {html.escape(extension[:4])}
            </div>

            <div class="file-details">

                <div class="file-name">
                    {html.escape(
                        uploaded_file.name
                    )}
                </div>

                <div class="file-meta">
                    {html.escape(extension)}
                    <span>•</span>
                    {format_file_size(
                        uploaded_file.size
                    )}
                </div>

            </div>

            <div class="ready-badge">
                Ready
            </div>

        </div>
        """
    )


    change_spacer, change_col = st.columns(
        [5, 1],
        gap="small",
    )


    with change_col:

        change_document = st.button(
            "Change document",
            use_container_width=True,
            key="change_document",
        )


    if change_document:

        st.session_state[
            "uploader_version"
        ] += 1

        st.rerun()


    optimize_clicked = st.button(
        "⚡ Optimize Document",
        type="primary",
        use_container_width=True,
        key="optimize_button",
    )


    if optimize_clicked:

        with st.spinner(
            "Optimizing your document..."
        ):

            try:

                converted_output = (
                    convert_to_markdown(
                        uploaded_file
                    )
                )


                if (
                    not converted_output
                    or not converted_output.strip()
                ):

                    st.error(
                        "No usable content was found "
                        "in the uploaded document."
                    )

                    st.stop()


                converted_analysis = (
                    analyze_text(
                        converted_output
                    )
                )


                optimization = (
                    optimize_document(
                        converted_output
                    )
                )


                optimized_output = (
                    optimization[
                        "optimized_text"
                    ]
                )


                optimized_analysis = (
                    analyze_text(
                        optimized_output
                    )
                )


                st.session_state[
                    "tokenlite_result"
                ] = {

                    "filename":
                        uploaded_file.name,

                    "document_type":
                        extension.lower(),

                    "converted_output":
                        converted_output,

                    "optimized_output":
                        optimized_output,

                    "converted_analysis":
                        converted_analysis,

                    "optimized_analysis":
                        optimized_analysis,

                    "optimization":
                        optimization,
                }


                st.switch_page(
                    "pages/result.py"
                )


            except Exception as error:

                st.error(
                    f"Processing failed: {error}"
                )


st.html(
    """
    <div class="feature-row">

        <div class="feature">
            <span>✓</span>
            Content-safe cleanup
        </div>

        <div class="feature">
            <span>✓</span>
            Measured token savings
        </div>

        <div class="feature">
            <span>✓</span>
            Meaningful content preserved
        </div>

    </div>
    """
)


st.html(
    """
    <footer class="site-footer">

        <span>
            ⚡ TokenLite
        </span>

        <span>
            Safe document optimization
        </span>

    </footer>
    """
)