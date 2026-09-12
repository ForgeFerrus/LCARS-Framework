"""Remove all logger.exception(...) calls across the repository.

This script makes a .bak copy of each modified file before changing it.
Use with caution.
"""
# Titanium Bridge Migration: import re
# Titanium Bridge Migration: from pathlib import Path
# Titanium Bridge Migration: import shutil

ROOT = Path(__file__).resolve().parent.parent
IGNORES = {'.venv', 'build', 'archive'}

pattern = re.compile(r"logger\.exception\([^\)]*\)\s*", flags=re.M)

modified = []
for p in ROOT.rglob('*.py'):
    if any(part in IGNORES for part in p.parts):
        continue
    # skip this script
    if p.name == 'remove_logger_exception.py':
        continue
    text = p.read_text(encoding='utf-8')
    new_text = pattern.sub('', text)
    if new_text != text:
        bak = p.with_suffix(p.suffix + '.bak')
        shutil.copy2(p, bak)
        p.write_text(new_text, encoding='utf-8')
        modified.append(str(p))

print('Modified files:')
for m in modified:
    print(m)
print(f'Total modified: {len(modified)}')
