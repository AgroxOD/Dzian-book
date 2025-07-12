from pathlib import Path

from .utils import update_log

ROOT = Path(__file__).resolve().parents[1]
ANALYSIS_DIR = ROOT / "analyses"
OUT_FILE = ANALYSIS_DIR / "truth_core.md"

IGNORED = ["Уровень уверенности", "Самооценка"]


def extract_bullets(md_path: Path) -> list[str]:
    bullets = []
    for line in md_path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("- "):
            continue
        if any(word in line for word in IGNORED):
            continue
        bullets.append(line[2:].strip())
    return bullets


def main() -> None:
    lines = ["# Ядро истины", ""]
    files = sorted(ANALYSIS_DIR.glob("*_analysis_10wise.md")) + sorted(
        ANALYSIS_DIR.glob("*_cognitive_core.md")
    )
    for path in files:
        lines.append(f"## {path.stem}")
        for bullet in extract_bullets(path):
            lines.append(f"- {bullet}")
        lines.append("")
    OUT_FILE.write_text("\n".join(lines), encoding="utf-8")
    update_log('build_truth_core.py', {'files': len(files)})


if __name__ == "__main__":
    main()
