from pathlib import Path
import csv

from .utils import update_log

ROOT = Path(__file__).resolve().parents[1]
OCR_DIR = ROOT / 'analyses' / 'ocr_full' / '1'
META_FILE = ROOT / 'analyses' / 'metadata.csv'

rows = []
for page_file in sorted(OCR_DIR.glob('page-*.txt')):
    page_num = page_file.stem.split('-')[-1]
    rows.append({'page': page_num, 'section': '', 'notes': ''})

with META_FILE.open('w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['page', 'section', 'notes'])
    writer.writeheader()
    writer.writerows(rows)

update_log('create_metadata.py', {'pages': len(rows)})
