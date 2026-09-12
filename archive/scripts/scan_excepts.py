import os
import glob
import re

def clean_excepts(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        original = content
        
        # We need to explicitly parse and remove or replace the logic.
        # But auto-removing try/except blocks is dangerous with regex because of indentation.
        # We will instead log the locations to guide manual replacement.
        lines = content.split('\n')
        has_except = False
        for i, line in enumerate(lines):
            if re.search(r'^\s*try:', line) or re.search(r'^\s*except\b', line):
                has_except = True
                break
        
        if has_except:
            print(f'File needs except removal: {filepath}')
            return True
    except Exception as e:
        print(f"Error on {filepath}: {e}")
        pass
    return False

files = glob.glob('lcars/base/**/*.py', recursive=True)
for f in files:
    clean_excepts(f)

