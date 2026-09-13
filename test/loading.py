import sys
from pathlib import Path

projectRoot = Path(__file__).resolve().parent.parent
if str(projectRoot) not in sys.path:
    sys.path.insert(0, str(projectRoot))

from lcars.base.type import LCARS
from lcars.ui.screen.loading import LCARSLoading

def run():
    cls = LCARS.Application
    app = cls(sys.argv)
    
    loading = LCARSLoading()
    loading.loadingFinished.Connect(lambda success: print(f"LOADING FINISHED: {success}", flush=True))
    loading.show()
    
    # Let's run a timer to shut down the app after 4 seconds
    timer = LCARS.Timer(loading)
    timer.singleShot(4000, app.quit)
    
    print("RUNNING APP", flush=True)
    app.exec()

if __name__ == "__main__":
    run()
