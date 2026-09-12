#!/usr/bin/env python3
# LCARS Framework - Startup sequence manager
# start.py → LCARSLauncher → boot → loading → login → desktop

import sys
from pathlib import Path

# Add project root to sys.path
ProjectRoot = Path(__file__).parent.absolute()
if str(ProjectRoot) not in sys.path:
    sys.path.insert(0, str(ProjectRoot))

# Import sequence stages
from lcars.base.type import LCARS, Directive
from lcars.ui.screen.boot import LCARSBoot
from lcars.ui.screen.loading import LCARSLoading
from lcars.ui.screen.login import LCARSLogin
from lcars.base.desktop import LCARSDesktop
from lcars.system.bios import LCARSEmergencyMode

class LCARSLauncher:
    # Titanium-compliant startup launcher
    
    def __init__(self):
        AppClass = LCARS.Application
        if not AppClass:
            raise RuntimeError("QApplication (PyQt6) is not available.")
        self.App = AppClass(sys.argv)

        # Initialize fonts and theme
        from lcars.base.default import FontSetup, Palette, ContrastColor
        FontSetup()
        
        TextColor = '#FFFFFF' if ContrastColor(Palette.Background) == '#FFFFFF' else '#000000'
        self.App.setStyleSheet(f"QWidget {{ background-color: {Palette.Background}; color: {TextColor}; }}")

        StackClass = LCARS.Stacked
        if not StackClass:
            raise RuntimeError("QStackedWidget (PyQt6) is not available.")
        self.Stack = StackClass()
        
        Protocol = LCARS.Directive
        if Protocol is not None:
            self.Stack.setWindowFlag(Protocol.WindowType.FramelessWindowHint)
            self.Stack.setWindowState(Protocol.WindowState.WindowFullScreen)
        
        # Instantiate views
        self.BootView = LCARSBoot()
        self.LoadingView = LCARSLoading()
        self.EmergencyView = LCARSEmergencyMode()
        self.LoginView = LCARSLogin()
        self.DesktopView = LCARSDesktop()
        
        self.Stack.addWidget(self.BootView)      # Stage 1: Boot
        self.Stack.addWidget(self.LoadingView)   # Stage 2: Loading
        self.Stack.addWidget(self.EmergencyView) # Stage 3: Emergency Mode
        self.Stack.addWidget(self.LoginView)     # Stage 4: Login
        self.Stack.addWidget(self.DesktopView)   # Stage 5: Desktop
        
        # Connect signals for transitions
        self.ConnectSignals()
        
        # Start from Boot view
        self.ShowBoot()
        
    def ConnectSignals(self):
        def BindSignal(SignalRef, HandlerFunc):
            if not SignalRef:
                return
            if hasattr(SignalRef, 'Connect'):
                SignalRef.Connect(HandlerFunc)
                return
            if hasattr(SignalRef, 'connect'):
                SignalRef.connect(HandlerFunc)
                return

        # Boot completed -> Loading
        if hasattr(self.BootView, 'boot_complete'):
            BindSignal(getattr(self.BootView, 'boot_complete'), self.ShowLoading)

        # Loading finished -> Login or Emergency
        if hasattr(self.LoadingView, 'loading_finished'):
            BindSignal(getattr(self.LoadingView, 'loading_finished'), self.OnLoadingFinished)
            
        # Emergency Mode -> Reboot (returns to loading view)
        if hasattr(self.EmergencyView, 'btn_override'):
            self.EmergencyView.btn_override.clicked.connect(self.TriggerColdReboot)
            
        # Login successful -> Desktop  
        if hasattr(self.LoginView, 'login_successful'):
            BindSignal(getattr(self.LoginView, 'login_successful'), self.ShowDesktop)
    
    def ShowLoading(self):
        print("TRANSITIONING TO LOADING STAGE", flush=True)
        self.Stack.setCurrentWidget(self.LoadingView)
        self.Stack.show()
        
    def ShowBoot(self):
        print("TRANSITIONING TO BOOT STAGE", flush=True)
        self.Stack.setCurrentWidget(self.BootView)
        self.Stack.show()
    
    def ShowLogin(self):
        print("TRANSITIONING TO LOGIN STAGE", flush=True)
        self.Stack.setCurrentWidget(self.LoginView)

    def OnLoadingFinished(self, Success: bool, Reason: str = ""):
        if Success:
            self.ShowLogin()
        else:
            self.ShowEmergencyMode(Reason or "System integrity check failed during loading.")

    def ShowEmergencyMode(self, Reason: str = ""):
        print("TRANSITIONING TO EMERGENCY VIEW IN STACK", flush=True)
        if hasattr(self.EmergencyView, 'SetErrorContext'):
            self.EmergencyView.SetErrorContext({
                "error": Reason or "Unknown system fault",
                "stage": "LOADING",
                "details": []
            })
        self.Stack.setCurrentWidget(self.EmergencyView)

    def TriggerColdReboot(self):
        print("REBOOTING SYSTEM FROM EMERGENCY PROTOCOL...", flush=True)
        from lcars.base.default import Palette, FontStyle
        
        # Reset LoadingView state
        self.LoadingView.sequence_active = False
        self.LoadingView.step_idx = 0
        
        # Re-initialize loading labels and styling (remove red alert colors)
        if hasattr(self.LoadingView, 'step_lbl') and hasattr(self.LoadingView.step_lbl, 'Widget'):
            self.LoadingView.step_lbl.Widget.setText("INITIALIZING INTEGRITY CHECK...")
            self.LoadingView.step_lbl.Widget.setStyleSheet(f"color: {Palette.Buttons[-2]}; {FontStyle(28, 'normal')}; background: transparent;")
        
        if hasattr(self.LoadingView, 'dots_lbl') and hasattr(self.LoadingView.dots_lbl, 'Widget'):
            self.LoadingView.dots_lbl.Widget.setText("● ● ● ● ● ● ●")
            self.LoadingView.dots_lbl.Widget.setStyleSheet(f"color: {Palette.Buttons[-2]}; {FontStyle(22, 'normal')}; background: transparent;")
            
        # Reset panel colors to standard atmospheric
        if hasattr(self.LoadingView, 'elbow_l') and hasattr(self.LoadingView.elbow_l, 'Widget'):
            self.LoadingView.elbow_l.Widget.setStyleSheet(f"background-color: {self.LoadingView.GetColor(0)}; border-top-left-radius: 40px;")
        if hasattr(self.LoadingView, 'title_bar'):
            self.LoadingView.title_bar.setStyleSheet(f"background-color: {self.LoadingView.GetColor(1)}; border-radius: 4px;")
        if hasattr(self.LoadingView, 'elbow_r') and hasattr(self.LoadingView.elbow_r, 'Widget'):
            self.LoadingView.elbow_r.Widget.setStyleSheet(f"background-color: {self.LoadingView.GetColor(2)}; border-top-right-radius: 25px;")
        if hasattr(self.LoadingView, 'footer_l') and hasattr(self.LoadingView.footer_l, 'Widget'):
            self.LoadingView.footer_l.Widget.setStyleSheet(f"background-color: {self.LoadingView.GetColor(3)}; border-bottom-left-radius: 40px;")
        if hasattr(self.LoadingView, 'footer_main'):
            self.LoadingView.footer_main.setStyleSheet(f"background-color: {self.LoadingView.GetColor(4)}; border-radius: 4px;")
            
        # Start the loading sequence again
        self.ShowLoading()

    def ShowDesktop(self):
        print("TRANSITIONING TO DESKTOP STAGE", flush=True)
        if not hasattr(self, 'DesktopView') or self.DesktopView is None:
            self.DesktopView = LCARSDesktop()
            self.Stack.addWidget(self.DesktopView)
            if hasattr(self.DesktopView, 'system_lock'):
                if hasattr(self.DesktopView.system_lock, 'connect'):
                    self.DesktopView.system_lock.connect(self.ShowLogin)
                elif hasattr(self.DesktopView.system_lock, 'Connect'):
                    self.DesktopView.system_lock.Connect(self.ShowLogin)
            if hasattr(self.DesktopView, 'system_logout'):
                if hasattr(self.DesktopView.system_logout, 'connect'):
                    self.DesktopView.system_logout.connect(self.ShowLogin)
                elif hasattr(self.DesktopView.system_logout, 'Connect'):
                    self.DesktopView.system_logout.Connect(self.ShowLogin)
        self.Stack.setCurrentWidget(self.DesktopView)
    
    def Run(self):
        return self.App.exec()

def StartCacheSentinel():
    import subprocess
    SentinelPath = ProjectRoot / "tools" / "cache_sentinel.py"
    if SentinelPath.exists():
        subprocess.Popen([sys.executable, str(SentinelPath)], 
                         creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0)

def Run():
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--emergency':
        from lcars.system.bios import RunEmergencyMode
        return RunEmergencyMode()
    else:
        StartCacheSentinel()
        Launcher = LCARSLauncher()
        return Launcher.Run()

run = Run

if __name__ == "__main__":
    sys.exit(Run())
