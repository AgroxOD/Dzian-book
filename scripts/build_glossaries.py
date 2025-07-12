from collections import Counter, defaultdict
from pathlib import Path
import csv
import spacy
from spacy.lang.ru.stop_words import STOP_WORDS

ROOT = Path(__file__).resolve().parents[1]
OCR_DIR = ROOT / 'analyses' / 'ocr_full'
OUT_DIR = ROOT / 'analyses' / 'glossaries'

nlp = spacy.load('ru_core_news_sm', disable=["parser", "ner"])

OUT_DIR.mkdir(parents=True, exist_ok=True)


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


def process_book(book_id: str) -> Counter:
    book_dir = OCR_DIR / book_id
    if not book_dir.is_dir():
        raise FileNotFoundError(book_dir)
    text_parts = []
    for txt in sorted(book_dir.glob('page-*.txt')):
        text_parts.append(txt.read_text(encoding='utf-8'))
    return extract_terms("\n".join(text_parts))


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
    for book_id in sorted(book_ids):
        counts = process_book(book_id)
        save_glossary(book_id, counts)
        for term, cnt in counts.items():
            all_terms[term][book_id] = cnt
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
