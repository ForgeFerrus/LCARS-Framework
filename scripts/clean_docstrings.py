import os
import glob
import re

def clean_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        original = content
        
        # Remove triple double quotes
        content = re.sub(r'\"\"\"[\s\S]*?\"\"\"', '', content)
        # Remove triple single quotes
        content = re.sub(r"'''[\s\S]*?'''", '', content)

        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f'Cleaned docstrings: {filepath}')
            return True
    except Exception as e:
        print(f"Error on {filepath}: {e}")
        pass
    return False

files = glob.glob('lcars/base/**/*.py', recursive=True)
count = 0
for f in files:
    if clean_file(f):
        count += 1

print(f'Done. Cleaned {count} files in lcars/base/')
