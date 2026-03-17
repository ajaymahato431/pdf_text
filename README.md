# Nepali PDF Text Extractor

This project extracts text from Nepali PDF files inside Docker.

It tries extraction in this order:

1. `pdffonts` to inspect font Unicode mapping
2. `pdftotext` for direct text extraction
3. `pdfminer.six` as a fallback for broken direct extraction
4. `ocrmypdf` with Nepali OCR when the PDF text layer is missing or unusable

## Prerequisites

- Docker Desktop installed and running
- Windows PowerShell
- This project available locally at:
  `c:\laragon\www\htdocs\aDocker\pdf_text`

## Project Files

- `main.py`: CLI application
- `Dockerfile`: container definition
- `requirements.txt`: Python dependencies
- `pdf/`: sample input PDFs

## Step 1: Open PowerShell In The Project Folder

```powershell
cd c:\laragon\www\htdocs\aDocker\pdf_text
```

## Step 2: Build The Docker Image

Build the image once:

```powershell
docker build -t nepali-pdf-text .
```

This creates a Docker image named `nepali-pdf-text`.

You can confirm it exists with:

```powershell
docker images
```

## Step 3: Run The Built Image For One PDF

This runs a container from the already built image and writes output to `out-single.txt` in the project folder:

```powershell
docker run --rm -v "${PWD}:/work" nepali-pdf-text '/work/pdf/औद्योगिक नीति, २०६७.pdf' --output /work/out-single.txt
```

What this does:

- `docker run`: starts a container from an image
- `--rm`: removes the container after it finishes
- `-v "${PWD}:/work"`: mounts the current project folder into the container
- `nepali-pdf-text`: the image name
- `'/work/pdf/औद्योगिक नीति, २०६७.pdf'`: input PDF inside the container
- `--output /work/out-single.txt`: output text file inside the mounted folder

After it finishes, you should see:

- `out-single.txt`

## Step 4: Run The Already Built Image Again

You do not need to rebuild the image every time.

As long as you have not changed the code or Dockerfile, just run the image again:

```powershell
docker run --rm -v "${PWD}:/work" nepali-pdf-text '/work/pdf/राष्ट्रिय बौद्धिक सम्पत्ति नीति, २०७३.pdf' --output /work/second-output.txt
```

You only need to rebuild if you change:

- `main.py`
- `Dockerfile`
- `requirements.txt`

If you changed any of those files, rebuild:

```powershell
docker build -t nepali-pdf-text .
```

## Step 5: Run Batch Mode For All PDFs

This processes every `.pdf` file inside `pdf/` and writes `.txt` files into `out-batch/`:

```powershell
docker run --rm -v "${PWD}:/work" nepali-pdf-text --input-dir /work/pdf --output-dir /work/out-batch
```

After it finishes, you should see output files such as:

- `out-batch\औद्योगिक नीति, २०६७.txt`
- `out-batch\राष्ट्रिय बौद्धिक सम्पत्ति नीति, २०७३.txt`

## Step 6: Run Without Explicit Output Path

### Single-file mode

If you omit `--output`, the `.txt` file is written next to the input PDF:

```powershell
docker run --rm -v "${PWD}:/work" nepali-pdf-text '/work/pdf/औद्योगिक नीति, २०६७.pdf'
```

That will create:

- `pdf\औद्योगिक नीति, २०६७.txt`

### Batch mode

If you omit `--output-dir`, each `.txt` file is written next to its source PDF:

```powershell
docker run --rm -v "${PWD}:/work" nepali-pdf-text --input-dir /work/pdf
```

## Step 7: Show CLI Help

You can see all supported arguments with:

```powershell
docker run --rm nepali-pdf-text --help
```

## Common Commands

Build image:

```powershell
docker build -t nepali-pdf-text .
```

Run one PDF:

```powershell
docker run --rm -v "${PWD}:/work" nepali-pdf-text '/work/pdf/औद्योगिक नीति, २०६७.pdf' --output /work/out-single.txt
```

Run all PDFs:

```powershell
docker run --rm -v "${PWD}:/work" nepali-pdf-text --input-dir /work/pdf --output-dir /work/out-batch
```

Show help:

```powershell
docker run --rm nepali-pdf-text --help
```

## Troubleshooting

If Docker says the image does not exist, build it first:

```powershell
docker build -t nepali-pdf-text .
```

If you changed the code but the container still behaves like the old version, rebuild the image:

```powershell
docker build -t nepali-pdf-text .
```

If OCR runs, it may take longer and print warnings from `ocrmypdf`. That is expected.

If you want to remove the built image later:

```powershell
docker rmi nepali-pdf-text
```
