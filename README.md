# Nepali PDF Text Extractor (DOCX Edition)

This tool extracts high-accuracy Nepali text from PDFs and exports directly to **DOCX** files formatted with the **Mangal** font.

It uses a multi-stage approach for maximum accuracy:

1. **Direct Extraction**: Uses `pdftotext` (Poppler) for clean, layout-preserved text.
2. **Font Fallback**: Uses `pdfminer.six` if standard extraction fails.
3. **OCR Fallback**: Uses `ocrmypdf` with Nepali, Hindi, and English models for scanned or image-based PDFs.
4. **ASCII Text Handling**: Keeps clean copyable `A-Za-z0-9` text as-is, including legacy-font text that will be converted later.
5. **Accuracy Scoring**: Applies Devanagari validation only when the extracted text is actually Unicode Devanagari.
6. **Post-Processing**: Normalizes Unicode (NFC), cleans whitespace, and formats for Word.

---

## 🚀 Quick Start (Docker)

### 1. Build the Image (One-time only)

Open PowerShell in this folder and build the image:

```powershell
docker build -t nepali-pdf-text .
```

### 2. Basic Usage (Current Folder)

Process all PDFs in your local `pdf/` folder and save to `out-batch/`:

```powershell
docker run --rm -v "${PWD}:/work" nepali-pdf-text --input-dir /work/pdf --output-dir /work/out-batch
```

---

## 🛠️ Flexible Use (Any Local Path)

**No need to move files or rebuild the image.** You can process PDFs from anywhere on your Windows disk by mounting them as volumes (`-v`).

### Process a Single PDF from anywhere

```powershell
docker run --rm `
  -v "C:\Users\ADMIN\Documents\MyPDFs:/input" `
  -v "C:\Users\ADMIN\Desktop\output:/output" `
  nepali-pdf-text '/input/somefile.pdf' --output /output/somefile.docx
```

### Process an Entire Folder from anywhere

```powershell
docker run --rm `
  -v "D:\AllMyPDFs:/input" `
  -v "D:\Results:/output" `
  nepali-pdf-text --input-dir /input --output-dir /output --workers 4
```

_Note: `/input` and `/output` are just names used inside the container. You can name them anything._

---

## ⚡ Batch Processing Features

The tool is optimized for processing hundreds of PDFs:

| Feature                | Command / Detail                                                   |
| :--------------------- | :----------------------------------------------------------------- |
| **Parallel Workers**   | Add `--workers 8` to use more CPU cores.                           |
| **Progress Tracking**  | Shows `[3/150] ✓ filename` in real-time.                           |
| **Batch Summary**      | Prints a structured results table at the end.                      |
| **Auto-Naming**        | If `--output` is omitted, it saves `.docx` next to the source PDF. |
| **Verbose / Quiet**    | Use `--verbose` for debug output or `--quiet` for errors only.     |
| **Hindi + Nepali + English OCR** | OCR uses Nepali, Hindi, and English language data for mixed-language PDFs. |

---

## 📋 Common Commands Reference

| Goal                   | Sample Command                                                                 |
| :--------------------- | :----------------------------------------------------------------------------- |
| **Custom Output Path** | `... nepali-pdf-text '/work/input.pdf' --output /work/custom.docx`             |
| **High Performance**   | `... nepali-pdf-text --input-dir /work/pdf --output-dir /work/out --workers 8` |
| **Debug Logging**      | `... nepali-pdf-text --input-dir /work/pdf --verbose`                          |
| **Errors Only**        | `... nepali-pdf-text --input-dir /work/pdf --quiet`                            |
| **Help / Arguments**   | `docker run --rm nepali-pdf-text --help`                                       |

---

## 🛠️ Local Development (Non-Docker)

If you prefer running without Docker, ensure you have:

1. **Tesseract OCR** (with Nepali, Hindi, and English data)
2. **Poppler-utils** (for pdftotext)
3. **Python packages**: `pip install -r requirements.txt`

Then run: `python main.py --input-dir ./pdfs`

---

## ❓ Troubleshooting

- **Rebuild needed?** Only if you change `main.py` or `Dockerfile`. Run: `docker build -t nepali-pdf-text .`
- **`unpaper` error during OCR?** Rebuild the image after this update so the container includes `unpaper`: `docker build -t nepali-pdf-text .`
- **Missing Nepali Font?** The Docker image automatically installs `fonts-lohit-deva` for proper DOCX rendering.
- **OCR taking long?** This is normal for scanned PDFs as it runs deskewing and optimization.
