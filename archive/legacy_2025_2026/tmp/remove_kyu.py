# Remove stray 'кю' occurrences from .py files
import os
changed = []
for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in ('__pycache__', '.git', '.venv', 'resources')]
    for fn in files:
        if not fn.endswith('.py'):
            continue
        path = os.path.join(root, fn)
        try:
            with open(path, 'r', encoding='utf-8', errors='replace') as f:
                s = f.read()
        except Exception:
            continue
        if 'кю' in s or 'Кю' in s or 'КЮ' in s or 'кЮ' in s:
            new = s.replace('кю', '').replace('Кю','').replace('КЮ','').replace('кЮ','')
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new)
            changed.append(path.replace('\\','/'))
print('FILES_CHANGED:', len(changed))
for p in changed:
    print(p)
