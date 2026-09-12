from __future__ import annotations

from pathlib import Path
import re

# утиліта для виведення списку файлів, які вказані в PROJECT_STRUCTURE.md, але не існують в проекті
def parse_missing(md_path: Path):
    txt = md_path.read_text(encoding='utf-8')
    missing = re.findall(r"- `([^`]+)` — MISSING", txt)
    return missing

# основна функція, яка викликає parse_missing і виводить список відсутніх файлів в проекті PROJECT_STRUCTURE.md
def main():
    root = Path(__file__).parent.parent
    md = root / 'PROJECT_STRUCTURE.md'
    if not md.exists():
        print('PROJECT_STRUCTURE.md not found')
        return
    missing = parse_missing(md)
    print('Missing files listed in PROJECT_STRUCTURE.md:')
    for p in missing:
        print(' -', p)


if __name__ == '__main__':
    main()
