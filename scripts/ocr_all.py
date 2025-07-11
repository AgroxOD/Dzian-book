import os
import subprocess
import shutil
from pathlib import Path

try:
    from PyPDF2 import PdfReader  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    PdfReader = None

ROOT = Path(__file__).resolve().parents[1]
CORE_DIR = ROOT / "core_texts"
OUT_DIR = ROOT / "analyses" / "ocr_full"

OUT_DIR.mkdir(parents=True, exist_ok=True)


def get_page_count(pdf_path: Path) -> int:
    """Return the number of pages in *pdf_path*.

    Tries ``pdfinfo`` if available, otherwise falls back to ``PyPDF2``.
    """
    if shutil.which("pdfinfo"):
        info = subprocess.check_output(["pdfinfo", str(pdf_path)], text=True)
        for line in info.splitlines():
            if line.startswith("Pages:"):
                return int(line.split()[1])
    if PdfReader is not None:
        with open(pdf_path, "rb") as f:
            reader = PdfReader(f)
            return len(reader.pages)
    raise RuntimeError(
        "Cannot determine page count; install poppler-utils or PyPDF2"
    )


def run_ocr(pdf_path: Path, max_pages: int | None = None):
    if not shutil.which("pdftoppm"):
        raise RuntimeError("pdftoppm not found; install poppler-utils")
    if not shutil.which("tesseract"):
        raise RuntimeError("tesseract not found; install tesseract-ocr")
    base = pdf_path.stem
    pdf_out = OUT_DIR / base
    pdf_out.mkdir(exist_ok=True)
    total_pages = get_page_count(pdf_path)
    if max_pages is not None:
        total_pages = min(total_pages, max_pages)
    for page in range(1, total_pages + 1):
        txt_file = pdf_out / f"page-{page:04d}.txt"
        if txt_file.exists():
            continue
        img_prefix = pdf_out / f"page-{page:04d}"
        subprocess.run([
            "pdftoppm",
            "-r",
            "300",
            "-f",
            str(page),
            "-l",
            str(page),
            "-png",
            str(pdf_path),
            str(img_prefix),
        ], check=True)
        pattern = f"{img_prefix.name}-*.png"
        files = list(pdf_out.glob(pattern))
        if not files:
            raise FileNotFoundError(f"Image not created for page {page}")
        img_file = files[0]
        subprocess.run([
            "tesseract",
            str(img_file),
            str(txt_file.with_suffix("")),
            "-l",
            "rus+eng",
        ], check=True)
        img_file.unlink()


if __name__ == "__main__":
    limit = None
    try:
        limit = int(os.environ.get("MAX_PAGES", ""))
    except ValueError:
        pass
    for pdf in CORE_DIR.glob("*.pdf"):
        run_ocr(pdf, limit)
