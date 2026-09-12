#!/usr/bin/env python3
import re

# Read the file
with open('c:\\Users\\Forge\\MyProject\\LCARS-Framework\\archive\\era_files\\LCARS_24th.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the corrupted CSS section and replace it
pattern = r'font-family: \'Swiss 911\', \' . \. sans-serifFI;.*?\"\"\"'
replacement = '''font-family: 'Swiss 911', 'Arial', sans-serif;
            font-weight: bold;
            padding: 10px;
        \"\"\'''

content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# Write back to file
with open('c:\\Users\\Forge\\MyProject\\LCARS-Framework\\archive\\era_files\\LCARS_24th.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Fixed CSS in project_title')
