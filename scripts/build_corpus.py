import os
from pathlib import Path
import csv
import spacy

from .utils import update_log, get_script_log

ROOT = Path(__file__).resolve().parents[1]
OCR_DIR = ROOT / 'analyses' / 'ocr_full'
OUT_DIR = ROOT / 'analyses' / 'lemma_pos'

nlp = spacy.load('ru_core_news_sm')

OUT_DIR.mkdir(parents=True, exist_ok=True)


def process_pdf(pdf_id: str, max_pages: int | None = None):
    src_dir = OCR_DIR / pdf_id
    if not src_dir.is_dir():
        raise FileNotFoundError(src_dir)
    out_pdf_dir = OUT_DIR / pdf_id
    out_pdf_dir.mkdir(exist_ok=True)
    pages = sorted(src_dir.glob('page-*.txt'))
    if max_pages is not None:
        pages = pages[:max_pages]
    logs = get_script_log('build_corpus.py')
    last_page = int(logs.get(pdf_id, {}).get('last_page', 0))
    pages = pages[last_page:]
    for page_file in pages:
        page_num = page_file.stem.split('-')[-1]
        out_file = out_pdf_dir / f'{page_file.stem}.csv'
        if out_file.exists():
            continue
        text = page_file.read_text(encoding='utf-8', errors='ignore')
        doc = nlp(text)
        with out_file.open('w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['page', 'token', 'lemma', 'pos'])
            for token in doc:
                if not token.text.strip():
                    continue
                writer.writerow([page_num, token.text, token.lemma_, token.pos_])
        last_page += 1
        update_log('build_corpus.py', {pdf_id: {'last_page': last_page}})


if __name__ == '__main__':
    limit = None
    try:
        limit = int(os.environ.get('MAX_PAGES', ''))
    except ValueError:
        pass
    for pdf in ['1']:
        process_pdf(pdf, limit)
