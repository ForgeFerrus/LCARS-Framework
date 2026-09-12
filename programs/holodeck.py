# ◤ TITANIUM PROGRAM :: HOLODECK SIMULATION GRID
# Безпечне ізольоване середовище виконання для тестування UI компонентів та симуляцій.
# СТАНДАРТ: Titanium (Zero-Except, No Underscores, Strict PascalCase, Pure LCARS Classes).

from __future__ import annotations
from lcars.base.type import LCARS
from lcars.base.default import GetDefaultTheme

class HolodeckProgram(LCARS.Widget):
    def __init__(self, ParentNode: any = None):
        super().__init__(ParentNode)
        self.MainLayout = LCARS.VBoxLayout(self)
        self.main_layout = self.MainLayout
        self.ActiveProgram = None
        self.active_program = self.ActiveProgram

        ThemeDict = getattr(self.parent(), "theme", {}) if self.parent() else {}
        if not ThemeDict:
            ThemeDict = GetDefaultTheme()
        self.AccentColor = ThemeDict.get("accent", "#FF9900") if isinstance(ThemeDict, dict) else "#FF9900"
        self.BgColor = ThemeDict.get("bg", "#000000") if isinstance(ThemeDict, dict) else "#000000"
        self.TextColor = ThemeDict.get("text", "#FFFFFF") if isinstance(ThemeDict, dict) else "#FFFFFF"

        self.GridLabel = LCARS.Label("◤ HOLODECK GRID // READY FOR SIMULATION INITIALIZATION")
        self.GridLabel.setStyleSheet(f"color: {self.TextColor}; text-align: center; font-size: 20px;")
        self.MainLayout.addWidget(self.GridLabel)
        self.setStyleSheet(f"background-color: {self.BgColor}; border: 2px dashed {self.AccentColor};")

    def LoadProgramFromModule(self, ModulePathStr: str, ClassNameStr: str) -> None:
        ImportLib = LCARS.System.Importlib
        if not ImportLib:
            self.HandleCrash(f"IMPORT FAILURE: System.Importlib unavailable.")
            return

        Module = ImportLib.import_module(ModulePathStr) if hasattr(ImportLib, "import_module") else None
        if Module and hasattr(Module, ClassNameStr):
            WidgetClass = getattr(Module, ClassNameStr)
            self.RunSimulation(WidgetClass)
        else:
            self.HandleCrash(f"IMPORT FAILURE: Class {ClassNameStr} not found in {ModulePathStr}.")

    load_program_from_module = LoadProgramFromModule

    def RunSimulation(self, WidgetClass: any, *Args: any, **Kwargs: any) -> None:
        if self.ActiveProgram:
            self.MainLayout.removeWidget(self.ActiveProgram)
            if hasattr(self.ActiveProgram, "deleteLater"):
                self.ActiveProgram.deleteLater()

        self.ActiveProgram = WidgetClass(*Args, **Kwargs)
        self.active_program = self.ActiveProgram
        self.MainLayout.addWidget(self.ActiveProgram)
        self.GridLabel.hide()

    run_simulation = RunSimulation

    def HandleCrash(self, ErrorMessageStr: str) -> None:
        if self.ActiveProgram:
            self.ActiveProgram.hide()
        self.GridLabel.setText(f"SIMULATION ERROR: {ErrorMessageStr}")
        self.GridLabel.show()

    _handle_crash = HandleCrash

class HolodeckRunner(LCARS):
    @staticmethod
    def Main() -> None:
        App = LCARS.Application.instance() or LCARS.Application(LCARS.System.Arguments)
        MainDisplay = LCARS.Display()
        Holo = HolodeckProgram(MainDisplay.widget)
        Content = MainDisplay.Items["Content"].widget if "Content" in MainDisplay.Items else MainDisplay.widget
        Layout = Content.layout() or LCARS.Vertical(Content)
        Layout.addWidget(Holo)
        MainDisplay.widget.resize(800, 600)
        MainDisplay.widget.show()
        if hasattr(App, "exec"):
            LCARS.System.Exit(App.exec())

if __name__ == "__main__":
    HolodeckRunner.Main()
