# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: from pathlib import Path
# Titanium Bridge Migration: import json

project_root = str(Path(__file__).resolve().parents[1])
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from lcars.core.board_computer import BoardComputer

def main():
    bc = BoardComputer()
    print('BoardComputer instance:', type(bc).__name__)
    plan = bc.orchestrate_project(execute=False)
    print('orchestrate_project (dry-run):')
    print(json.dumps(plan, indent=2, ensure_ascii=False))

    # Try enabling auto-translate (best-effort)
    bc.enable_auto_translate(True)
    sample = 'MAIN_DISPLAY'
    translated = bc.translate_text(sample, src='en')
    print('translate_text sample ->', translated)

if __name__ == '__main__':
    main()
