from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from lcars.base.component import LCARSButton, LCARSLabel, SetStyle
from lcars.base.interface import Panel
from lcars.base.default import Palette
from lcars.base.type import LCARS
from lcars.service.console import LCARSConsole

TextEditType = getattr(LCARS, "TextEdit", None)
if TextEditType is None:
    from lcars.base.component import LCARSTextEdit
    TextEditType = LCARSTextEdit


def _set_text(target: Any, text: str) -> None:
    setter = getattr(target, "SetText", None)
    if setter:
        setter(str(text))
        return
    setter = getattr(target, "setPlainText", None)
    if setter:
        setter(str(text))
        return
    setter = getattr(target, "setText", None)
    if setter:
        setter(str(text))


class SuperDesignPanel(Panel):
    def __init__(self, Parent=None, Editor=None, Designer=None):
        super().__init__(Parent=Parent, Color="#000000")
        self.Editor = Editor
        self.Designer = Designer
        self.CopilotBuffer = ""
        self.Console = LCARSConsole()

        self.Vertical(8, 8, 8, 8, 8)
        self.widget.setStyleSheet("background: #050509; border: 1px solid #224466;")

        self.Title = LCARSLabel(
            Text="SUPERDESIGN AGENT",
            Type="title",
            Parent=self.widget,
            Color="#66cccc",
            FontSize=16,
        )
        self.Add(self.Layout, self.Title)

        self.Description = LCARSLabel(
            Text="AI-driven design assistant for LCARS layouts and theme presets.",
            Type="status",
            Parent=self.widget,
            Color="#99ccff",
            FontSize=12,
        )
        self.Add(self.Layout, self.Description)

        self.ButtonRow = Panel(Parent=self.widget, Color="#000000")
        self.ButtonRow.Horizontal(0, 0, 0, 0, 6)
        self.ButtonRow.widget.setFixedHeight(48)

        self.GenerateButton = LCARSButton(
            Text="GENERATE AI DESIGN",
            Type="rect",
            Parent=self.ButtonRow.widget,
            Width=260,
            Height=38,
            Color="#66cccc",
        )
        self.ResetButton = LCARSButton(
            Text="RESET PREVIEW",
            Type="soft",
            Parent=self.ButtonRow.widget,
            Width=140,
            Height=38,
            Color="#ffcc66",
        )
        self.Add(self.ButtonRow.Layout, self.GenerateButton)
        self.Add(self.ButtonRow.Layout, self.ResetButton)
        self.Add(self.Layout, self.ButtonRow)

        self.OutputLog = None
        if TextEditType:
            self.OutputLog = TextEditType(self.widget)
            SetStyle(
                self.OutputLog,
                "background-color: #020305; color: #99ccff; border: 1px solid #224466; "
                "font-family: 'LCARS', Consolas, monospace; font-size: 12px; padding: 8px;"
            )
            self.OutputLog.setFixedHeight(180)
            self.Add(self.Layout, self.OutputLog, 1)
        else:
            self.OutputLog = LCARSLabel(
                Text="SuperDesign log is unavailable.",
                Type="console",
                Parent=self.widget,
                Color="#99ccff",
                FontSize=12,
            )
            self.Add(self.Layout, self.OutputLog)

        self.GenerateButton.clicked.Connect(self.GenerateDesign)
        self.ResetButton.clicked.Connect(self.ResetPreview)

    def Log(self, text: str) -> None:
        if self.OutputLog is None:
            return
        current = ""
        getter = getattr(self.OutputLog, "toPlainText", None)
        if getter:
            current = getter() or ""
        elif hasattr(self.OutputLog, "GetText"):
            current = self.OutputLog.GetText() or ""
        payload = current + ("\n" if current else "") + text
        _set_text(self.OutputLog, payload)
        if hasattr(self.OutputLog, "ensureCursorVisible"):
            self.OutputLog.ensureCursorVisible()

    def ResetPreview(self, checked: bool = False) -> None:
        if self.Editor is None:
            return
        self.Log("[SUPERDESIGN] Resetting preview and clearing generated content.")
        _set_text(self.Editor, "")
        if hasattr(self.Editor, "clear"):
            self.Editor.clear()
        self.Log("[SUPERDESIGN] Editor cleared.")

    def GenerateDesign(self, checked: bool = False) -> None:
        if self.Editor is None:
            self.Log("[ERROR] Editor reference missing.")
            return

        self.Log("[SUPERDESIGN] Requesting AI interface generation...")
        prompt = (
            "Generate a high-fidelity LCARS IDE interface layout for the current Nova development workspace. "
            "Use LCARSButton, LCARSLabel, Panel, Segment, Padd, and Designer-friendly components. "
            "Return only valid Python code inside a ```python``` block. "
            "Do not add prose outside the code block. "
            "Use the current LCARS theme and make the layout look polished and modern."
        )
        self.CopilotBuffer = ""

        def callback(text: str) -> None:
            self.Log(text)
            self.CopilotBuffer += text + "\n"
            if "```python" in self.CopilotBuffer and "```" in self.CopilotBuffer.split("```python")[1]:
                code = self.CopilotBuffer.split("```python")[1].split("```", 1)[0].strip()
                if code:
                    _set_text(self.Editor, code)
                    if hasattr(self.Editor, "setPlainText"):
                        self.Editor.setPlainText(code)
                    self.Log("[SUPERDESIGN] Generated design injected into editor.")
                    if self.Designer and hasattr(self.Designer, "ClearCanvas"):
                        self.Designer.ClearCanvas()
                    if hasattr(self.Editor, "textChanged"):
                        try:
                            self.Editor.textChanged.emit()
                        except Exception:
                            pass
                    self.CopilotBuffer = ""

        import threading
        from lcars.core.computer import BoardComputer
        def Worker():
            try:
                comp = BoardComputer.GetInstance()
                resp = comp.AskNeuralCore(prompt, StreamCallback=None)
                callback(resp)
            except Exception as e:
                self.Log(f"[SUPERDESIGN ERROR] {e}")

        threading.Thread(target=Worker, daemon=True).start()
