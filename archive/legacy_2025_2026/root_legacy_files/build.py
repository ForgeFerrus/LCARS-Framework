from pathlib import Path
import sys

project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from lcars.ui.screen.loading import LCARSLoading, RunLoadingPreview


# Compatibility entrypoint: loading screen lives in lcars/ui/screen/loading.py.
if __name__ == "__main__":
    raise SystemExit(RunLoadingPreview())
