from __future__ import annotations
from pathlib import Path
import json
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
LOG_FILE = ROOT / 'analyses' / 'run_logs.json'


def load_logs() -> dict:
    if LOG_FILE.exists():
        with LOG_FILE.open(encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_logs(data: dict) -> None:
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open('w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def update_log(script: str, info: dict) -> None:
    logs = load_logs()
    section = logs.get(script, {})
    section.update(info)
    section['timestamp'] = datetime.now().isoformat()
    logs[script] = section
    save_logs(logs)


def get_script_log(script: str) -> dict:
    return load_logs().get(script, {})
