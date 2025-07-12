from __future__ import annotations
from collections import Counter, defaultdict
from pathlib import Path
import json
import os
import csv
import spacy
from spacy.lang.ru.stop_words import STOP_WORDS

from .utils import update_log, get_script_log

ROOT = Path(__file__).resolve().parents[1]
OCR_DIR = ROOT / 'analyses' / 'ocr_full'
OUT_DIR = ROOT / 'analyses' / 'glossaries'
INTERIM_DIR = OUT_DIR / 'interim'

nlp = spacy.load('ru_core_news_sm', disable=["parser", "ner"])
nlp.max_length = max(nlp.max_length, 2_000_000)

OUT_DIR.mkdir(parents=True, exist_ok=True)
INTERIM_DIR.mkdir(parents=True, exist_ok=True)


def extract_terms(text: str) -> Counter:
    doc = nlp(text)
    counts = Counter()
    for token in doc:
        if not token.is_alpha:
            continue
        if token.text.lower() in STOP_WORDS:
            continue
        lemma = token.lemma_.lower()
        counts[lemma] += 1
    return counts


def load_interim(book_id: str) -> tuple[Counter, int]:
    file = INTERIM_DIR / f'{book_id}.json'
    if file.exists():
        data = json.loads(file.read_text(encoding='utf-8'))
        counts = Counter(data.get('counts', {}))
        last = int(data.get('last_page', 0))
        return counts, last
    return Counter(), 0


def save_interim(book_id: str, counts: Counter, last_page: int) -> None:
    file = INTERIM_DIR / f'{book_id}.json'
    file.write_text(
        json.dumps({'counts': dict(counts), 'last_page': last_page}, ensure_ascii=False, indent=2),
        encoding='utf-8'
    )


def process_book(book_id: str, last_page: int, chunk: int, max_pages: int | None = None) -> tuple[Counter, int]:
    book_dir = OCR_DIR / book_id
    if not book_dir.is_dir():
        raise FileNotFoundError(book_dir)
    counts, saved_last = load_interim(book_id)
    if last_page < saved_last:
        last_page = saved_last
    pages = sorted(book_dir.glob('page-*.txt'))
    if max_pages is not None:
        pages = pages[:max_pages]
    start = last_page
    end = start + chunk if chunk > 0 else len(pages)
    to_process = pages[start:end]
    for txt in to_process:
        text = txt.read_text(encoding='utf-8')
        counts.update(extract_terms(text))
    last_page = start + len(to_process)
    save_interim(book_id, counts, last_page)
    return counts, last_page


def save_glossary(book_id: str, counts: Counter) -> None:
    out_file = OUT_DIR / f'{book_id}_glossary.csv'
    with out_file.open('w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['term', 'count'])
        for term, cnt in counts.most_common():
            writer.writerow([term, cnt])


def main() -> None:
    all_terms: defaultdict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    book_ids = [d.name for d in OCR_DIR.iterdir() if d.is_dir()]
    limit = None
    try:
        limit = int(os.environ.get('MAX_PAGES', ''))
    except ValueError:
        pass
    chunk = int(os.environ.get('PAGES_PER_RUN', '50'))
    logs = get_script_log('build_glossaries.py')
    update_info = {}
    for book_id in sorted(book_ids):
        last_page = int(logs.get(book_id, {}).get('last_page', 0))
        counts, last_page = process_book(book_id, last_page, chunk, limit)
        total_pages = len(sorted((OCR_DIR / book_id).glob('page-*.txt')))
        if limit is not None:
            total_pages = min(total_pages, limit)
        if last_page >= total_pages:
            save_glossary(book_id, counts)
            (INTERIM_DIR / f'{book_id}.json').unlink(missing_ok=True)
        update_info[book_id] = {'last_page': last_page}
        for term, cnt in counts.items():
            all_terms[term][book_id] = cnt
    update_log('build_glossaries.py', update_info)
    # save comparison
    comparison_file = OUT_DIR / 'comparison.csv'
    all_books = sorted(book_ids)
    with comparison_file.open('w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        header = ['term'] + all_books
        writer.writerow(header)
        for term in sorted(all_terms):
            row = [term] + [all_terms[term].get(b, 0) for b in all_books]
            writer.writerow(row)


if __name__ == '__main__':
    main()
