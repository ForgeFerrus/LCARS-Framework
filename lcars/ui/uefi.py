# ◤ LCARS UEFI CONFIGURATION INTERFACE
# ОПИС: Екран налаштувань UEFI з LCARS-інтерфейсом.
# Архітектура: LCARS namespace — Widget, Vertical, Horizontal, Grid, Bar, Button, Label, Elbow.
#              lcars.base.default — Palette.
#              lcars.base.component — LCARSButton, LCARSBar, LCARSLabel, LCARSElbow.
# Стандарт: Titanium (Zero-Except, Zero-Underscores, PascalCase, Pure LCARS).
# ─────────────────────────────────────────────────────────────────────────────

import sys
from pathlib import Path

project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from lcars.base.type import LCARS
from lcars.base.default import Palette
from lcars.base.component import LCARSButton, LCARSLabel, LCARSBar, LCARSElbow


# Секція UEFI — контейнер з заголовком та опціями
class LCARSSection:
    def __init__(self, title, color, Parent=None):
        self.widget = LCARS.Widget()
        self.widget.setStyleSheet(
            f"background-color: rgba(47, 55, 73, 0.5); border: 2px solid {color}; border-radius: 20px;"
        )
        if Parent is not None:
            self.widget.setParent(Parent)

        self.section_layout = LCARS.Vertical(self.widget)
        self.section_layout.setContentsMargins(20, 15, 20, 15)
        self.section_layout.setSpacing(12)

        title_label = LCARSLabel(
            Text=f"\u25e2 {title}", Color=color, FontSize=16, Parent=self.widget
        )
        self.section_layout.addWidget(title_label.widget)

    def AddOption(self, label, widget, color):
        row = LCARS.Widget()
        row_layout = LCARS.Horizontal(row)
        row_layout.setContentsMargins(0, 5, 0, 5)

        label_widget = LCARSLabel(
            Text=label, Color=color, FontSize=13, Parent=row
        )
        row_layout.addWidget(label_widget.widget)
        row_layout.addStretch()

        if hasattr(widget, "widget"):
            row_layout.addWidget(widget.widget)
        else:
            row_layout.addWidget(widget)

        self.section_layout.addWidget(row)


# Головний клас екрану UEFI
class UEFI:
    def __init__(self, Parent=None, bios_instance=None):
        self.widget = LCARS.Widget()
        self.Layout = LCARS.Vertical(self.widget)
        self.bios = bios_instance if bios_instance is not None else Parent
        self.current_era = 25
        self.SystemInfo = {}
        self.LoadSystemInfo()
        self.BuildUi()

    def LoadSystemInfo(self):
        import platform
        self.SystemInfo = {
            "platform": platform.system(),
            "platform_release": platform.release(),
            "platform_version": platform.version(),
            "architecture": platform.machine(),
            "hostname": platform.node(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
        }
        if self.bios:
            self.SystemInfo["processor"] = self.bios.Hardware.Cpu
            self.SystemInfo["memory_total"] = str(self.bios.Hardware.MemoryTotal) + " MB"

    def BuildUi(self):
        MainLayout = self.Layout
        MainLayout.setContentsMargins(15, 15, 15, 15)
        MainLayout.setSpacing(10)

        # Header: elbow + bar + elbow
        TopFrame = LCARS.Horizontal()
        TopFrame.setSpacing(10)

        self.ElbowTopLeft = LCARSElbow(
            Direction="top-left", Color=Palette.Buttons[0],
            Width=180, Height=60, Parent=self.widget
        )
        TopFrame.addWidget(self.ElbowTopLeft.widget)

        self.HeaderBar = LCARSBar(
            Parent=self.widget, Color=Palette.Buttons[0], Height=60
        )
        TitleLayout = LCARS.Horizontal(self.HeaderBar.widget)
        TitleLayout.setContentsMargins(20, 0, 20, 0)

        title = LCARSLabel(
            Text="SYSTEM CONFIGURATION // UEFI v25.0",
            Color="#000000", FontSize=24, Parent=self.HeaderBar.widget
        )
        TitleLayout.addWidget(title.widget)
        TitleLayout.addStretch()
        TopFrame.addWidget(self.HeaderBar.widget, 1)

        self.HeaderElbowRight = LCARSElbow(
            Direction="top-right", Color=Palette.Buttons[0],
            Width=60, Height=60, Parent=self.widget
        )
        TopFrame.addWidget(self.HeaderElbowRight.widget)
        MainLayout.addLayout(TopFrame)

        # Body: menu + settings
        BodyFrame = LCARS.Horizontal()
        BodyFrame.setSpacing(15)

        menu = self.CreateMenu()
        BodyFrame.addWidget(menu.widget)

        self.settings_chamber = LCARS.Chamber(self.widget)
        self.CreateSettingsPages()
        BodyFrame.addWidget(self.settings_chamber, 1)
        MainLayout.addLayout(BodyFrame, 1)

        # Footer
        FooterFrame = LCARS.Horizontal()
        FooterFrame.setSpacing(10)

        self.ElbowBottomLeft = LCARSElbow(
            Direction="bottom-left", Color=Palette.Buttons[0],
            Width=180, Height=30, Parent=self.widget
        )
        FooterFrame.addWidget(self.ElbowBottomLeft.widget)

        self.FooterBar = LCARSBar(
            Parent=self.widget, Color=Palette.Buttons[0], Height=30
        )
        FooterFrame.addWidget(self.FooterBar.widget, 1)
        MainLayout.addLayout(FooterFrame)

    def CreateMenu(self):
        menu = LCARS.Widget()
        menu.setFixedWidth(180)

        menu_layout = LCARS.Vertical(menu)
        menu_layout.setContentsMargins(0, 0, 0, 0)
        menu_layout.setSpacing(8)

        menu_items = [
            ("SYSTEM INFO", 0),
            ("BOOT ORDER", 1),
            ("SECURITY", 2),
            ("PERIPHERAL", 3),
            ("STORAGE", 4),
            ("POWER", 5),
            ("DIAGNOSTIC", 6),
            ("SAVE & EXIT", 7),
        ]

        self.menu_buttons = []
        for label, index in menu_items:
            color = Palette.Buttons[index % len(Palette.Buttons)]
            btn = LCARSButton(
                Text=label, Color=color, Type="soft",
                Width=180, Height=50, Parent=menu
            )
            idx = index
            btn.Clicked.Connect(lambda sender, i=idx: self.SwitchPage(i))
            self.menu_buttons.append(btn)
            menu_layout.addWidget(btn.widget)

        menu_layout.addStretch(1)

        exit_btn = LCARSButton(
            Text="REBOOT", Color=Palette.Buttons[3], Type="soft",
            Width=180, Height=60, Parent=menu
        )
        exit_btn.Clicked.Connect(lambda sender: self.ExitToDesktop())
        menu_layout.addWidget(exit_btn.widget)

        menu_holder = type("MenuReturn", (), {"widget": menu})()
        return menu_holder

    def SwitchPage(self, index):
        self.settings_chamber.setCurrentIndex(index)

    def CreateSettingsPages(self):
        pages = [
            self.CreateSystemInfoPage(),
            self.CreateBootPage(),
            self.CreateSecurityPage(),
            self.CreatePeripheralPage(),
            self.CreateStoragePage(),
            self.CreatePowerPage(),
            self.CreateDiagnosticPage(),
            self.CreateExitPage(),
        ]
        for page in pages:
            self.settings_chamber.addWidget(page)

    def CreateSystemInfoPage(self):
        page = LCARS.Widget()
        layout = LCARS.Vertical(page)
        layout.setSpacing(20)

        title = LCARSLabel(
            Text="SYSTEM INFORMATION", Color=Palette.Buttons[1],
            FontSize=24, Parent=page
        )
        layout.addWidget(title.widget)

        gridLayout = LCARS.Grid()
        gridLayout.setSpacing(15)

        info_lines = [
            ("Platform", self.SystemInfo.get("platform", "N/A")),
            ("Release", self.SystemInfo.get("platform_release", "N/A")),
            ("Architecture", self.SystemInfo.get("architecture", "N/A")),
            ("Processor", self.SystemInfo.get("processor", "N/A")),
            ("Memory Total", self.SystemInfo.get("memory_total", "N/A")),
            ("Hostname", self.SystemInfo.get("hostname", "N/A")),
        ]

        row, col = 0, 0
        for key, val in info_lines:
            card = LCARS.Widget()
            card.setStyleSheet(
                "background-color: rgba(255, 255, 255, 0.05); border-radius: 10px;"
            )
            cardLayout = LCARS.Vertical(card)
            cardLayout.setContentsMargins(15, 15, 15, 15)

            lblKey = LCARSLabel(
                Text=key.upper(), Color=Palette.Buttons[2],
                FontSize=12, Parent=card
            )
            lblVal = LCARSLabel(
                Text=val, Color="#FFFFFF", FontSize=16, Parent=card
            )
            cardLayout.addWidget(lblKey.widget)
            cardLayout.addWidget(lblVal.widget)

            gridLayout.addWidget(card, row, col)
            col += 1
            if col > 1:
                col = 0
                row += 1

        layout.addLayout(gridLayout)
        layout.addStretch(1)
        return page

    def CreateBootPage(self):
        page = LCARS.Widget()
        layout = LCARS.Vertical(page)
        layout.setSpacing(20)

        title = LCARSLabel(
            Text="BOOT ORDER", Color=Palette.Buttons[1],
            FontSize=24, Parent=page
        )
        layout.addWidget(title.widget)

        boot_section = LCARSSection("PRIORITY", Palette.Buttons[2], Parent=page)

        if self.bios:
            entries = self.bios.GetBootEntries()
            for i, entry in enumerate(entries):
                name = entry.get("Name", "UNKNOWN")
                target = entry.get("Target", "unknown")
                option_label = LCARSLabel(
                    Text=f"{i+1}. {name} [{target}]",
                    Color=Palette.Buttons[2], FontSize=14, Parent=page
                )
                boot_section.AddOption("Boot Device", option_label.widget, Palette.Buttons[2])
        else:
            boot_options = ["LCARS FRAMEWORK", "RECOVERY MODE", "NETWORK BOOT", "SAFE MODE"]
            for i, option in enumerate(boot_options):
                option_label = LCARSLabel(
                    Text=f"{i+1}. {option}",
                    Color=Palette.Buttons[2], FontSize=14, Parent=page
                )
                boot_section.AddOption("Boot Device", option_label.widget, Palette.Buttons[2])

        layout.addWidget(boot_section.widget)
        return page

    def CreateSecurityPage(self):
        page = LCARS.Widget()
        layout = LCARS.Vertical(page)
        layout.setSpacing(20)

        title = LCARSLabel(
            Text="SECURITY SETTINGS", Color=Palette.Buttons[2],
            FontSize=24, Parent=page
        )
        layout.addWidget(title.widget)

        security_section = LCARSSection("ACCESS CONTROL", Palette.Buttons[3], Parent=page)
        security_options = [
            "Password Protection: ENABLED",
            "Secure Boot: ENABLED",
            "Firmware Lock: DISABLED",
            "Admin Access: RESTRICTED",
        ]
        for option in security_options:
            label = LCARSLabel(
                Text=option, Color=Palette.Buttons[3],
                FontSize=14, Parent=page
            )
            security_section.AddOption("Option", label.widget, Palette.Buttons[3])

        layout.addWidget(security_section.widget)
        return page

    def CreatePeripheralPage(self):
        page = LCARS.Widget()
        layout = LCARS.Vertical(page)
        layout.setSpacing(20)

        title = LCARSLabel(
            Text="PERIPHERAL CONFIGURATION", Color=Palette.Buttons[3],
            FontSize=24, Parent=page
        )
        layout.addWidget(title.widget)

        peripheral_section = LCARSSection("DEVICES", Palette.Buttons[4], Parent=page)
        peripherals = [
            "Keyboard: USB Standard",
            "Mouse: USB Standard",
            "Display: LCARS Interface",
            "Audio: LCARS Audio System",
        ]
        for peripheral in peripherals:
            label = LCARSLabel(
                Text=peripheral, Color=Palette.Buttons[4],
                FontSize=14, Parent=page
            )
            peripheral_section.AddOption("Device", label.widget, Palette.Buttons[4])

        layout.addWidget(peripheral_section.widget)
        return page

    def CreateStoragePage(self):
        page = LCARS.Widget()
        layout = LCARS.Vertical(page)
        layout.setSpacing(20)

        title = LCARSLabel(
            Text="STORAGE CONFIGURATION", Color=Palette.Buttons[4],
            FontSize=24, Parent=page
        )
        layout.addWidget(title.widget)

        storage_section = LCARSSection("DRIVES", Palette.Buttons[0], Parent=page)

        try:
            import psutil
            partitions = psutil.disk_partitions()
            for partition in partitions:
                label = LCARSLabel(
                    Text=f"{partition.device} - {partition.fstype}",
                    Color=Palette.Buttons[0], FontSize=14, Parent=page
                )
                storage_section.AddOption("Drive", label.widget, Palette.Buttons[0])
        except ImportError:
            label = LCARSLabel(
                Text="Storage detection unavailable",
                Color=Palette.Buttons[0], FontSize=14, Parent=page
            )
            storage_section.AddOption("Drive", label.widget, Palette.Buttons[0])

        layout.addWidget(storage_section.widget)
        return page

    def CreatePowerPage(self):
        page = LCARS.Widget()
        layout = LCARS.Vertical(page)
        layout.setSpacing(20)

        title = LCARSLabel(
            Text="POWER MANAGEMENT", Color=Palette.Buttons[0],
            FontSize=24, Parent=page
        )
        layout.addWidget(title.widget)

        power_section = LCARSSection("SETTINGS", Palette.Buttons[1], Parent=page)
        power_options = [
            "Power Mode: HIGH PERFORMANCE",
            "Sleep Timer: 30 MINUTES",
            "Display Timeout: 15 MINUTES",
            "Battery Saver: DISABLED",
        ]
        for option in power_options:
            label = LCARSLabel(
                Text=option, Color=Palette.Buttons[1],
                FontSize=14, Parent=page
            )
            power_section.AddOption("Option", label.widget, Palette.Buttons[1])

        layout.addWidget(power_section.widget)
        return page

    def CreateDiagnosticPage(self):
        page = LCARS.Widget()
        layout = LCARS.Vertical(page)
        layout.setSpacing(20)

        title = LCARSLabel(
            Text="SYSTEM DIAGNOSTIC", Color=Palette.Buttons[1],
            FontSize=24, Parent=page
        )
        layout.addWidget(title.widget)

        diagnostic_section = LCARSSection("HEALTH CHECK", Palette.Buttons[2], Parent=page)

        try:
            import psutil
            cpu_percent = psutil.cpu_percent(interval=1)
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage("/")
            diagnostics = [
                f"CPU Usage: {cpu_percent}%",
                f"Memory Usage: {mem.percent}%",
                f"Disk Usage: {disk.percent}%",
                "System Status: NORMAL",
            ]
        except ImportError:
            diagnostics = [
                "CPU Usage: UNAVAILABLE",
                "Memory Usage: UNAVAILABLE",
                "Disk Usage: UNAVAILABLE",
                "System Status: UNKNOWN",
            ]

        for diagnostic in diagnostics:
            label = LCARSLabel(
                Text=diagnostic, Color=Palette.Buttons[2],
                FontSize=14, Parent=page
            )
            diagnostic_section.AddOption("Check", label.widget, Palette.Buttons[2])

        layout.addWidget(diagnostic_section.widget)

        run_btn = LCARSButton(
            Text="RUN FULL DIAGNOSTIC", Type="pill",
            Color=Palette.Buttons[2], Width=250, Height=45, Parent=page
        )
        run_btn.Clicked.Connect(lambda *A: self.RunFullDiagnostic())
        layout.addWidget(run_btn.widget)
        return page

    def CreateExitPage(self):
        page = LCARS.Widget()
        layout = LCARS.Vertical(page)
        layout.setSpacing(20)

        title = LCARSLabel(
            Text="SAVE AND EXIT", Color=Palette.Buttons[2],
            FontSize=24, Parent=page
        )
        layout.addWidget(title.widget)

        options_section = LCARSSection("EXIT OPTIONS", Palette.Buttons[3], Parent=page)
        layout.addWidget(options_section.widget)

        button_layout = LCARS.Horizontal(page)
        button_layout.setSpacing(20)

        save_btn = LCARSButton(
            Text="SAVE CHANGES", Type="pill",
            Color=Palette.Buttons[3], Width=200, Height=50, Parent=page
        )
        save_btn.Clicked.Connect(lambda *A: self.SaveChanges())

        discard_btn = LCARSButton(
            Text="DISCARD CHANGES", Type="pill",
            Color=Palette.Buttons[4], Width=200, Height=50, Parent=page
        )
        discard_btn.Clicked.Connect(lambda *A: self.DiscardChanges())

        button_layout.addWidget(save_btn.widget)
        button_layout.addWidget(discard_btn.widget)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        return page

    def RunFullDiagnostic(self):
        try:
            from lcars.system.odn import scanner
            telemetry = scanner.GetHardwareTelemetry()
            DTV = LCARS.System.DateTime
            if DTV and hasattr(DTV, "now"):
                Now = DTV.now()
                timestamp = Now.strftime("%H:%M:%S") if hasattr(Now, "strftime") else "00:00:00"
            else:
                timestamp = "00:00:00"
            diag_text = (
                f"DIAGNOSTIC [{timestamp}]\n"
                f"CPU: {telemetry['CpuLoad']}%\n"
                f"MEMORY: {telemetry['MemPercent']}%\n"
                f"STATUS: COMPLETE"
            )
        except Exception:
            diag_text = "DIAGNOSTIC UNAVAILABLE"

    def SaveChanges(self):
        if self.bios:
            self.bios.SaveAndExit()
        self.ExitToDesktop()

    def DiscardChanges(self):
        self.ExitToDesktop()

    def ExitToDesktop(self):
        from lcars.core.signal import ODN
        ODN.Transmit("System.Phase.Boot")


if __name__ == "__main__":
    ProjectRoot = Path(__file__).parent.parent.parent.absolute()
    if str(ProjectRoot) not in sys.path:
        sys.path.insert(0, str(ProjectRoot))

    from lcars.system.bios import BIOS

    App = LCARS.Application(sys.argv)

    bios_instance = BIOS()
    bios_ui = UEFI(bios_instance=bios_instance)

    from lcars.base.default import SetDisplayFlag

    if hasattr(bios_ui.widget, "setWindowFlag"):
        FramelessFlag = getattr(LCARS, "Frameless", None)
        if FramelessFlag is not None:
            bios_ui.widget.setWindowFlag(FramelessFlag, True)
        bios_ui.widget.showFullScreen()
    else:
        bios_ui.widget.resize(1920, 1080)
        bios_ui.widget.show()

    bios_ui.widget.setWindowTitle("LCARS UEFI Test")
    bios_ui.widget.show()
    sys.exit(App.exec())
