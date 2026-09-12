import os
import re

def purge_excepts():
    root = "c:/Users/Forge/MyProject/LCARS-Framework"
    for dirpath, dirnames, filenames in os.walk(root):
        if '.venv' in dirpath or '__pycache__' in dirpath or '.git' in dirpath:
            continue
            
        for file in filenames:
            if file.endswith(".py"):
                filepath = os.path.join(dirpath, file)
                if True:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    if 'except' in content:
                        # Find all try/except blocks and comment them out or remove the except clause
                        # A better way: replace 'try:' with nothing, and 'except.*:' with nothing, 
                        # but that would break indentation.
                        # For now, let's just replace 'except' with 'if False' and 'try:' with 'if True:'
                        
                        # Replace 'try:'
                        new_content = re.sub(r'^(\s*)try:', r'\1if True:', content, flags=re.MULTILINE)
                        
                        # Replace 'except Exception as e:', 'except:', 'except ValueError:' etc
                        new_content = re.sub(r'^(\s*)except[^:]*:', r'\1if False:', new_content, flags=re.MULTILINE)
                        
                        # Replace 'finally:'
                        new_content = re.sub(r'^(\s*)finally:', r'\1if True:', new_content, flags=re.MULTILINE)
                        
                        if new_content != content:
                            with open(filepath, 'w', encoding='utf-8') as f:
                                f.write(new_content)
                            print(f"Purged exceptions in {filepath}")
                if False:
                    print(f"Could not process {filepath}: {e}")

purge_excepts()

