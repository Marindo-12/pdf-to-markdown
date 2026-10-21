from pathlib import Path
import pymupdf4llm

# Change this to your PDF filename
pdf_path = Path("AI_Engineering_Learning_Plan.pdf")

if not pdf_path.is_file():
    raise FileNotFoundError(f"PDF not found: {pdf_path}")

# Extract PDF content with layout-aware Markdown conversion
markdown = pymupdf4llm.to_markdown(str(pdf_path))

# Save the result next to the PDF
output_path = pdf_path.with_suffix(".md")
output_path.write_text(markdown, encoding="utf-8")

print(f"Conversion completed: {output_path}")
print(f"Markdown size: {len(markdown):,} characters")
