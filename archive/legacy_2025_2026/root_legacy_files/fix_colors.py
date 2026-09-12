#!/usr/bin/env python3
import re

# Read the file
with open('c:/Users/Forge/MyProject/LCARS-Framework/archive/era_files/LCARS_24th.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace all old color references with new theme system
replacements = [
    ("self.colors['background_color']", "self.colors.get('bg', '#000000')"),
    ("self.colors['text_color']", "self.colors.get('txt', '#FFFFFF')"),
    ("self.colors['panel_color']", "self.colors.get('btn2', '#664466')")
]

for old, new in replacements:
    content = content.replace(old, new)

# Write back to file
with open('c:/Users/Forge/MyProject/LCARS-Framework/archive/era_files/LCARS_24th.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Fixed all color references')
