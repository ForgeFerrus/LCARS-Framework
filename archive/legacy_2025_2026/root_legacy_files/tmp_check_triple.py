from pathlib import Path
files = [
    Path('programs/learning/ui/dashboard.py'),
    Path('programs/learning/ui/dictionary.py'),
    Path('programs/learning/ui/exercises.py'),
    Path('programs/learning/ui/grammar.py'),
    Path('programs/learning/ui/interface.py'),
    Path('programs/learning/ui/progress.py'),
    Path('programs/learning/ui/tenses.py'),
]
qq = '"""'
pq = "'''"
found = False
for path in files:
    text = path.read_text(encoding='utf-8')
    if qq in text or pq in text:
        found = True
        print(path)
print('found' if found else 'none')
