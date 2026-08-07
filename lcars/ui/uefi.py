import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
import importlib.util

project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from lcars.base.interface import Segment, Panel, Screen
from lcars.base.type import LCARS
from lcars.base.default import Palette, Widget
from lcars.base.component import LCARSButton, LCARSLabel, LCARSBar, LCARSElbow

# Секція UEFI інтерфейсу для групування параметрів
class LCARSSection(Segment):
    def __init__(self, title, color, Parent=None):
        super().__init__(Parent=Parent)
        self.widget.setStyleSheet(f"background-color: rgba(47, 55, 73, 0.5); border: 2px solid {color}; border-radius: 20px;")
        
        section_layout = LCARS.VBox(self.widget)
        section_layout.setContentsMargins(20, 15, 20, 15)
        section_layout.setSpacing(12)
        self.section_layout = section_layout
        
        title_label = LCARSLabel(Text=f"◢ {title}", Color=color, FontSize=16, Parent=self.widget)
        section_layout.addWidget(title_label.widget)
    
    # Додаємо опцію до секції у вигляді рядка з міткою та віджетом
    def AddOption(self, label, widget, color):
        row = Segment(Parent=self.widget)
        row_layout = LCARS.HBox(row.widget)
        row_layout.setContentsMargins(0, 5, 0, 5)
        
        label_widget = LCARSLabel(Text=label, Color=color, FontSize=13, Parent=row.widget)
        row_layout.addWidget(label_widget.widget)
        
        row_layout.addStretch()
        row_layout.addWidget(Widget(widget))
        
        self.section_layout.addWidget(row.widget)


# Головний клас екрану UEFI — налаштування системи
class UEFI(Screen):
    def __init__(self, Parent=None, bios_instance=None):
        super().__init__(Parent=None)
        if bios_instance is not None:
            self.bios = bios_instance
        else:
            self.bios = Parent
        self.current_era = 25
        self.SystemInfo = {}
        self.LoadSystemInfo()
        self.BuildUi()
    
    # Завантажуємо інформацію про систему з платформи та BIOS
    def LoadSystemInfo(self):
        import platform
        self.SystemInfo = {
            "platform": platform.system(),
            "platform_release": platform.release(),
            "platform_version": platform.version(),
            "architecture": platform.machine(),
            "hostname": platform.node(),
            "processor": platform.processor(),
            "python_version": platform.python_version()
        }
        if self.bios:
            self.SystemInfo["processor"] = self.bios.Hardware.Cpu
            self.SystemInfo["memory_total"] = str(self.bios.Hardware.MemoryTotal) + " MB"
    
    # Будуємо головний інтерфейс UEFI: шапка, тіло, підвал
    def BuildUi(self):
        MainLayout = self.Layout
        if not MainLayout:
            MainLayout = LCARS.VBox()
            self.widget.setLayout(MainLayout)
        
        MainLayout.setContentsMargins(15, 15, 15, 15)
        MainLayout.setSpacing(10)
        
        # Верхня частина з LCARSElbow
        TopFrame = LCARS.HBox()
        TopFrame.setSpacing(10)
        
        self.ElbowTopLeft = LCARSElbow(Direction="top-left", Color=Palette.Buttons[0], Width=180, Height=60, Parent=self.widget)
        TopFrame.addWidget(self.ElbowTopLeft.Widget)
        
        self.HeaderBar = LCARSBar(Parent=self.widget, Color=Palette.Buttons[0], Height=60)
        TitleLayout = LCARS.HBox(self.HeaderBar.Widget)
        TitleLayout.setContentsMargins(20, 0, 20, 0)
        
        title = LCARSLabel(Text="SYSTEM CONFIGURATION // UEFI v25.0", Color="#000000", FontSize=24, Weight="bold", Parent=self.HeaderBar.Widget)
        TitleLayout.addWidget(title.widget)
        TitleLayout.addStretch()
        
        TopFrame.addWidget(self.HeaderBar.Widget, 1)
        
        self.HeaderElbowRight = LCARSElbow(Direction="top-right", Color=Palette.Buttons[0], Width=60, Height=60, Parent=self.widget)
        TopFrame.addWidget(self.HeaderElbowRight.Widget)
        
        MainLayout.addLayout(TopFrame)
        
        # Основний вміст: меню зліва, налаштування справа
        BodyFrame = LCARS.HBox()
        BodyFrame.setSpacing(15)
        
        menu = self.CreateMenu()
        BodyFrame.addWidget(menu.widget)
        
        self.settings_chamber = LCARS.Chamber(self.widget)
        self.CreateSettingsPages()
        BodyFrame.addWidget(self.settings_chamber, 1)
        
        MainLayout.addLayout(BodyFrame, 1)
        
        # Нижня частина — підвал
        FooterFrame = LCARS.HBox()
        FooterFrame.setSpacing(10)
        
        self.ElbowBottomLeft = LCARSElbow(Direction="bottom-left", Color=Palette.Buttons[0], Width=180, Height=30, Parent=self.widget)
        FooterFrame.addWidget(self.ElbowBottomLeft.Widget)
        
        self.FooterBar = LCARSBar(Parent=self.widget, Color=Palette.Buttons[0], Height=30)
        FooterFrame.addWidget(self.FooterBar.Widget, 1)
        
        MainLayout.addLayout(FooterFrame)
    
    # Створюємо бічне меню навігації з кнопками сторінок
    def CreateMenu(self):
        menu = Segment(Parent=self.widget)
        menu.widget.setFixedWidth(180)
        
        menu_layout = LCARS.VBox(menu.widget)
        menu_layout.setContentsMargins(0, 0, 0, 0)
        menu_layout.setSpacing(8)
        menu_layout.setAlignment(LCARS.Protocol.AlignmentFlag.AlignTop)
        
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
            btn = LCARSButton(Text=label, Color=color, Type="soft", Width=180, Height=50, Parent=menu.widget)
            btn.clicked.connect(lambda _, i=index: self.SwitchPage(i))
            self.menu_buttons.append(btn)
            menu_layout.addWidget(btn.widget)
        
        menu_layout.addStretch(1)
        
        exit_btn = LCARSButton(Text="REBOOT", Color=Palette.Buttons[3], Type="soft", Width=180, Height=60, Parent=menu.widget)
        exit_btn.clicked.connect(self.ExitToDesktop)
        menu_layout.addWidget(exit_btn.widget)
        
        return menu
    
    # Перемикаємо сторінку налаштувань за індексом
    def SwitchPage(self, index):
        self.settings_chamber.setCurrentIndex(index)
    
    # Створюємо всі сторінки налаштувань і додаємо до камери
    def CreateSettingsPages(self):
        system_info_page = self.CreateSystemInfoPage()
        self.settings_chamber.addWidget(system_info_page.widget)
        
        boot_page = self.CreateBootPage()
        self.settings_chamber.addWidget(boot_page.widget)
        
        security_page = self.CreateSecurityPage()
        self.settings_chamber.addWidget(security_page.widget)
        
        peripheral_page = self.CreatePeripheralPage()
        self.settings_chamber.addWidget(peripheral_page.widget)
        
        storage_page = self.CreateStoragePage()
        self.settings_chamber.addWidget(storage_page.widget)
        
        power_page = self.CreatePowerPage()
        self.settings_chamber.addWidget(power_page.widget)
        
        diagnostic_page = self.CreateDiagnosticPage()
        self.settings_chamber.addWidget(diagnostic_page.widget)
        
        exit_page = self.CreateExitPage()
        self.settings_chamber.addWidget(exit_page.widget)
    
    # Сторінка інформації про систему з картками даних
    def CreateSystemInfoPage(self):
        page = Segment(Parent=self.widget)
        layout = LCARS.VBox(page.widget)
        layout.setSpacing(20)
        
        title = LCARSLabel(Text="SYSTEM INFORMATION", Color=Palette.Buttons[1], FontSize=24, Weight="bold", Parent=page.widget)
        layout.addWidget(title.widget)
        
        # Сітка для відображення інформації про систему
        gridLayout = LCARS.Grid()
        gridLayout.setSpacing(15)
        
        info_lines = [
            ("Platform", self.SystemInfo.get('platform', 'N/A')),
            ("Release", self.SystemInfo.get('platform_release', 'N/A')),
            ("Architecture", self.SystemInfo.get('architecture', 'N/A')),
            ("Processor", self.SystemInfo.get('processor', 'N/A')),
            ("Memory Total", self.SystemInfo.get('memory_total', 'N/A')),
            ("Hostname", self.SystemInfo.get('hostname', 'N/A'))
        ]
        
        row, col = 0, 0
        for key, val in info_lines:
            # Створюємо картку для кожного параметра
            card = Segment(Parent=page.widget)
            card.widget.setStyleSheet(f"background-color: rgba(255, 255, 255, 0.05); border-radius: 10px;")
            cardLayout = LCARS.VBox(card.widget)
            cardLayout.setContentsMargins(15, 15, 15, 15)
            
            lblKey = LCARSLabel(Text=key.upper(), Color=Palette.Buttons[2], FontSize=12, Parent=card.widget)
            lblVal = LCARSLabel(Text=val, Color="#FFFFFF", FontSize=16, Weight="bold", Parent=card.widget)
            
            cardLayout.addWidget(lblKey.widget)
            cardLayout.addWidget(lblVal.widget)
            
            gridLayout.addWidget(card.widget, row, col)
            col += 1
            # Переводимо на наступний рядок після двох стовпців
            if col > 1:
                col = 0
                row += 1
                
        layout.addLayout(gridLayout)
        layout.addStretch(1)
        
        return page
    
    # Сторінка порядку завантаження — список пріоритетів boot
    def CreateBootPage(self):
        page = Segment(Parent=self.widget)
        layout = LCARS.VBox(page.widget)
        layout.setSpacing(20)
        
        title = LCARSLabel(Text="BOOT ORDER", Color=Palette.Buttons[1], FontSize=24, Parent=page.widget)
        layout.addWidget(title.widget)
        
        boot_section = LCARSSection("PRIORITY", Palette.Buttons[2], Parent=page.widget)
        
        if self.bios:
            entries = self.bios.GetBootEntries()
            for i, entry in enumerate(entries):
                name = entry.get("Name", "UNKNOWN")
                target = entry.get("Target", "unknown")
                option_label = LCARSLabel(Text=f"{i+1}. {name} [{target}]", Color=Palette.Buttons[2], FontSize=14, Parent=page.widget)
                boot_section.AddOption("Boot Device", option_label.widget, Palette.Buttons[2])
        else:
            boot_options = ["LCARS FRAMEWORK", "RECOVERY MODE", "NETWORK BOOT", "SAFE MODE"]
            for i, option in enumerate(boot_options):
                option_label = LCARSLabel(Text=f"{i+1}. {option}", Color=Palette.Buttons[2], FontSize=14, Parent=page.widget)
                boot_section.AddOption("Boot Device", option_label.widget, Palette.Buttons[2])
        
        layout.addWidget(boot_section.widget)
        
        return page
    
    # Сторінка налаштувань безпеки — пароль, secure boot тощо
    def CreateSecurityPage(self):
        page = Segment(Parent=self.widget)
        layout = LCARS.VBox(page.widget)
        layout.setSpacing(20)
        
        title = LCARSLabel(Text="SECURITY SETTINGS", Color=Palette.Buttons[2], FontSize=24, Parent=page.widget)
        layout.addWidget(title.widget)
        
        security_section = LCARSSection("ACCESS CONTROL", Palette.Buttons[3], Parent=page.widget)
        
        security_options = [
            "Password Protection: ENABLED",
            "Secure Boot: ENABLED",
            "Firmware Lock: DISABLED",
            "Admin Access: RESTRICTED"
        ]
        
        for option in security_options:
            label = LCARSLabel(Text=option, Color=Palette.Buttons[3], FontSize=14, Parent=page.widget)
            security_section.AddOption("Option", label.widget, Palette.Buttons[3])
        
        layout.addWidget(security_section.widget)
        
        return page
    
    # Сторінка конфігурації периферійних пристроїв
    def CreatePeripheralPage(self):
        page = Segment(Parent=self.widget)
        layout = LCARS.VBox(page.widget)
        layout.setSpacing(20)
        
        title = LCARSLabel(Text="PERIPHERAL CONFIGURATION", Color=Palette.Buttons[3], FontSize=24, Parent=page.widget)
        layout.addWidget(title.widget)
        
        peripheral_section = LCARSSection("DEVICES", Palette.Buttons[4], Parent=page.widget)
        
        peripherals = [
            "Keyboard: USB Standard",
            "Mouse: USB Standard",
            "Display: LCARS Interface",
            "Audio: LCARS Audio System"
        ]
        
        for peripheral in peripherals:
            label = LCARSLabel(Text=peripheral, Color=Palette.Buttons[4], FontSize=14, Parent=page.widget)
            peripheral_section.AddOption("Device", label.widget, Palette.Buttons[4])
        
        layout.addWidget(peripheral_section.widget)
        
        return page
    
    # Сторінка сховища — перелік дисків та розділів
    def CreateStoragePage(self):
        page = Segment(Parent=self.widget)
        layout = LCARS.VBox(page.widget)
        layout.setSpacing(20)
        
        title = LCARSLabel(Text="STORAGE CONFIGURATION", Color=Palette.Buttons[4], FontSize=24, Parent=page.widget)
        layout.addWidget(title.widget)
        
        storage_section = LCARSSection("DRIVES", Palette.Buttons[0], Parent=page.widget)
        
        # Перевіряємо наявність psutil для виявлення дисків
        psutil_found = importlib.util.find_spec("psutil") is not None
        if psutil_found:
            import psutil
            partitions = psutil.disk_partitions()
            for partition in partitions:
                label = LCARSLabel(Text=f"{partition.device} - {partition.fstype}", Color=Palette.Buttons[0], FontSize=14, Parent=page.widget)
                storage_section.AddOption("Drive", label.widget, Palette.Buttons[0])
        else:
            label = LCARSLabel(Text="Storage detection unavailable", Color=Palette.Buttons[0], FontSize=14, Parent=page.widget)
            storage_section.AddOption("Drive", label.widget, Palette.Buttons[0])
        
        layout.addWidget(storage_section.widget)
        
        return page
    
    # Сторінка керування живленням — режими, таймери
    def CreatePowerPage(self):
        page = Segment(Parent=self.widget)
        layout = LCARS.VBox(page.widget)
        layout.setSpacing(20)
        
        title = LCARSLabel(Text="POWER MANAGEMENT", Color=Palette.Buttons[0], FontSize=24, Parent=page.widget)
        layout.addWidget(title.widget)
        
        power_section = LCARSSection("SETTINGS", Palette.Buttons[1], Parent=page.widget)
        
        power_options = [
            "Power Mode: HIGH PERFORMANCE",
            "Sleep Timer: 30 MINUTES",
            "Display Timeout: 15 MINUTES",
            "Battery Saver: DISABLED"
        ]
        
        for option in power_options:
            label = LCARSLabel(Text=option, Color=Palette.Buttons[1], FontSize=14, Parent=page.widget)
            power_section.AddOption("Option", label.widget, Palette.Buttons[1])
        
        layout.addWidget(power_section.widget)
        
        return page
    
    # Сторінка діагностики — моніторинг ресурсів системи
    def CreateDiagnosticPage(self):
        page = Segment(Parent=self.widget)
        layout = LCARS.VBox(page.widget)
        layout.setSpacing(20)
        
        title = LCARSLabel(Text="SYSTEM DIAGNOSTIC", Color=Palette.Buttons[1], FontSize=24, Parent=page.widget)
        layout.addWidget(title.widget)
        
        diagnostic_section = LCARSSection("HEALTH CHECK", Palette.Buttons[2], Parent=page.widget)
        
        # Перевіряємо наявність psutil для діагностики системи
        psutil_found = importlib.util.find_spec("psutil") is not None
        if psutil_found:
            import psutil
            cpu_percent = psutil.cpu_percent(interval=1)
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            diagnostics = [
                f"CPU Usage: {cpu_percent}%",
                f"Memory Usage: {mem.percent}%",
                f"Disk Usage: {disk.percent}%",
                "System Status: NORMAL"
            ]
        else:
            diagnostics = [
                "CPU Usage: UNAVAILABLE",
                "Memory Usage: UNAVAILABLE",
                "Disk Usage: UNAVAILABLE",
                "System Status: UNKNOWN"
            ]
        
        for diagnostic in diagnostics:
            label = LCARSLabel(Text=diagnostic, Color=Palette.Buttons[2], FontSize=14, Parent=page.widget)
            diagnostic_section.AddOption("Check", label.widget, Palette.Buttons[2])
        
        layout.addWidget(diagnostic_section.widget)
        
        run_btn = LCARSButton(Text="RUN FULL DIAGNOSTIC", Type="pill", Color=Palette.Buttons[2], Width=250, Height=45, Parent=page.widget)
        run_btn.clicked.connect(self.RunFullDiagnostic)
        layout.addWidget(run_btn.widget)
        
        return page
    
    # Сторінка збереження та виходу — зберегти / відхилити зміни
    def CreateExitPage(self):
        page = Segment(Parent=self.widget)
        layout = LCARS.VBox(page.widget)
        layout.setSpacing(20)
        
        title = LCARSLabel(Text="SAVE AND EXIT", Color=Palette.Buttons[2], FontSize=24, Parent=page.widget)
        layout.addWidget(title.widget)
        
        options_section = LCARSSection("EXIT OPTIONS", Palette.Buttons[3], Parent=page.widget)
        
        layout.addWidget(options_section.widget)
        
        button_layout = LCARS.HBox(page.widget)
        button_layout.setSpacing(20)
        
        save_btn = LCARSButton(Text="SAVE CHANGES", Type="pill", Color=Palette.Buttons[3], Width=200, Height=50, Parent=page.widget)
        save_btn.clicked.connect(self.SaveChanges)
        
        discard_btn = LCARSButton(Text="DISCARD CHANGES", Type="pill", Color=Palette.Buttons[4], Width=200, Height=50, Parent=page.widget)
        discard_btn.clicked.connect(self.DiscardChanges)
        
        button_layout.addWidget(save_btn.widget)
        button_layout.addWidget(discard_btn.widget)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        return page
    
    # Запуск повної діагностики — збір телеметрії апаратури
    def RunFullDiagnostic(self):
        # Перевіряємо наявність модуля сканера для діагностики
        scanner_found = importlib.util.find_spec("lcars.system.odn.scanner") is not None
        if scanner_found:
            from lcars.system.odn import scanner
            telemetry = scanner.GetHardwareTelemetry()
            
            timestamp = datetime.now().strftime("%H:%M:%S")
            diag_text = f"DIAGNOSTIC [{timestamp}]\nCPU: {telemetry['CpuLoad']}%\nMEMORY: {telemetry['MemPercent']}%\nSTATUS: COMPLETE"
        else:
            diag_text = "DIAGNOSTIC UNAVAILABLE"
    
    # Зберігаємо зміни BIOS та повертаємось на робочий стіл
    def SaveChanges(self):
        if self.bios:
            self.bios.SaveAndExit()
        self.ExitToDesktop()
    
    # Відхиляємо зміни і повертаємось на робочий стіл
    def DiscardChanges(self):
        self.ExitToDesktop()
    
    # Створюємо підвал у вигляді смуги
    def CreateFooter(self):
        footer = LCARSBar(Type="bar", Color=Palette.Buttons[1], Height=30, Parent=self.widget)
        return footer
    
    # Надсилаємо сигнал завершення та виходимо з UEFI
    def ExitToDesktop(self):
        from lcars.core.signal import ODN
        ODN.send("System.Phase.Boot")

if __name__ == "__main__":
    import sys
    from pathlib import Path

    ProjectRoot = Path(__file__).parent.parent.parent.absolute()
    if str(ProjectRoot) not in sys.path:
        sys.path.insert(0, str(ProjectRoot))

    from lcars.base.type import LCARS
    from lcars.system.bios import BIOS

    App = LCARS.Application(sys.argv)
    
    # Ініціалізуємо логіку бази BIOS
    bios_instance = BIOS()
    
    # Створюємо і малюємо екран UEFI
    bios_ui = UEFI(bios_instance=bios_instance)
    
    # Задаємо відображення без рамок Windows і на весь екран
    from lcars.base.default import SetDisplayFlag
    Protocol = LCARS.Protocol
    Display = getattr(Protocol, "WindowType", None)
    State = getattr(Protocol, "WindowState", None)
    
    if Display and hasattr(Display, "FramelessWindowHint"):
        SetDisplayFlag(bios_ui.widget, Display.FramelessWindowHint, True)
    if State and hasattr(State, "WindowFullScreen"):
        bios_ui.widget.setWindowState(State.WindowFullScreen)
    else:
        bios_ui.widget.resize(1920, 1080)
        
    bios_ui.widget.setWindowTitle("LCARS UEFI Test")
    bios_ui.widget.show()
    
    sys.exit(App.exec())
