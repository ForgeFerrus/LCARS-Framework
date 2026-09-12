# Clean headless-capable startup copy for testing
from __future__ import annotations

import sys
import os
import logging
from pathlib import Path

project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

os.environ.setdefault("LCARS_TELEMETRY_CONSOLE", "0")

log_dir = project_root / "logs"
log_dir.mkdir(parents=True, exist_ok=True)
log_file_path = log_dir / "start_lcars_clean.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s: %(message)s',
    handlers=[logging.FileHandler(str(log_file_path), encoding='utf-8')]
)

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass

from lcars.base.types import Application, Timer
from lcars.system.initialization import TitaniumSystemInitializer


def FullSystemStartup(headless: bool = False):
    logger = logging.getLogger(__name__)

    app = Application.instance()
    if not app:
        app = Application(sys.argv)
        try:
            app.setStyle("Fusion")
            app.setQuitOnLastWindowClosed(False)
        except Exception:
            logger.debug("Could not set application style or quit behavior")

    try:
        from lcars.base.defaults import SetupFont
        SetupFont()
    except Exception:
        logger.exception("Font setup failed")

    Loading = None
    if not headless:
        try:
            from lcars.ui.loading_screen import LCARSLoadingScreen
            Loading = LCARSLoadingScreen()
            Loading.showFullScreen()
            app.processEvents()
            Loading.AddLog("◤ TITANIUM OPERATING ENVIRONMENT v44.20 INITIALIZING...")
            Loading.AddLog("──────────────────────────────────────────────────────")
        except Exception:
            logger.exception("Failed to create loading screen")

    if not headless:
        try:
            from scripts.sentinel import RunSentinelSubsystem
            app._SentinelRef = RunSentinelSubsystem()
        except Exception:
            logger.debug("Sentinel service not started")

    def ProgressCallback(step: str, pct: int):
        if Loading:
            try:
                Loading.update_status(step, pct)
                app.processEvents()
            except Exception:
                logger.debug("Loading screen update failed")

    initializer = TitaniumSystemInitializer(ProgressCallbackNode=ProgressCallback)
    if (not headless) and hasattr(initializer, "set_loading_screen") and Loading is not None:
        try:
            initializer.set_loading_screen(Loading)
        except Exception:
            logger.debug("Attaching loading screen to initializer failed")

    success = False
    try:
        success = initializer.execute()
    except Exception:
        logger.exception("Initializer execution failed")

    if success:
        if Loading:
            try:
                Loading.AddLog("◤ CORE SYSTEMS ONLINE — AUTHORIZATION REQUIRED")
                Loading.UpdateStep("AUTHORIZATION BARRIER", 100)
                Timer.singleShot(800, lambda: ShowLoginScreen(Loading))
            except Exception:
                logger.debug("Post-initialization UI steps failed")
    else:
        if Loading:
            try:
                Loading.AddLog("◤ CRITICAL: INITIALIZATION FAILED — SYSTEM HALTED")
            except Exception:
                logger.debug("Failed to notify loading screen of init failure")

    return app, Loading


def ShowLoginScreen(LoadingDisplay):
    from lcars.ui.login_screen import LCARSLoginScreen
    Login = LCARSLoginScreen()
    Login.showFullScreen()
    Application.instance().processEvents()
    try:
        LoadingDisplay.close()
    except Exception:
        pass
    Login.AuthorizedSignal.connect(lambda CrewId, L=Login: LaunchDesktop(L))
    Application.instance()._LoginRef = Login


def LaunchDesktop(LoginDisplay):
    from lcars.ui.desktop import LCARSDesktop
    Desktop = LCARSDesktop()
    Desktop.showFullScreen()
    Application.instance().processEvents()
    try:
        LoginDisplay.close()
    except Exception:
        pass
    Application.instance()._LoginRef = None
    Application.instance()._DesktopRef = Desktop


if __name__ == "__main__":
    app, loading = FullSystemStartup()
    if app:
        sys.exit(app.exec())
