# ◤ TITANIUM LCARS :: CONTROL MASTER LAUNCHER 🖖
# =============================================================================
# ФАЙЛ: control.py
# ПРИЗНАЧЕННЯ: Головна точка входу для автономного застосунку LCARS Control (CCX Desktop Hub).
# ЗАПУСК: py -3.14 control.py
# СТАНДАРТ: Titanium LCARS (Zero-Direct-Imports, Zero-Except, Zero-Underscores, Strict PascalCase).
# =============================================================================

from lcars.base.type import LCARS

def LaunchControlApplication():
    SysModule = LCARS.Import("sys")
    if hasattr(SysModule.stdout, "reconfigure"):
        SysModule.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(SysModule.stderr, "reconfigure"):
        SysModule.stderr.reconfigure(encoding="utf-8", errors="replace")

    print("=" * 76, flush=True)
    print("◤ LAUNCHING LCARS CONTROL // CCX DESKTOP MASTER HUB 🖖", flush=True)
    print("============================================================================", flush=True)

    # Reliable local-first cockpit. Keep the legacy LCARS gateway available
    # behind the original launcher, while making the default path usable.
    LocalPanelModule = LCARS.Import("programs.Control.local_panel")
    if LocalPanelModule and hasattr(LocalPanelModule, "launch"):
        SysModule.exit(LocalPanelModule.launch())

    BaseApp = LCARS.Application
    ArgList = getattr(SysModule, "argv", [])
    AppInstance = BaseApp.instance() if hasattr(BaseApp, "instance") else None
    if AppInstance is None and callable(BaseApp):
        AppInstance = BaseApp(ArgList)

    ControlModule = LCARS.Import("programs.Control.app")
    ControlWindow = ControlModule.LCARSControlApp()
    ControlWindow.show()

    print("✓ LCARS Control Station operational // Maximized Viewport Active.", flush=True)
    if SysModule and hasattr(SysModule, "exit"):
        ExitCode = AppInstance.exec_() if hasattr(AppInstance, "exec_") else AppInstance.exec()
        SysModule.exit(ExitCode)

LaunchControlApplication()
