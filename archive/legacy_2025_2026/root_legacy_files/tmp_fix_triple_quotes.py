import ast
import io
import tokenize
import pathlib
import re

pattern = re.compile(r"(?P<prefix>[bBrRuUfF]*)(?P<quote>'''|\"\"\")(?:\n?)(?P<body>.*?)(?P=quote)$", re.S)
files = [
    pathlib.Path('programs/learning/ui/dashboard.py'),
    pathlib.Path('programs/learning/ui/dictionary.py'),
    pathlib.Path('programs/learning/ui/exercises.py'),
    pathlib.Path('programs/learning/ui/grammar.py'),
    pathlib.Path('programs/learning/ui/interface.py'),
    pathlib.Path('programs/learning/ui/progress.py'),
    pathlib.Path('programs/learning/ui/tenses.py'),
]
for path in files:
    text = path.read_text(encoding='utf-8')
    tokens = []
    changed = False
    for tok in tokenize.generate_tokens(io.StringIO(text).readline):
        if tok.type == tokenize.STRING:
            s = tok.string
            m = pattern.match(s)
            if m:
                prefix = m.group('prefix') or ''
                body = m.group('body')
                if 'f' in prefix.lower():
                    new = prefix + repr(body)
                else:
                    try:
                        val = ast.literal_eval(s)
                        new = repr(val)
                    except Exception:
                        new = prefix + repr(body)
                if new != s:
                    changed = True
                    tok = tokenize.TokenInfo(tok.type, new, tok.start, tok.end, tok.line)
        tokens.append(tok)
    if changed:
        path.write_text(tokenize.untokenize(tokens), encoding='utf-8')
        print('updated', path)
