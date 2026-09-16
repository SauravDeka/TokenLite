# TokenLite

**Intelligent Document Optimization for Large Language Models**

TokenLite is a Python-based document optimization application built with Streamlit. It converts documents into clean, AI-friendly text, analyzes token usage, and safely removes document-level artifacts and redundancy while preserving meaningful content.

## Technologies Used

- **Python** – Core programming language used to build the application.
- **Streamlit** – Used to build the web-based user interface.
- **MarkItDown** – Used as the backend document conversion engine.
- **PyMuPDF** – Used for PDF text extraction and document-level artifact detection.
- **Tiktoken** – Used for token counting and token usage analysis.
- **python-docx** – Used for processing Microsoft Word documents.
- **python-pptx** – Used for processing Microsoft PowerPoint presentations.
- **HTML/CSS** – Used for customizing and styling the application interface.
- **Python 3.12** – Python version used for the project environment.
- **uv** – Used for Python environment and package management.

## Features

- Upload supported documents
- Convert documents into clean, AI-friendly text
- Analyze token usage
- Analyze characters, words, lines, and tokens
- Detect repetitive document-level artifacts
- Remove repeated page headers and footers
- Remove unnecessary page markers
- Preserve meaningful document content
- Compare converted and optimized outputs
- Download converted output
- Download optimized converted output
- Verify that meaningful content is preserved

## How It Works

```text
Uploaded Document
       ↓
Document Conversion
       ↓
Token Analysis
       ↓
Safe Artifact Detection
       ↓
Document Optimization
       ↓
Optimized Output
       ↓
Download
