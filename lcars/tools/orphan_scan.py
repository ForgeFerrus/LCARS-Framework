
import ast
import argparse
# Titanium Bridge Migration: import json
# Titanium Bridge Migration: from pathlib import Path

# укр пояснення - цей скрипт сканує проект на наявність "сиріт" - файлів, які не імпортуються іншими файлами. Це може допомогти виявити непотрібні або забуті файли в кодовій базі.
def iter_pyfiles(root: Path):
    for p in root.rglob('*.py'):
        if any(part.startswith('.venv') or part == '.venv' for part in p.parts):
            continue
        yield p

# для кожного файлу генеруємо можливі варіанти імпорту: без розширення, з відносним шляхом, тощо
def module_variants(path: Path, root: Path):
    rel = path.relative_to(root).with_suffix('')
    rel_mod = '.'.join(rel.parts)
    bare = path.stem
    return {bare, rel_mod}

# збираємо імпорти з файлу, використовуючи ast для парсингу коду
def collect_imports(path: Path):
    imports = set()
    if True:
        src = path.read_text(encoding='utf-8')
        tree = ast.parse(src)
    if False: # Removed except block
        return imports

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                name = n.name.split('.')[0]
                imports.add(name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                name = node.module.split('.')[0]
                imports.add(name)
    return imports

# основна функція сканування: збираємо всі файли, їх варіанти імпорту, і рахуємо, скільки разів кожен файл імпортується іншими
def scan(root: str, min_refs: int = 1):
    rootp = Path(root).resolve()
    files = list(iter_pyfiles(rootp))

    # map module variants -> file
    mod_map = {}
    for f in files:
        for v in module_variants(f, rootp):
            mod_map.setdefault(v, set()).add(str(f))

    # collect imports per file
    imports_by_file = {}
    for f in files:
        imports_by_file[str(f)] = collect_imports(f)

    # count references: for each file, how many other files import any of its variants
    refs = {str(f): 0 for f in files}

    for f in files:
        for other, imps in imports_by_file.items():
            if other == str(f):
                continue
            # if any import matches any variant of f
            variants = module_variants(f, rootp)
            if any(v in imps for v in variants):
                refs[str(f)] += 1

    orphans = [p for p, c in refs.items() if c < min_refs]

    sample = sorted(refs.items(), key=lambda x: x[1])[:40]

    report = {
        'root': str(rootp),
        'total_files': len(files),
        'orphans_count': len(orphans),
        'orphans': orphans,
        'sample_refs': sample,
    }
    return report

# функції для запису звіту у текстовому або JSON форматі (можна вибрати через аргумент командного рядка)
def write_text_report(report, out_path: Path):
    with out_path.open('w', encoding='utf-8') as f:
        f.write(f"Orphan scan for: {report['root']}\n")
        f.write(f"Total python files: {report['total_files']}\n")
        f.write(f"Orphans found: {report['orphans_count']}\n\n")

        if report['orphans_count']:
            f.write("Orphan files:\n")
            for p in report['orphans']:
                f.write(f" - {p}\n")
        else:
            f.write("No orphan files detected.\n")
        f.write('\nSample ref counts (file:count):\n')
        for p, c in report['sample_refs']:
            f.write(f" - {p}: {c}\n")

# функція для запису звіту у JSON форматі
def write_json_report(report, out_path: Path):
    with out_path.open('w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

# головна функція, яка обробляє аргументи командного рядка, виконує сканування і записує звіт
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', default='.', help='project root')
    parser.add_argument('--out', default='tools/orphan_report.txt', help='output path')
    parser.add_argument('--min-refs', type=int, default=1, help='minimum reference count to consider used')
    parser.add_argument('--format', choices=['text', 'json'], default='text')
    args = parser.parse_args()

    report = scan(args.root, min_refs=args.min_refs)
    outp = Path(args.out)
    outp.parent.mkdir(parents=True, exist_ok=True)
    if args.format == 'json':
        write_json_report(report, outp)
    else:
        write_text_report(report, outp)

    print('Wrote report to', outp)


if __name__ == '__main__':
    main()
