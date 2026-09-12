# ◤ LCARS STARFLEET LAUNCHER 🖖
# =============================================================================
# ФАЙЛ: launcher.py
# ПОСЛІДОВНІСТЬ:
# 1. Boot: чорний екран -> поява терміналу -> розгортання інтерфейсу.
# 2. Security Gate (Login): підтвердження та авторизація.
# 3. Desktop (Welcome / MSD): головний робочий простір.
# НАДІЙНІСТЬ: перехоплення будь-яких збоїв та перехід в EmergencyMode без вильотів.
# =============================================================================

from __future__ import annotations

from lcars.base.type import LCARS
from lcars.core.signal import ODN
from lcars.ui.screen.boot import LCARSBoot
from lcars.ui.screen.login import LCARSLoginScreen
from lcars.ui.screen.desktop import LCARSDesktop
from lcars.ui.screen.emergency import EmergencyScreen

class LaunchOptions(LCARS):
    def __init__(self, Arguments = None):
        super().__init__()
        self.RawArguments = Arguments or []
        self.Station = "WELCOME"
        self.FullScreen = True
        self.DebugMode = False
        self.SafeMode = False
        self.NoAudio = False
        self.DirectMode = None
        self.Parse(self.RawArguments)

    def Parse(self, ArgList):
        for Arg in ArgList:
            A = str(Arg).strip()
            if A in ("-w", "--windowed", "/w"):
                self.FullScreen = False
            elif A in ("-f", "--fullscreen", "/f"):
                self.FullScreen = True
            elif A in ("-d", "--debug", "/d"):
                self.DebugMode = True
            elif A in ("-s", "--safe", "/s"):
                self.SafeMode = True
            elif A in ("--no-audio", "/noaudio"):
                self.NoAudio = True
            elif A in ("--terminal", "-t", "/t", "--console", "-c", "/c"):
                self.DirectMode = "CONSOLE"
                self.Station = "CONSOLE"
            elif A in ("--bios", "-b", "/b"):
                self.DirectMode = "BIOS"
            elif A.startswith("--station="):
                self.Station = A.split("=", 1)[1].strip().upper()

class LCARSLauncher(LCARS):
    def __init__(self, ApplicationInstance = None, Options = None):
        super().__init__()
        HostSys = LCARS.Import("sys")
        ArgsList = HostSys.argv if HostSys and hasattr(HostSys, "argv") else []
        self.App = ApplicationInstance or LCARS.Application.instance() or LCARS.Application(ArgsList)
        self.Options = Options or LaunchOptions(ArgsList[1:])
        self.BootScreen = None
        self.LoginScreen = None
        self.DesktopScreen = None
        self.EmergencyInstance = None

        ODN.Listen("System.Phase.Login", lambda *Args: self.LaunchLogin())
        ODN.Listen("System.Phase.Desktop", lambda *Args: self.LaunchDesktop(self.Options.Station or "WELCOME"))
        ODN.Listen("System.Access.Granted", lambda *Args: self.LaunchDesktop(self.Options.Station or "WELCOME"))

        # Глобальний перехоплювач будь-яких помилок в середовищі для переходу в EmergencyMode
        if HostSys and hasattr(HostSys, "excepthook"):
            def GlobalExceptionHandler(ExcType, ExcValue, ExcTraceback):
                ErrText = f"{ExcType.__name__ if hasattr(ExcType, '__name__') else 'Error'}: {ExcValue}"
                self.LaunchEmergency(ErrText)
            HostSys.excepthook = GlobalExceptionHandler

    def ShowWidget(self, Widget, Title):
        if hasattr(Widget, "setWindowTitle"):
            Widget.setWindowTitle(Title)

        if self.Options.FullScreen:
            FramelessFlag = getattr(LCARS, "Frameless", None)
            if FramelessFlag is not None and hasattr(Widget, "setWindowFlag"):
                Widget.setWindowFlag(FramelessFlag, True)
            if hasattr(Widget, "showFullScreen"):
                Widget.showFullScreen()
            elif hasattr(Widget, "showMaximized"):
                Widget.showMaximized()
            else:
                Widget.show()
        else:
            if hasattr(Widget, "resize"):
                Widget.resize(1280, 800)
            if hasattr(Widget, "showNormal"):
                Widget.showNormal()
            else:
                Widget.show()
        LCARS.ProcessEvents()

    def LaunchBoot(self):
        try:
            self.BootScreen = LCARSBoot(LauncherRef=self)
            self.ShowWidget(self.BootScreen.widget, "LCARS 25th Century :: System Boot & Hardware Diagnostics")
        except Exception as e:
            self.LaunchEmergency(str(e))

    def LaunchLogin(self):
        try:
            self.LoginScreen = LCARSLoginScreen(LauncherRef=self)
            self.ShowWidget(self.LoginScreen.widget, "LCARS 25th Century :: Security Gate")
            if self.BootScreen and hasattr(self.BootScreen, "widget"):
                self.BootScreen.widget.hide()
        except Exception as e:
            self.LaunchEmergency(str(e))

    def LaunchDesktop(self, Station = "WELCOME"):
        try:
            TargetStation = str(Station).strip().upper() if Station and not isinstance(Station, bool) else (self.Options.Station or "WELCOME")
            if self.DesktopScreen is None:
                self.DesktopScreen = LCARSDesktop()
            self.ShowWidget(self.DesktopScreen.widget, f"LCARS 25th Century :: {TargetStation}")

            if TargetStation and hasattr(self.DesktopScreen, "Select"):
                self.DesktopScreen.Select(TargetStation)

            if self.BootScreen and hasattr(self.BootScreen, "widget"):
                self.BootScreen.widget.hide()
            if self.LoginScreen and hasattr(self.LoginScreen, "widget"):
                self.LoginScreen.widget.hide()

            ODN.Emit("System.DesktopLaunched", Station=TargetStation)
        except Exception as e:
            self.LaunchEmergency(str(e))

    def LaunchEmergency(self, ErrorMessage = "Unknown System Fault"):
        try:
            self.EmergencyInstance = EmergencyScreen()
            if hasattr(self.EmergencyInstance, "SetErrorContext"):
                self.EmergencyInstance.SetErrorContext({"error": ErrorMessage, "stage": "SYSTEM RUNTIME"})
            self.ShowWidget(self.EmergencyInstance.widget, "LCARS 25th Century :: EMERGENCY MODE")
        except Exception:
            if self.DesktopScreen is None:
                self.DesktopScreen = LCARSDesktop()
            self.ShowWidget(self.DesktopScreen.widget, "LCARS 25th Century :: RECOVERY CONSOLE")
            if hasattr(self.DesktopScreen, "Select"):
                self.DesktopScreen.Select("CONSOLE")

    def Start(self):
        if self.Options.DirectMode == "CONSOLE":
            self.LaunchDesktop("CONSOLE")
        elif self.Options.DirectMode == "BIOS":
            self.LaunchDesktop("CONSTRUCTOR")
        else:
            self.LaunchBoot()

    def Run(self):
        self.Start()
        return self.App.exec()

    def __call__(self):
        return self.Run()

Launcher = LCARSLauncher

if __name__ == "__main__":
    HostSys = LCARS.Import("sys")
    ArgsList = HostSys.argv if HostSys and hasattr(HostSys, "argv") else []
    AppInstance = LCARS.Application.instance() or LCARS.Application(ArgsList)
    LauncherInstance = LCARSLauncher(AppInstance)
    ExitCode = LauncherInstance()
    if HostSys and hasattr(HostSys, "exit"):
        HostSys.exit(ExitCode)