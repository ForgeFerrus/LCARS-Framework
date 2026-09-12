import re

with open('lcars/ui/screen/bios.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = re.sub(r'NativeWidget\((\w+)\)', r'\1.widget', content)

with open('lcars/ui/screen/bios.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Replaced NativeWidget with .widget in bios.py')
