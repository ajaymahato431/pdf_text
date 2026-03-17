import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    from pdfminer.high_level import extract_text as pdfminer_extract
except ImportError:  # pragma: no cover - handled at runtime
    pdfminer_extract = None


REQUIRED_COMMANDS = ("pdffonts", "pdftotext", "ocrmypdf")
BAD_PATTERNS = [r"ष्ट्र", r"प्", r"अतभ", r"त्तर्", r"ाँ"]


def ensure_python_dependencies() -> None:
    if pdfminer_extract is None:
        raise RuntimeError(
            "Missing Python dependency 'pdfminer.six'. Install it with "
            "'pip install -r requirements.txt'."
        )


def ensure_external_dependencies() -> None:
    missing_commands = [command for command in REQUIRED_COMMANDS if shutil.which(command) is None]
    if missing_commands:
        joined = ", ".join(missing_commands)
        raise RuntimeError(
            f"Missing required system commands: {joined}. "
            "Install poppler-utils and ocrmypdf (plus Tesseract language packs)."
        )


def check_unicode_mapping(pdf_path: Path) -> bool:
    """Return True when font metadata suggests Unicode text extraction is possible."""
    try:
        result = subprocess.run(
            ["pdffonts", str(pdf_path)],
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        details = exc.stderr.strip() or exc.stdout.strip() or str(exc)
        raise RuntimeError(f"Font inspection failed: {details}") from exc

    lines = result.stdout.splitlines()
    for line in lines[2:]:
        if not line.strip():
            continue
        columns = line.split()
        if len(columns) >= 6 and columns[5].lower() == "no":
            return False
    return True


def extract_with_poppler(pdf_path: Path) -> str:
    """Extract text with pdftotext and preserve layout where possible."""
    try:
        result = subprocess.run(
            ["pdftotext", "-layout", "-enc", "UTF-8", str(pdf_path), "-"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        details = exc.stderr.strip() or exc.stdout.strip() or str(exc)
        raise RuntimeError(f"Poppler extraction failed: {details}") from exc

    return result.stdout


def is_text_valid(text: str) -> bool:
    """
    Evaluate whether extracted Devanagari text looks usable.
    """
    if not text.strip():
        return False

    error_count = sum(len(re.findall(pattern, text)) for pattern in BAD_PATTERNS)
    return error_count <= 3


def run_ocr_and_extract(pdf_path: Path) -> str:
    """Run OCRmyPDF to rebuild the text layer, then re-extract via Poppler."""
    print("Running OCR fallback...")
    with tempfile.TemporaryDirectory() as temp_dir:
        ocr_output = Path(temp_dir) / "ocr_output.pdf"
        try:
            completed = subprocess.run(
                [
                    "ocrmypdf",
                    "-l",
                    "nep",
                    "--deskew",
                    "--force-ocr",
                    str(pdf_path),
                    str(ocr_output),
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=True,
            )
        except subprocess.CalledProcessError as exc:
            details = exc.stderr.strip() or exc.stdout.strip() or str(exc)
            raise RuntimeError(f"OCR fallback failed: {details}") from exc

        if completed.stderr.strip():
            print(completed.stderr.strip())
        return extract_with_poppler(ocr_output)


def process_nepali_pdf(pdf_path: Path) -> tuple[str, str]:
    """Extract text from a single PDF and return (text, method)."""
    print(f"Processing: {pdf_path}")

    if not pdf_path.exists():
        raise FileNotFoundError(f"Cannot find input PDF: {pdf_path}")
    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(f"Input is not a PDF: {pdf_path}")

    has_unicode = check_unicode_mapping(pdf_path)
    if has_unicode:
        print("Unicode mapping found. Trying Poppler first.")
        text = extract_with_poppler(pdf_path)
        if is_text_valid(text):
            return text, "poppler"

        print("Poppler output failed validation. Trying PDFMiner.")
        text = pdfminer_extract(str(pdf_path))
        if is_text_valid(text):
            return text, "pdfminer"

        print("PDFMiner output failed validation. Falling back to OCR.")
    else:
        print("Missing Unicode mapping detected. Skipping directly to OCR.")

    text = run_ocr_and_extract(pdf_path)
    if text.strip():
        return text, "ocr"

    raise RuntimeError("All extraction methods failed or returned empty text.")


def default_output_path(pdf_path: Path) -> Path:
    return pdf_path.with_suffix(".txt")


def write_text_output(output_path: Path, text: str) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text, encoding="utf-8")


def process_single_file(input_pdf: Path, output_path: Path | None) -> int:
    target_output = output_path or default_output_path(input_pdf)
    text, method = process_nepali_pdf(input_pdf)
    write_text_output(target_output, text)
    print(f"Extraction successful via {method}.")
    print(f"Saved text to: {target_output}")
    return 0


def process_directory(input_dir: Path, output_dir: Path | None) -> int:
    if not input_dir.exists():
        raise FileNotFoundError(f"Input directory does not exist: {input_dir}")
    if not input_dir.is_dir():
        raise NotADirectoryError(f"Input path is not a directory: {input_dir}")

    pdf_files = sorted(path for path in input_dir.iterdir() if path.is_file() and path.suffix.lower() == ".pdf")
    if not pdf_files:
        raise FileNotFoundError(f"No PDF files found in directory: {input_dir}")

    failures = 0
    for pdf_path in pdf_files:
        if output_dir is None:
            target_output = default_output_path(pdf_path)
        else:
            target_output = output_dir / f"{pdf_path.stem}.txt"

        try:
            text, method = process_nepali_pdf(pdf_path)
            write_text_output(target_output, text)
            print(f"Extraction successful via {method}.")
            print(f"Saved text to: {target_output}")
        except Exception as exc:  # pragma: no cover - depends on external tools/files
            failures += 1
            print(f"Failed to process {pdf_path}: {exc}", file=sys.stderr)

    return 1 if failures else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Extract Nepali text from PDFs using Poppler, PDFMiner, and OCR fallback."
    )
    parser.add_argument(
        "input_pdf",
        nargs="?",
        help="Path to a single PDF file to process.",
    )
    parser.add_argument(
        "--output",
        help="Optional text output path for single-file mode.",
    )
    parser.add_argument(
        "--input-dir",
        help="Process all PDFs in this directory (non-recursive).",
    )
    parser.add_argument(
        "--output-dir",
        help="Optional directory to receive .txt outputs in batch mode.",
    )
    return parser


def validate_args(args: argparse.Namespace, parser: argparse.ArgumentParser) -> None:
    if bool(args.input_pdf) == bool(args.input_dir):
        parser.error("Specify exactly one of: input_pdf or --input-dir.")
    if args.output and not args.input_pdf:
        parser.error("--output can only be used with single-file mode.")
    if args.output_dir and not args.input_dir:
        parser.error("--output-dir can only be used with --input-dir.")


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    validate_args(args, parser)

    try:
        ensure_python_dependencies()
        ensure_external_dependencies()

        if args.input_pdf:
            output_path = Path(args.output) if args.output else None
            return process_single_file(Path(args.input_pdf), output_path)

        output_dir = Path(args.output_dir) if args.output_dir else None
        return process_directory(Path(args.input_dir), output_dir)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
