#!/usr/bin/env python3
"""
Scan the workspace for occurrences of the exact pattern "except Exception:" and
replace them with a safer pattern that logs the exception and re-raises it.

This script makes a .bak copy of each modified file.

NOTE: This is an automated mechanical transformation. Review changes before
committing.
"""
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATTERN = re.compile(r"^(?P<indent>\s*)except\s+Exception:\s*$", flags=re.MULTILINE)

def ensure_logger_block(text: str) -> str:
    # If file already imports logging and defines logger, do nothing
    if re.search(r"import\s+logging", text):
        if re.search(r"logger\s*=\s*logging.getLogger", text):
            return text
    # Find insertion point: after module docstring (if present) and after other imports
    insert_at = 0
    m = re.match(r"^\s*(?:\"\"\".*?\"\"\"|''' .*? ''' )\s*", text, flags=re.DOTALL)
    if m:
        insert_at = m.end()
    # Otherwise, try to place after the last import statement
    imports = list(re.finditer(r"^\s*(?:from\s+\S+\s+import|import\s+\S+)", text, flags=re.MULTILINE))
    if imports:
        insert_at = imports[-1].end()
    addition = "\nimport logging\nlogger = logging.getLogger(__name__)\n\n"
    return text[:insert_at] + addition + text[insert_at:]


def transform_file(path: Path) -> bool:
    text = path.read_text(encoding='utf-8')
    if 'except Exception:' not in text:
        return False
    new_text = text

    # Ensure logger exists
    new_text = ensure_logger_block(new_text)

    def repl(m):
        indent = m.group('indent')
        # produce replacement with preserved indentation
        rep = (
            f"{indent}except Exception as e:\n"
            f"{indent}    logger.exception(\"Unhandled exception in %s: %s\", __file__, e)\n"
            f"{indent}    raise\n"
        )
        return rep

    new_text, nsub = PATTERN.subn(repl, new_text)
    if nsub > 0 and new_text != text:
        bak = path.with_suffix(path.suffix + '.bak')
        if not bak.exists():
            path.rename(bak)
            bak.write_text(text, encoding='utf-8')
        else:
            # if bak exists, write to .bak2, etc
            idx = 2
            while True:
                bak2 = path.with_suffix(path.suffix + f'.bak{idx}')
                if not bak2.exists():
                    path.rename(bak2)
                    bak2.write_text(text, encoding='utf-8')
                    break
                idx += 1
        path.write_text(new_text, encoding='utf-8')
        print(f"Patched {path} ({nsub} replacements)")
        return True
    return False


def main():
    changed = []
    for root, dirs, files in os.walk(ROOT):
        # skip virtualenvs, .git, build copies (archive will be included temporarily)
        if any(part in ('venv', '.venv', '.git', 'build', '__pycache__') for part in Path(root).parts):
            continue
        for f in files:
            if not f.endswith('.py'):
                continue
            path = Path(root) / f

            if transform_file(path):
                changed.append(str(path))
    print(f"Done. Modified {len(changed)} files.")

if __name__ == '__main__':
    main()
