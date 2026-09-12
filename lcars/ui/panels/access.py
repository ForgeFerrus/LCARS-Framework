# SYSTEM ACCESS PANEL
# LCARS Framework :: панель керування живленням та сесією
# Призначення: управління живленням ПК та контроль сесії + живий моніторинг системи.
# НЕ дублює desktop — навігація по панелях вже є на Desktop.

import sys
import time
import subprocess
from pathlib import Path
from datetime import datetime
import psutil
from lcars.base.component import LCARSButton, LCARSLabel, LCARSElbow, LCARSBar, LCARSIndicator
from lcars.base.interface import Segment, DataBlock
from lcars.base.default import Palette
from lcars.base.type import LCARS
from lcars.base.animation import DiagnosticGrid
from lcars.core.signal import ODN

def GetSystemStats() -> dict:
    stats = {}
    stats["cpu"]  = f"{psutil.cpu_percent(interval=0.1):.1f}%"
    mem  = psutil.virtual_memory()
    stats["ram"]  = f"{mem.used // (1024**3):.1f} / {mem.total // (1024**3):.1f} GB  ({mem.percent:.0f}%)"
    DiskRoot = "/" if not hasattr(Path, "anchor") else Path.cwd().anchor
    disk = psutil.disk_usage(str(DiskRoot))
    stats["disk"] = f"{disk.used // (1024**3):.0f} / {disk.total // (1024**3):.0f} GB  ({disk.percent:.0f}%)"
    secs = int(time.time() - psutil.boot_time())
    stats["uptime"] = f"{secs // 3600}h {(secs % 3600) // 60}m"
    return stats

class ConfirmDialog(Segment):
    def __init__(self, message: str, on_confirm, parent_widget=None, danger: bool = True):
        super().__init__(Parent=parent_widget)
        self.on_confirm = on_confirm
        self.parent = parent_widget

        accent = "#CC3300" if danger else "#FF9900"
        bg     = "#0d0000" if danger else "#0d0800"

        # Оверлей
        self.widget.setStyleSheet("background-color: rgba(0, 0, 0, 180);")
        if parent_widget:
            self.widget.setGeometry(parent_widget.geometry())
        self.widget.hide()

        # Панель діалогу
        self.panel = Segment(Parent=self.widget)
        self.panel.widget.setFixedSize(560, 260)
        self.panel.widget.setStyleSheet(
            f"background-color: {bg}; border: 3px solid {accent}; border-radius: 4px;"
        )

        root = self.panel.Vertical(24, 20, 24, 20, 14)

        head_row = Segment(Parent=self.panel.widget)
        head_layout = head_row.Horizontal(0, 0, 0, 0, 12)

        warn_pill = LCARSBar(Type="rect", Color=accent, Width=8, Height=44, Parent=head_row.widget)
        head_layout.addWidget(warn_pill.widget)

        warn_lbl = LCARSLabel("⚠  ПІДТВЕРДІТЬ ДІЮ  //  CONFIRM ACTION", Color=accent, FontSize=16, Parent=head_row.widget)
        head_layout.addWidget(warn_lbl.widget)
        root.addWidget(head_row.widget)

        sep = LCARSBar(Type="rect", Color=accent, Height=2, Parent=self.panel.widget)
        root.addWidget(sep.widget)

        msg_lbl = LCARSLabel(message, Color="#DDDDDD", FontSize=18, Parent=self.panel.widget)
        if hasattr(msg_lbl.widget, "setWordWrap"):
            msg_lbl.widget.setWordWrap(True)
        root.addWidget(msg_lbl.widget)

        root.addStretch(1)

        btn_row = Segment(Parent=self.panel.widget)
        btn_layout = btn_row.Horizontal(0, 0, 0, 0, 16)

        self.confirm_btn = LCARSButton("ПІДТВЕРДИТИ  /  CONFIRM", Color=accent, Type="soft", Width=240, Height=50, Parent=btn_row.widget)
        if hasattr(self.confirm_btn, "Clicked"):
            self.confirm_btn.Clicked.Connect(self.DoConfirm)
        elif hasattr(self.confirm_btn, "clicked"):
            self.confirm_btn.clicked.connect(self.DoConfirm)
        btn_layout.addWidget(self.confirm_btn.widget, 1)

        self.cancel_btn = LCARSButton("СКАСУВАТИ  /  ABORT", Color=Palette.Buttons[0], Type="soft", Width=200, Height=50, Parent=btn_row.widget)
        if hasattr(self.cancel_btn, "Clicked"):
            self.cancel_btn.Clicked.Connect(self.DoCancel)
        elif hasattr(self.cancel_btn, "clicked"):
            self.cancel_btn.clicked.connect(self.DoCancel)
        btn_layout.addWidget(self.cancel_btn.widget, 1)

        root.addWidget(btn_row.widget)

    def show(self):
        if self.parent:
            pw = self.parent.width()
            ph = self.parent.height()
            self.widget.setGeometry(0, 0, max(600, pw), max(400, ph))
            px = max(0, (pw - self.panel.widget.width()) // 2)
            py = max(0, (ph - self.panel.widget.height()) // 2)
            self.panel.widget.move(px, py)
        self.widget.show()
        self.widget.raise_()

    def DoConfirm(self):
        self.widget.hide()
        if callable(self.on_confirm):
            self.on_confirm()

    def DoCancel(self):
        self.widget.hide()

class SystemAccess(Segment):
    POWER_ACTIONS = [
        ("SHUTDOWN",  "shutdown",  True),
        ("RESTART",   "restart",   True),
        ("SLEEP",     "sleep",     False),
        ("HIBERNATE", "hibernate", False),
    ]
    SESSION_ACTIONS = [
        ("LOCK SESSION",  "lock_session"),
        ("SWITCH USER",   "switch_user"),
        ("BIOS / UEFI",   "bios"),
    ]

    def __init__(self, DesktopNodeRef=None, ParentNode=None):
        super().__init__(Parent=ParentNode)
        self.DesktopNode = DesktopNodeRef
        self.widget.setStyleSheet("background-color: #000000;")
        self.LiveLabels = {}
        self.Build()

        self.UpdateTimer = LCARS.Timer(self.widget)
        self.UpdateTimer.timeout.connect(self.UpdateMetrics)
        self.UpdateTimer.start(2000)

        self.ClockTimer = LCARS.Timer(self.widget)
        self.ClockTimer.timeout.connect(self.UpdateClock)
        self.ClockTimer.start(1000)

        self.confirm_dialog = None

    def Build(self):
        root = self.Vertical(16, 16, 16, 16, 12)

        # HEADER
        head = Segment(Parent=self.widget)
        head_layout = head.Horizontal(0, 0, 0, 0, 8)

        head_bar = LCARSBar(Type="rect", Color=Palette.Buttons[1], Height=50, Parent=head.widget)
        inner = LCARS.Horizontal(head_bar.widget)
        inner.setContentsMargins(16, 0, 16, 0)
        title_lbl = LCARSLabel("SYSTEM ACCESS  //  POWER & SESSION CONTROL", Color="#000000", FontSize=20, Parent=head_bar.widget)
        inner.addWidget(title_lbl.widget)
        head_layout.addWidget(head_bar.widget, 1)

        accent_r = LCARSBar(Type="rect", Color=Palette.Buttons[2], Width=60, Height=50, Parent=head.widget)
        head_layout.addWidget(accent_r.widget)
        root.addWidget(head.widget)

        # BODY
        body = Segment(Parent=self.widget)
        body_layout = body.Horizontal(0, 0, 0, 0, 20)

        # POWER
        power_col = Segment(Parent=body.widget)
        power_layout = power_col.Vertical(0, 0, 0, 0, 8)
        
        power_head = LCARSIndicator(Text="POWER CONTROL NODE", Type="rect-left", Color=Palette.Buttons[0], FontSize=13, Parent=power_col.widget)
        power_layout.addWidget(power_head.widget)
        
        for label, action_key, is_danger in self.POWER_ACTIONS:
            btn = LCARSButton(label, Type="soft-left", Color="#CC3300" if is_danger else Palette.Buttons[1], Width=240, Height=48, Parent=power_col.widget)
            btn.Clicked.Connect(lambda chk=False, a=action_key, d=is_danger: self.AskConfirm(a, d))

        power_layout.addSpacing(15)
        
        sess_head = LCARSIndicator(Text="ACTIVE SESSION", Type="rect-left", Color=Palette.Buttons[3], FontSize=13, Parent=power_col.widget)
        power_layout.addWidget(sess_head.widget)
        
        for label, action_key in self.SESSION_ACTIONS:
            btn = LCARSButton(label, Type="soft-left", Color=Palette.Buttons[4], Width=240, Height=44, Parent=power_col.widget)
            btn.Clicked.Connect(lambda chk=False, a=action_key: self.ExecuteAction(a))
            power_layout.addWidget(btn.widget)
        power_layout.addStretch()
        body_layout.addWidget(power_col.widget)

        sep = LCARSBar(Type="rect", Color=Palette.Neutral[1], Width=3, Parent=body.widget)
        body_layout.addWidget(sep.widget)

        # MONITOR
        monitor_col = Segment(Parent=body.widget)
        monitor_layout = monitor_col.Vertical(0, 0, 0, 0, 10)
        
        mon_head = LCARSIndicator(Text="SYSTEM HARDWARE TELEMETRY", Type="rect", Color=Palette.Buttons[0], FontSize=13, Parent=monitor_col.widget)
        monitor_layout.addWidget(mon_head.widget)

        metrics = [
            ("cpu",    "CORE PROCESSOR",   Palette.Buttons[1]),
            ("ram",    "NEURAL MEMORY",     Palette.Buttons[2]),
            ("disk",   "STORAGE ARRAY",       Palette.Buttons[3]),
            ("uptime", "CONTINUOUS UPTIME",     Palette.Buttons[4]),
        ]
        
        grid_row1 = Segment(Parent=monitor_col.widget)
        grid_layout1 = grid_row1.Horizontal(0, 0, 0, 0, 15)
        grid_row2 = Segment(Parent=monitor_col.widget)
        grid_layout2 = grid_row2.Horizontal(0, 0, 0, 0, 15)

        for i, (key, label, color) in enumerate(metrics):
            block = DataBlock(Title=label, Value="—", Color=color, Parent=grid_row1.widget if i < 2 else grid_row2.widget)
            self.LiveLabels[key] = block
            if i < 2:
                grid_layout1.addWidget(block.widget, 1)
            else:
                grid_layout2.addWidget(block.widget, 1)

        monitor_layout.addWidget(grid_row1.widget)
        monitor_layout.addWidget(grid_row2.widget)
        
        monitor_layout.addSpacing(10)
        diag = DiagnosticGrid(Parent=monitor_col.widget, Color=Palette.Buttons[2])
        diag.widget.setMinimumHeight(150)
        monitor_layout.addWidget(diag.widget, 1)

        monitor_layout.addStretch()
        body_layout.addWidget(monitor_col.widget, 2)
        root.addWidget(body.widget, 1)

        # FOOTER
        foot = Segment(Parent=self.widget)
        foot_layout = foot.Horizontal(0, 0, 0, 0, 4)

        foot_bar = LCARSBar(Type="rect", Color=Palette.Buttons[0], Height=30, Parent=foot.widget)
        foot_inner = LCARS.Horizontal(foot_bar.widget)
        foot_inner.setContentsMargins(14, 0, 14, 0)
        self.FooterClock = LCARSLabel("STARDATE: --  //  00:00:00", Color="#000000", FontSize=11, Parent=foot_bar.widget)
        foot_inner.addWidget(self.FooterClock.widget)
        foot_inner.addStretch()

        foot_layout.addWidget(foot_bar.widget, 1)
        root.addWidget(foot.widget)

    def UpdateMetrics(self):
        stats = GetSystemStats()
        for key, lbl in self.LiveLabels.items():
            if hasattr(lbl, 'SetValue'):
                lbl.SetValue(stats.get(key, "N/A"))

    def UpdateClock(self):
        now = datetime.now()
        self.FooterClock.SetText(f"STARDATE: {now.strftime('%Y.%m.%d')}  //  {now.strftime('%H:%M:%S')}")

    def AskConfirm(self, action_key: str, danger: bool = True):
        messages = {
            "shutdown":  "INITIATE FULL SYSTEM SHUTDOWN?\nAll unsaved data will be lost.",
            "restart":   "INITIATE SYSTEM RESTART?\nAll unsaved data will be lost.",
            "sleep":     "ENTER SLEEP MODE?\nSystem will suspend to RAM.",
            "hibernate": "INITIATE HIBERNATION?\nSystem will suspend to disk.",
        }
        msg = messages.get(action_key, f"EXECUTE: {action_key.upper()}?")
        
        if self.confirm_dialog:
            self.confirm_dialog.widget.deleteLater()
            
        self.confirm_dialog = ConfirmDialog(msg, lambda a=action_key: self.ExecuteAction(a), self.widget, danger)
        self.confirm_dialog.show()

    def ExecuteAction(self, action_key: str):
        if action_key == "bios":
            ODN.Emit("System.Phase.Bios")
            return
        Cmd = ""
        if sys.platform.startswith("win"):
            Cmd = {
                "shutdown": "shutdown /s /t 0",
                "restart": "shutdown /r /t 0",
                "sleep": "rundll32.exe powrprof.dll,SetSuspendState 0,1,0",
                "hibernate": "shutdown /h",
                "lock_session": "rundll32.exe user32.dll,LockWorkStation",
                "switch_user": "tsdiscon",
            }.get(action_key, f"echo Unknown action: {action_key}")
        elif sys.platform.startswith("linux"):
            Cmd = {
                "shutdown": "systemctl poweroff",
                "restart": "systemctl reboot",
                "sleep": "systemctl suspend",
                "hibernate": "systemctl hibernate",
                "lock_session": "loginctl lock-session",
                "switch_user": "dm-tool switch-to-greeter",
            }.get(action_key, f"echo Unknown action: {action_key}")
        
        self.FooterClock.SetText(f"COMMAND QUEUE: {action_key.upper()}")
        if Cmd:
            subprocess.Popen(Cmd, shell=True)

if __name__ == "__main__":
    app = CreateApplication(sys.argv)
    if app:
        panel = SystemAccess()
        Host = LCARS.Segment()
        Host.widget.setGeometry(100, 100, 1100, 750)
        Host.Add(Host.Vertical(), panel)
        Host.widget.show()
        sys.exit(app.exec())
