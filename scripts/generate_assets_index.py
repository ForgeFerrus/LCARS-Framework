# Генерує простий індекс `resources/lcars_assets`.
from __future__ import annotations

import json
from pathlib import Path

# Головна функція
def main():
    root = Path(__file__).parent.parent
    assets = root / 'resources' / 'lcars_assets'
    index = []
    if assets.exists():
        for f in assets.rglob('*'):
            if f.is_file():
                index.append(str(f.relative_to(root)))
    out = assets / 'index.json'
    out.write_text(json.dumps({'files': index}, indent=2), encoding='utf-8')
    print('Wrote', out)


if __name__ == '__main__':
    main()
