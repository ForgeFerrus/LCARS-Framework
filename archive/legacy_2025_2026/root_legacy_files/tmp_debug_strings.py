import tokenize, io
from pathlib import Path
path = Path('programs/learning/ui/dashboard.py')
text = path.read_text(encoding='utf-8')
count = 0
for tok in tokenize.generate_tokens(io.StringIO(text).readline):
    if tok.type == tokenize.STRING:
        prefixes = ['','f','F','r','R','b','B','fr','Fr','fR','FR','rf','rF','Rf','RF','br','Br','bR','BR','rb','rB','Rb','RB']
        if any(tok.string.startswith(prefix + chr(34)*3) or tok.string.startswith(prefix + chr(39)*3) for prefix in prefixes):
            print('FOUND', tok.string[:50])
            count += 1
print('count', count)
