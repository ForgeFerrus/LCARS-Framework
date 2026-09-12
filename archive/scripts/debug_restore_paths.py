import os
import json
root = r"c:\Users\Forge\AppData\Roaming\Code\User\History"
needle = 'data/iso_chip/english_learning_a1_b1.json'
for name in os.listdir(root):
    d = os.path.join(root, name)
    fn = os.path.join(d, 'entries.json')
    if not os.path.isfile(fn):
        continue
    try:
        data = json.load(open(fn, 'r', encoding='utf-8'))
    except Exception:
        continue
    resource = data.get('resource', '')
    if needle in resource:
        print('FOUND resource:', resource)
        for entry in data.get('entries', []):
            print('  id', entry.get('id'), 'ts', entry.get('timestamp'))
        path = resource
        if path.startswith('file:///'):
            path = path[len('file:///'):]
        path = path.replace('/', os.sep)
        if path.startswith('c%3A'):
            path = path.replace('c%3A', 'c:')
        if path.startswith('c:'):
            path = path[2:]
        print('norm path', path)
        idx = path.find('LCARS-Framework')
        print('idx', idx)
        if idx >= 0:
            rel = path[idx + len('LCARS-Framework'):].lstrip(os.sep)
            print('rel', rel)
