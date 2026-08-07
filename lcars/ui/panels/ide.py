# ◤ TITANIUM IDE PANEL — v44.20 🖖
# LCARS Framework :: INTEGRATED DEVELOPMENT ENVIRONMENT
# ─────────────────────────────────────────────────────────────────────────────
# ОПИС: Базова панель IDE з інтеграцією BoardComputer для AI-допомоги
# ФУНКЦІЇ: Редагування файлів, термінал, AI-допомога, системні команди
# ─────────────────────────────────────────────────────────────────────────────

from __future__ import annotations
from pathlib import Path
from typing import Optional

from lcars.base.type import LCARS
from lcars.base.component import LCARSButton, LCARSBar, LCARSLabel
from lcars.base.interface import Panel, Segment
from lcars.base.default import Palette
from lcars.core.signal import Transmission
from lcars.service.console import LCARSConsole
from lcars.ui.terminal import LCARSTerminal


# ◤ ГОЛОВНИЙ КЛАС IDE ПАНЕЛІ
class TitaniumIDE(Segment):
    def __init__(self, Parent=None, BoardComputer=None):
        # ◤ ІНІЦІАЛІЗАЦІЯ З МОЖЛИВІСТЮ ЗОВНІШНЬОГО КОМП'ЮТЕРА
        super().__init__(Parent=Parent)
        
        self.BoardComputer = BoardComputer
        self.CurrentFile: Optional[Path] = None
        self.ProjectRoot = Path(__file__).resolve().parents[3]
        
        self.BuildInterface()
        self.ConnectBoardComputer()
        
    def BuildInterface(self):
        # ◤ ПОБУДОВА ІНТЕРФЕЙСУ IDE
        rootLayout = self.Vertical(16, 16, 16, 16, 8)
        
        HeaderContainer = Segment(Parent=self.widget)
        HeaderLayout = LCARS.Horizontal(HeaderContainer.widget)
        HeaderLayout.setContentsMargins(0, 0, 0, 0)
        HeaderLayout.setSpacing(6)
        
        # ◤ КНОПКИ УПРАВЛІННЯ
        self.NewFileBtn = LCARSButton(
            Text="NEW", 
            Type="pill", 
            Color=Palette.Buttons[1 % len(Palette.Buttons)],
            Parent=HeaderContainer.widget,
            Width=80, Height=40
        )
        self.OpenFileBtn = LCARSButton(
            Text="OPEN",
            Type="pill",
            Color=Palette.Buttons[2 % len(Palette.Buttons)], 
            Parent=HeaderContainer.widget,
            Width=80, Height=40
        )
        self.SaveFileBtn = LCARSButton(
            Text="SAVE",
            Type="pill",
            Color=Palette.Buttons[3 % len(Palette.Buttons)],
            Parent=HeaderContainer.widget,
            Width=80, Height=40
        )
        self.AiFixBtn = LCARSButton(
            Text="AI FIX",
            Type="pill",
            Color=Palette.Buttons[4 % len(Palette.Buttons)],
            Parent=HeaderContainer.widget,
            Width=90, Height=40
        )
        self.ConsoleBtn = LCARSButton(
            Text="CONSOLE",
            Type="pill",
            Color=Palette.Buttons[5 % len(Palette.Buttons)],
            Parent=HeaderContainer.widget,
            Width=100, Height=40
        )
        self.RunBtn = LCARSButton(
            Text="RUN",
            Type="pill", 
            Color=Palette.Buttons[6 % len(Palette.Buttons)],
            Parent=HeaderContainer.widget,
            Width=80, Height=40
        )
        
        self.Add(HeaderLayout, self.NewFileBtn)
        self.Add(HeaderLayout, self.OpenFileBtn)
        self.Add(HeaderLayout, self.SaveFileBtn)
        self.Add(HeaderLayout, self.AiFixBtn)
        self.Add(HeaderLayout, self.ConsoleBtn)
        self.Add(HeaderLayout, self.RunBtn)
        HeaderLayout.addStretch()
        
        self.Add(rootLayout, HeaderContainer)
        
        # ◤ ПІДКЛЮЧЕННЯ СИГНАЛІВ ДО КНОПОК
        self.NewFileBtn.Clicked.Connect(self.NewFile)
        self.OpenFileBtn.Clicked.Connect(self.OpenFile)
        self.SaveFileBtn.Clicked.Connect(self.SaveFile)
        self.AiFixBtn.Clicked.Connect(self.AiFixCurrent)
        self.ConsoleBtn.Clicked.Connect(self.ToggleConsole)
        self.RunBtn.Clicked.Connect(self.RunCurrent)
        
        # ◤ ОБЛАСТЬ РЕДАГУВАННЯ КОДУ
        self.Editor = LCARS.PlainText(self.widget)
        if self.Editor:
            self.Editor.setStyleSheet(
                "background-color: #050509; color: #99ccff; border: none; "
                "font-family: 'LCARS', Consolas, monospace; font-size: 16px; "
                "padding: 12px;"
            )
            self.Add(rootLayout, self.Editor, 1)
        
        # ◤ КОНСОЛЬ (СПОЧАТКУ ПРИХОВАНА)
        self.ConsolePanel = LCARSTerminal(
            Parent=self.widget,
            BoardComputer=self.BoardComputer
        )
        self.ConsolePanel.Widget.hide()
        self.Add(rootLayout, self.ConsolePanel.Widget, 1)
        
    def ConnectBoardComputer(self):
        # ◤ ПІДКЛЮЧЕННЯ ДО BOARD COMPUTER АБО REGISTRY
        if self.BoardComputer is None:
            # ◤ ПЕРЕВІРКА НАЯВНОСТІ REGISTRY ПЕРЕД ІМПОРТОМ
            if hasattr(__import__('lcars.base.register', fromlist=['REGISTRY']), 'REGISTRY'):
                from lcars.base.register import REGISTRY
                # ◤ ПЕРЕВІРКА ЧИ ІСНУЄ МЕТОД Get В REGISTRY
                if hasattr(REGISTRY, 'Get'):
                    self.BoardComputer = REGISTRY.Get("BoardComputer")
    
    def NewFile(self):
        # ◤ СТВОРЕННЯ НОВОГО ПОРОЖНЬОГО ФАЙЛУ
        self.CurrentFile = None
        if self.Editor:
            self.Editor.clear()
        
    def OpenFile(self):
        # ◤ ВІДКРИТТЯ ФАЙЛУ ЧЕРЕЗ ДІАЛОГ ВИБОРУ
        from PyQt6.QtWidgets import QFileDialog
        # ◤ ПЕРЕВІРКА НАЯВНОСТІ QFileDialog ПЕРЕД ВИКОРИСТАННЯМ
        if QFileDialog:
            filepath, _ = QFileDialog.getOpenFileName(
                self.widget, "OPEN FILE", str(self.ProjectRoot), 
                "All Files (*);;Python Files (*.py)"
            )
            if filepath:
                self.CurrentFile = Path(filepath)
                if self.Editor:
                    content = self.CurrentFile.read_text(encoding='utf-8')
                    self.Editor.setPlainText(content)
                self.SetStatus(f"OPENED: {self.CurrentFile.name}")
        
    def SaveFile(self):
        # ◤ ЗБЕРЕЖЕННЯ ПОТОЧНОГО ФАЙЛУ
        if self.CurrentFile and self.Editor:
            content = self.Editor.toPlainText()
            self.CurrentFile.write_text(content, encoding='utf-8')
            self.SetStatus(f"SAVED: {self.CurrentFile.name}")
        else:
            self.SetStatus("NO FILE TO SAVE")
            
    def AiFixCurrent(self):
        # ◤ AI-ВИПРАВЛЕННЯ ПОТОЧНОГО ФАЙЛУ ЧЕРЕЗ BOARD COMPUTER
        if not self.BoardComputer:
            self.SetStatus("BOARD COMPUTER OFFLINE")
            return
            
        if self.CurrentFile:
            # ◤ ПЕРЕВІРКА НАЯВНОСТІ МЕТОДУ askAI
            if hasattr(self.BoardComputer, 'askAI'):
                result = self.BoardComputer.askAI(f"Fix errors in file: {self.CurrentFile}")
                self.SetStatus("AI ANALYSIS COMPLETE")
                # ◤ ПОКАЗАТИ РЕЗУЛЬТАТ В КОНСОЛІ
                self.ShowConsole()
                if hasattr(self.ConsolePanel, 'Console'):
                    self.ConsolePanel.Console.Execute(f"echo {result}", lambda x: None)
        else:
            self.SetStatus("NO FILE OPEN")
            
    def ToggleConsole(self):
        # ◤ ПЕРЕМИКАННЯ ВИДИМОСТІ КОНСОЛІ
        if self.ConsolePanel.Widget.isVisible():
            self.ConsolePanel.Widget.hide()
        else:
            self.ConsolePanel.Widget.show()
            
    def ShowConsole(self):
        # ◤ ПОКАЗАТИ КОНСОЛЬ
        self.ConsolePanel.Widget.show()
        
    def RunCurrent(self):
        # ◤ ЗАПУСК ПОТОЧНОГО ФАЙЛУ
        if self.CurrentFile:
            self.SetStatus(f"RUNNING: {self.CurrentFile.name}")
            import subprocess
            import sys
            # ◤ ПЕРЕВІРКА НАЯВНОСТІ МЕТОДУ Popen
            if hasattr(subprocess, 'Popen'):
                subprocess.Popen([sys.executable, str(self.CurrentFile)])
        else:
            self.SetStatus("NO FILE TO RUN")
            
    def SetStatus(self, message: str):
        # ◤ ВСТАНОВЛЕННЯ СТАТУСУ ДО КОНСОЛІ
        # Тут можна додати індикатор статусу
        print(f"[IDE] {message}")
