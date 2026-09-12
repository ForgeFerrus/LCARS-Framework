import re

with open('lcars/ui/uefi.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = re.sub(r'Widget\((\w+)\)\.widget', r'\1.widget', content)

with open('lcars/ui/uefi.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Fixed uefi.py')
