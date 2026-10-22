import argparse
from pathlib import Path

import pymupdf4llm


def convert_pdf(pdf_path: str | Path) -> str:
    """Convert a PDF file to Markdown text."""
    source = Path(pdf_path)
    if not source.is_file():
        raise FileNotFoundError(f"PDF file not found: {source}")
    if source.suffix.lower() != ".pdf":
        raise ValueError("The input file must have a .pdf extension.")

    with source.open("rb") as pdf_file:
        if b"%PDF-" not in pdf_file.read(1024):
            raise ValueError("The input file does not appear to be a valid PDF.")

    return pymupdf4llm.to_markdown(str(source))


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert a PDF file to Markdown.")
    parser.add_argument("pdf", type=Path, help="Path to the PDF file to convert")
    args = parser.parse_args()

    markdown = convert_pdf(args.pdf)
    output_path = args.pdf.with_suffix(".md")
    output_path.write_text(markdown, encoding="utf-8")
    print(f"Conversion completed: {output_path}")
    print(f"Markdown size: {len(markdown):,} characters")


if __name__ == "__main__":
    main()
