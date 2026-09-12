import os
import re

def cleanup_triangles():
    print(f"Current working directory: {os.getcwd()}")
    patterns = [
        (r'◢ ', ''),
        (r'◢', '')
    ]
    
    # Target directories
    dirs = ['lcars']
    
    for d in dirs:
        for root, _, files in os.walk(d):
            for file in files:
                if file.endswith('.py'):
                    path = os.path.join(root, file)
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    new_content = content
                    for p, r in patterns:
                        new_content = re.sub(p, r, new_content)
                    
                    if new_content != content:
                        print(f"Cleaning triangles in {path}")
                        with open(path, 'w', encoding='utf-8') as f:
                            f.write(new_content)

if __name__ == "__main__":
    cleanup_triangles()
    cleanup_triangles()
