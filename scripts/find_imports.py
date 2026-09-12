import os

root = r'C:\Users\Forge\MyProject\LCARS-Framework'
needle = 'lcars.base.errors'
matches = []

for dirpath, dirnames, filenames in os.walk(root):
    if 'node_modules' in dirpath or '.git' in dirpath:
        continue
    for f in filenames:
        if not f.endswith('.py'):
            continue
        p = os.path.join(dirpath, f)
        try:
            with open(p, 'r', encoding='utf-8') as fh:
                txt = fh.read()
        except Exception:
            continue
        if needle in txt:
            matches.append(p)

print(len(matches))
for m in matches[:20]:
    print(m)
