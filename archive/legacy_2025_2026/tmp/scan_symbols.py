#!/usr/bin/env python3
import os, re, sys
root = r'C:\Users\Forge\MyProject\LCARS-Framework'
skipdirs = {'.git','__pycache__','archive','archives','.venv','tmp'}

kju_pat = re.compile('кю', re.I)
pyqt_pat = re.compile(r'\bPyQt\d+\b')
qclass_pat = re.compile(r'\bQ[A-Za-z_][A-Za-z0-9_]*\b')
triple_pat = re.compile(r"('''|\"\"\")")
logging_pat = re.compile(r'\bimport logging\b|logging\.getLogger|logger\s*=')

kju_hits = []
pyqt_files = set()
q_files = {}
triple_files = {}
logging_files = set()

for dirpath, dirnames, filenames in os.walk(root):
    dirnames[:] = [d for d in dirnames if d not in skipdirs]
    for fn in filenames:
        if not fn.endswith('.py'):
            continue
        fp = os.path.join(dirpath, fn)
        rel = fp[len(root)+1:]
        try:
            text = open(fp, encoding='utf-8', errors='replace').read()
        except Exception:
            continue
        if kju_pat.search(text):
            lines = []
            for i,l in enumerate(text.splitlines()):
                if kju_pat.search(l):
                    lines.append((i+1, l.strip()[:120]))
            kju_hits.append((rel, lines))
        if pyqt_pat.search(text):
            pyqt_files.add(rel)
        qmatches = set(qclass_pat.findall(text))
        # filter obvious non-Qt names (Queue, QUOTE, etc.) heuristically by common Qt prefix
        qmatches_filtered = {m for m in qmatches if m.startswith('Q') and len(m) > 1}
        if qmatches_filtered:
            q_files[rel] = list(sorted(qmatches_filtered))[:20]
        if triple_pat.search(text):
            # count occurrences
            occ = len(triple_pat.findall(text))
            triple_files[rel] = occ
        if logging_pat.search(text):
            logging_files.add(rel)

# Print summary
print('SUMMARY REPORT')
print('==============')
print(f"Literal 'кю' matches: {len(kju_hits)}")
for rel, lines in kju_hits[:25]:
    print('  ', rel)
    for ln, txt in lines[:3]:
        print(f'     L{ln}: {txt}')

print('\nPyQt import occurrences (files):', len(pyqt_files))
for p in sorted(list(pyqt_files))[:50]:
    print('  ', p)

print('\nFiles with Q*-like tokens:', len(q_files))
for rel, toks in list(q_files.items())[:50]:
    print('  ', rel, ' => ', ','.join(toks[:8]))

print('\nFiles with triple-quote occurrences:', len(triple_files))
for rel, occ in list(triple_files.items())[:50]:
    print('  ', rel, 'occurrences=', occ)

print('\nFiles importing or using logging:', len(logging_files))
for p in sorted(list(logging_files))[:50]:
    print('  ', p)

# Save JSON report
report = {
    'kju': kju_hits,
    'pyqt_files': sorted(list(pyqt_files)),
    'q_files_count': len(q_files),
    'q_files_sample': {k: v for k,v in list(q_files.items())[:100]},
    'triple_files': triple_files,
    'logging_files': sorted(list(logging_files)),
}

out = os.path.join(root, 'tmp', 'scan_symbols_report.json')
try:
    with open(out, 'w', encoding='utf-8') as f:
        import json
        json.dump(report, f, ensure_ascii=False, indent=2)
    print('\nReport saved to', out)
except Exception as e:
    print('Failed to save report:', e)
