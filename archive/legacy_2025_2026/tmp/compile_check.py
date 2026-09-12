import py_compile, os
broken = []
total = 0
for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in ('__pycache__','.git','.venv','resources')]
    for f in files:
        if f.endswith('.py'):
            total += 1
            path = os.path.join(root,f)
            try:
                py_compile.compile(path, doraise=True)
            except py_compile.PyCompileError as e:
                broken.append((path, str(e)))
print(f'Total: {total}, OK: {total-len(broken)}, BROKEN: {len(broken)}')
for p, e in broken:
    print('---')
    print(p)
    print(str(e).split('\n')[0])
