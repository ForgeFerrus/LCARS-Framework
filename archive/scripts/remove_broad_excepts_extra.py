#!/usr/bin/env python3
"""
Find both `except Exception:` and `except Exception as <name>:` and replace
with a pattern that logs the exception and re-raises it.

This is mechanical — review changes before committing.
"""
import re
from pathlib import Path
import os

ROOT = Path(__file__).resolve().parents[1]
PAT = re.compile(r"^(?P<indent>\s*)except\s+Exception(?:\s+as\s+(?P<name>\w+))?:\s*$", flags=re.MULTILINE)


def ensure_logger(text: str) -> str:
    if 'import logging' in text and 'logger = logging.getLogger' in text:
        return text
    # Find last import
    imports = list(re.finditer(r"^\s*(?:from\s+\S+\s+import|import\s+\S+)", text, flags=re.MULTILINE))
    insert_at = 0
    if imports:
        insert_at = imports[-1].end()
    addition = "\nimport logging\nlogger = logging.getLogger(__name__)\n\n"
    return text[:insert_at] + addition + text[insert_at:]


def transform(path: Path) -> bool:
    text = path.read_text(encoding='utf-8')
    if 'except Exception' not in text:
        return False
    new_text = ensure_logger(text)

    def repl(m):
        indent = m.group('indent')
        name = m.group('name') or 'e'
        return (
            f"{indent}except Exception as {name}:\n"
            f"{indent}    logger.exception(\"Unhandled exception in %s\", __file__)\n"
            f"{indent}    raise\n"
        )

    new_text, n = PAT.subn(repl, new_text)
    if n:
        bak = path.with_suffix(path.suffix + '.bak')
        if not bak.exists():
            path.rename(bak)
            bak.write_text(text, encoding='utf-8')
        else:
            idx = 2
            while True:
                bak2 = path.with_suffix(path.suffix + f'.bak{idx}')
                if not bak2.exists():
                    path.rename(bak2)
                    bak2.write_text(text, encoding='utf-8')
                    break
                idx += 1
        path.write_text(new_text, encoding='utf-8')
        print(f"Patched {path} ({n} replacements)")
        return True
    return False


def main():
    changed = []
    for root, dirs, files in os.walk(ROOT):
        if any(part in ('venv', '.venv', '.git', 'build', '__pycache__') for part in Path(root).parts):
            continue
        for f in files:
            if not f.endswith('.py'):
                continue
            p = Path(root) / f
            try:
                if transform(p):
                    changed.append(str(p))
            except Exception as e:
                logger.exception("Unhandled exception in %s", __file__)
                raise

                print(f"Error processing {p}: {e}")
    print(f"Done. Modified {len(changed)} files.")

if __name__ == '__main__':
    main()
