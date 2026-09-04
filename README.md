# Nepali PDF Text Extractor (DOCX Edition)

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Docker Ready](https://img.shields.io/badge/docker-ready-2496ED.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey.svg)](#)

A high-accuracy tool to extract Nepali (Devanagari) text from PDF documents and export directly to clean **DOCX** files formatted in the **Mangal** font.

Designed to reliably handle complex mixed-script documents, legacy font encodings (such as Preeti/Kantipur), low-quality scans, and massive multi-thousand-page PDFs.

---

## 🔍 How It Works

The extraction pipeline follows a resilient multi-stage fallback strategy:

```
                      [ Input PDF ]
                            │
              Font Unicode Mapping Inspection
                            │
               ┌────────────┴────────────┐
         [ Mapping OK ]            [ Missing ]
               │                         │
      Stage 1: Poppler (pdftotext)       │
               │                         │
         Passed Validation?              │
          ├── YES ──> [ Unicode Normalization (NFC) ]
          └── NO                         │
               │                         │
      Stage 2: PDFMiner.six              │
               │                         │
         Passed Validation?              │
          ├── YES ──> [ Unicode Normalization (NFC) ]
          └── NO                         │
               └────────────┬────────────┘
                            │
      Stage 3: OCRmyPDF (Tesseract nep + hin + eng)
               (Deskew + DPI optimization + unpaper)
                            │
                  Re-extract via Poppler
                            │
              [ Unicode Normalization (NFC) ]
                            │
             [ Export to Word DOCX (Mangal) ]
```

1. **Direct Extraction (Poppler)**: Fast, layout-preserving extraction via `pdftotext`.
2. **Font Fallback (PDFMiner)**: Alternative text-stream parser executed in an isolated process with strict timeouts to prevent hangs.
3. **OCR Fallback (OCRmyPDF / Tesseract)**: Triggers automatically for scanned pages or garbled fonts, combining Nepali, Hindi, and English OCR models with image deskewing.
4. **ASCII & Legacy Font Preservation**: Retains clean copyable ASCII layers as-is, preserving text formatted in legacy fonts for subsequent conversion.
5. **Heuristic Quality Scoring**: Validates Devanagari character ratios, filters junk glyphs, and detects bad font-mapping artifacts before accepting extracted text.
6. **Word DOCX Generation**: Automatically structures paragraphs, collapses blank lines into paragraph spacing, and formats runs using the Devanagari-standard **Mangal** font.

---

## 🚀 Quick Start (Docker - Recommended)

Docker is the simplest way to run the extractor without manually compiling Tesseract or Poppler language packages.

### 1. Build the Docker Image

```bash
docker build -t nepali-pdf-text .
```

### 2. Process a Folder of PDFs

Process all PDFs inside your local `pdf/` directory and write `.docx` outputs to `out-batch/`:

**PowerShell (Windows):**
```powershell
docker run --rm -v "${PWD}:/work" nepali-pdf-text --input-dir /work/pdf --output-dir /work/out-batch
```

**Bash (Linux / macOS):**
```bash
docker run --rm -v "$(pwd):/work" nepali-pdf-text --input-dir /work/pdf --output-dir /work/out-batch
```

### 3. Process a Single PDF File

**PowerShell (Windows):**
```powershell
docker run --rm -v "${PWD}:/work" nepali-pdf-text /work/document.pdf --output /work/document.docx
```

**Bash (Linux / macOS):**
```bash
docker run --rm -v "$(pwd):/work" nepali-pdf-text /work/document.pdf --output /work/document.docx
```

---

## ⚙️ Configuration & Environment Variables

You can configure default timeouts, parallel workers, and OCR parameters via environment variables or a `.env` file.

### Setting Up `.env`

Copy the template file:

```bash
cp .env.example .env
```

Edit `.env` to suit your requirements:

```env
# Concurrency
WORKERS=4

# Timeouts in seconds (useful for large PDFs)
PDFFONTS_TIMEOUT=120
PDFTOTEXT_TIMEOUT=900
PDFMINER_TIMEOUT=1200
OCR_TIMEOUT=5400

# OCR Settings
OCR_LANGUAGES=nep+hin+eng
OCR_IMAGE_DPI=300
OCR_OPTIMIZE=1
```

### Using `.env` with Docker

Pass `--env-file .env` directly to `docker run`:

```bash
docker run --rm --env-file .env -v "${PWD}:/work" nepali-pdf-text --input-dir /work/pdf --output-dir /work/out-batch
```

> **Note**: Command-line arguments always override values defined in `.env`.

---

## 🛠️ Flexible Directory Mounting (Any Local Path)

You do not need to move files into the repository folder. Mount any directory from your machine:

**Windows PowerShell:**
```powershell
docker run --rm `
  -v "D:\Documents\NepaliPDFs:/input" `
  -v "D:\Documents\DOCX_Output:/output" `
  nepali-pdf-text --input-dir /input --output-dir /output --workers 4
```

**Linux / macOS:**
```bash
docker run --rm \
  -v "/path/to/my/pdfs:/input" \
  -v "/path/to/my/output:/output" \
  nepali-pdf-text --input-dir /input --output-dir /output --workers 4
```

---

## 💻 Local Development (Non-Docker Setup)

If you prefer running natively without Docker:

### 1. Install System Dependencies

#### Ubuntu / Debian:
```bash
sudo apt-get update && sudo apt-get install -y \
    poppler-utils \
    ocrmypdf \
    tesseract-ocr \
    tesseract-ocr-nep \
    tesseract-ocr-hin \
    tesseract-ocr-eng \
    unpaper \
    fonts-lohit-deva
```

#### macOS (Homebrew):
```bash
brew install poppler ocrmypdf tesseract tesseract-lang unpaper
```

#### Windows:
Using Docker is strongly recommended on Windows. If running natively, install:
- [Poppler for Windows](https://github.com/oschwartz10612/poppler-windows/releases/) (add `bin/` to your `PATH`)
- [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) (include Nepali and Hindi language data)
- [Ghostscript](https://ghostscript.com/) (required by `ocrmypdf`)

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run

```bash
# Process a single file
python main.py sample.pdf --output sample.docx

# Process a directory in batch
python main.py --input-dir ./pdfs --output-dir ./outputs --workers 4
```

---

## 📋 CLI Reference

```
python main.py [input_pdf] [options]
```

| Argument | Description | Default |
| :--- | :--- | :--- |
| `input_pdf` | Path to a single PDF to process | None |
| `--output` | Target `.docx` path for single-file mode | `<source_name>.docx` |
| `--input-dir` | Path to directory containing PDFs for batch processing | None |
| `--output-dir` | Directory to store generated `.docx` files | Same as source |
| `--workers` | Parallel worker threads for batch mode | `4` (or `WORKERS` env) |
| `--ocr-languages` | Tesseract OCR language models (joined with `+`) | `'nep+hin+eng'` |
| `--ocr-dpi` | Resolution (DPI) for OCR image rasterization | `300` |
| `--pdffonts-timeout` | Timeout in seconds for font inspection | `120` |
| `--pdftotext-timeout` | Timeout in seconds for Poppler extraction | `900` |
| `--pdfminer-timeout` | Timeout in seconds for PDFMiner extraction | `1200` |
| `--ocr-timeout` | Timeout in seconds for OCR fallback | `5400` |
| `--verbose`, `-v` | Enable detailed debug logging | False |
| `--quiet`, `-q` | Suppress all terminal output except errors | False |

---

## ⚡ Handling Huge PDFs (1,000+ Pages)

For very large documents or slow scanned files, increase stage timeouts:

```bash
docker run --rm -v "${PWD}:/work" nepali-pdf-text \
  --input-dir /work/pdf \
  --output-dir /work/out-batch \
  --ocr-timeout 14400 \
  --pdfminer-timeout 3600 \
  --pdftotext-timeout 3600 \
  --pdffonts-timeout 600
```

Alternatively, set these once in your `.env` file.

---

## ❓ Troubleshooting

- **`unpaper not found` during OCR?**  
  Ensure `unpaper` is installed or rebuild the Docker container (`docker build -t nepali-pdf-text .`). The script automatically catches missing `unpaper` and retries without post-processing deskew.
- **Garbled font output?**  
  If the source PDF uses legacy ASCII fonts (such as Preeti), the extractor deliberately preserves the copyable ASCII character layer so it can be converted accurately using a Devanagari Unicode mapping converter.
- **Missing font rendering in Word?**  
  The generated `.docx` files specify `Mangal` as the font family. Ensure your operating system or Microsoft Word has standard Devanagari font packs installed.
- **Slow OCR execution?**  
  Full OCR is CPU-intensive. Adjust `--workers` to match your CPU cores, or reduce `--ocr-dpi` (e.g., `--ocr-dpi 200`) for faster rasterization if scan quality permits.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
