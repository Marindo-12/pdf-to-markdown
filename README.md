<p align="center">
  <img src="assets/pdf-to-md-banner.png" alt="PDF to Markdown Converter" width="100%" />
</p>


# PDF to Markdown Converter

A local Python utility for converting PDF documents into Markdown (`.md`) files. The goal is to extract document content into a readable, editable format suitable for documentation, note-taking, GitHub repositories, and AI-assisted workflows.

## Features

- **Local conversion:** Process documents on your computer without requiring an online conversion service.
- **Markdown output:** Convert PDF content into `.md` files.
- **Layout-aware extraction:** Use PyMuPDF4LLM-compatible functionality to improve reading order, headings, and table extraction.
- **UTF-8 encoding:** Support international characters and multilingual documents.
- **Automatic output naming:** Generate a Markdown file with the same base name as the source PDF.
- **Virtual environment:** Isolate Python dependencies from other projects.
- **Privacy-conscious workflow:** Avoid external AI services and cloud uploads during standard local conversion.

> **Note:** Conversion quality depends on the PDF structure. Complex tables, mathematical equations, multi-column layouts, and scanned pages may require additional processing or manual corrections.

## Technologies

- Python 3
- PyMuPDF
- PyMuPDF4LLM-compatible Markdown extraction
- PowerShell on Windows
- Git and GitHub for version control

## Project Structure

After setup, the project should look like this:

```text
pdf-to-markdown/
├── .venv/                  # Python virtual environment
├── convert_pdf.py          # PDF conversion script
├── cours.pdf               # Example input PDF
├── cours.md                # Generated Markdown output
├── .gitignore              # Files excluded from Git
└── README.md               # Project documentation
```

The example PDF and generated Markdown file are illustrative. Use your own filenames when running the converter.

## Prerequisites

Before starting, install:

- [Python](https://www.python.org/downloads/) — a version compatible with the installed PyMuPDF release.
- [Git](https://git-scm.com/downloads/) — optional, for version control.
- [Visual Studio Code](https://code.visualstudio.com/) — optional, for editing Python and Markdown files.

On Windows, verify Python is available:

```powershell
py --version
python --version
```

If neither command works, install Python and enable the option to add Python to PATH.

## Installation

### 1. Open the project directory

Open PowerShell and navigate to the project folder:

```powershell
cd C:\Users\hp\pdf-to-markdown
```

If you are creating the project from scratch:

```powershell
mkdir pdf-to-markdown
cd pdf-to-markdown
```

### 2. Create a virtual environment

```powershell
py -m venv .venv
```

This creates an isolated environment for project dependencies.

### 3. Activate the environment

```powershell
.\.venv\Scripts\Activate.ps1
```

Your terminal should display `(.venv)` at the beginning of the prompt.

If PowerShell prevents activation, you can run Python directly through the environment:

```powershell
.\.venv\Scripts\python.exe --version
```

### 4. Install the dependencies

Install the PDF processing library:

```powershell
python -m pip install --upgrade pip
python -m pip install --upgrade pymupdf
```

PyMuPDF provides PDF processing functionality. The Markdown extraction API may vary by installed release, so verify that the required module is available before running the script.

For versions that expose the `pymupdf4llm` module, test it with:

```powershell
python -c "import pymupdf4llm; print('Markdown extraction is available')"
```

If the module is unavailable, consult the [official PyMuPDF4LLM repository](https://github.com/pymupdf/pymupdf4llm) and [PyMuPDF documentation](https://pymupdf.readthedocs.io/) for the installation instructions corresponding to your installed version.

## Usage

### 1. Add your PDF

Copy the document into the project directory.

For example:

```text
pdf-to-markdown/
└── cours.pdf
```

### 2. Create the conversion script

Create a file named `convert_pdf.py` and add:

```python
from pathlib import Path
import pymupdf4llm


def convert_pdf(pdf_filename: str) -> Path:
    """Convert a PDF file into a Markdown document."""

    pdf_path = Path(pdf_filename)

    if not pdf_path.is_file():
        raise FileNotFoundError(
            f"PDF file not found: {pdf_path.resolve()}"
        )

    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError("The input file must have a .pdf extension.")

    # Extract PDF content into Markdown.
    markdown = pymupdf4llm.to_markdown(str(pdf_path))

    # Save the Markdown beside the original PDF.
    output_path = pdf_path.with_suffix(".md")
    output_path.write_text(markdown, encoding="utf-8")

    return output_path


if __name__ == "__main__":
    try:
        output_file = convert_pdf("cours.pdf")
        print(f"Conversion completed: {output_file.resolve()}")
        print(f"Output size: {output_file.stat().st_size:,} bytes")

    except (FileNotFoundError, ValueError) as error:
        print(f"Error: {error}")

    except Exception as error:
        print(f"Conversion failed: {error}")
        raise
```

**Important:** This example requires an installed version that supports `import pymupdf4llm` and `pymupdf4llm.to_markdown()`. If your installed release exposes a different API, follow the official documentation for that release rather than assuming the import will work.

### 3. Set your input filename

In the script, replace:

```python
output_file = convert_pdf("cours.pdf")
```

with your actual PDF filename, for example:

```python
output_file = convert_pdf("machine-learning.pdf")
```

Keep the PDF in the current working directory, or provide its full path.

### 4. Run the conversion

In PowerShell:

```powershell
python convert_pdf.py
```

If the environment is not activated, run:

```powershell
.\.venv\Scripts\python.exe convert_pdf.py
```

When conversion succeeds, the output will be saved next to the input PDF.

For example:

```text
machine-learning.pdf
machine-learning.md
```

### 5. Open the Markdown output

Open the generated file in VS Code:

```powershell
code machine-learning.md
```

Review the headings, paragraphs, lists, tables, equations, and special characters. Correct any formatting that was not preserved accurately.

## How It Works

The conversion process follows four steps:

1. **Input:** The program checks that the specified PDF exists.
2. **Extraction:** The PDF processing library extracts document content and reconstructs its logical reading order.
3. **Markdown generation:** The extracted content is represented using Markdown syntax.
4. **Output:** The generated text is written to a UTF-8 `.md` file.

The original PDF remains unchanged.

## Troubleshooting

### `ModuleNotFoundError`

Example:

```text
ModuleNotFoundError: No module named 'pymupdf4llm'
```

Check the active Python interpreter:

```powershell
python -c "import sys; print(sys.executable)"
python -m pip show pymupdf
python -m pip show pymupdf4llm
```

Make sure the packages are installed in the same virtual environment that runs the script. Package names and import names are not always identical, and the required API can change between releases.

### PDF file not found

Verify the current directory:

```powershell
Get-Location
Get-ChildItem -Filter *.pdf
```

Ensure the filename in the script exactly matches the PDF's name.

### Poor Markdown formatting

If headings, lists, tables, or columns are incorrect:

- Try the current Markdown extraction functionality documented by PyMuPDF4LLM.
- Inspect the PDF's text selection and reading order.
- Use OCR when the document consists of scanned page images.
- Consider [Docling](https://github.com/docling-project/docling) for documents requiring more advanced layout reconstruction.
- Manually correct complex equations, tables, and diagrams.

### PowerShell activation is blocked

If activation is blocked by the local execution policy, use the environment's Python executable directly:

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade pymupdf
.\.venv\Scripts\python.exe convert_pdf.py
```

This avoids the need to change the PowerShell execution policy.

## Security and Privacy

- Install packages from official project repositories and trusted package sources.
- Keep Python dependencies updated.
- Use a virtual environment to isolate dependencies.
- Treat untrusted PDFs as potentially malicious input.
- Avoid running unknown scripts or installing unnecessary packages.
- The basic conversion workflow can run locally without uploading the document to an AI service. Optional external integrations may have different privacy implications.

No software can guarantee complete protection against all vulnerabilities. For sensitive documents, use trusted dependencies and a suitably isolated environment.

## Git Configuration

If you do not want to commit PDFs and generated Markdown files, add the following rules to `.gitignore`:

```gitignore
# Python virtual environment
.venv/

# Python cache
__pycache__/
*.py[cod]

# PDF input files
*.pdf

# Generated Markdown files
*.md

# Keep the main project documentation
!README.md
```

**Note:** These rules ignore all Markdown files except `README.md`. If you want to track other Markdown documentation, use a narrower rule, such as ignoring only generated files in a dedicated output directory.

Files already tracked by Git are not automatically untracked when `.gitignore` changes.

## References

- [PyMuPDF4LLM — GitHub](https://github.com/pymupdf4llm/pymupdf4llm)
- [PyMuPDF — Documentation](https://pymupdf.readthedocs.io/)
- [Docling — GitHub](https://github.com/docling-project/docling)
- [Python — Official Website](https://www.python.org/)

## License

This project is a local utility script. Choose and add a license file if you intend to distribute it publicly. The licenses of the dependencies are separate from the license you select for your own code.
