# ◤ TITANIUM INTERFACE ARCHITECT & STUDIO — v44.20 🖖
# LCARS Framework :: DEVELOPMENT_SUITE // VISUAL_ENGINE // PERSISTENCE
# ─────────────────────────────────────────────────────────────────────────────
# Професійний інтерактивний конструктор та редактор інтерфейсів LCARS.
# Можливості:
# 1. Створення, перетягування та зміна розмірів графічних примітивів (Button, Label, Elbow, Bar, DataBlock).
# 2. Інспектор властивостей: Текст, чіп-номер, кольорова палітра, розміри, координати.
# 3. Збереження та завантаження структури інтерфейсу у файл (JSON) із персистентністю.
# 4. Застосування збережених змін до активного робочого столу.
# ─────────────────────────────────────────────────────────────────────────────

from __future__ import annotations
import os
import sys
import json
import random
from pathlib import Path

# Додаємо корінь проєкту до sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from lcars.base.type import Directive, Matrix, LCARS
from lcars.base.default import Palette, RandomButtonColor
from lcars.base.interface import LCARSProgramPanel, Segment, Screen
from lcars.base.component import LCARSButton, LCARSLabel, LCARSElbow, LCARSBar
from lcars.core.signal import ODN
from lcars.modules.memory import GetMemory


# =========================================================================
# ІНТЕРАКТИВНИЙ ВУЗОЛ ДИЗАЙНУ (DRAGGABLE LCARS DESIGN NODE)
# =========================================================================

class DraggableNode(Matrix):
    """Інтерактивний вузол на робочому полотні дизайнера."""

    def __init__(self, ParentCanvas=None, ArchitectRef=None, PrimitiveType="BUTTON", LabelText="NODE", Number="47", ColorHex=None, PosX=50, PosY=50, Width=180, Height=46):
        super().__init__(ParentCanvas)
        self.ArchitectEngine = ArchitectRef
        self.PrimitiveType = PrimitiveType
        self.LabelText = LabelText
        self.ChipNumber = Number
        self.ColorHex = ColorHex or Palette.Buttons[1]
        self.IsDragging = False
        self.DragStartPos = None
        self.IsSelected = False

        self.setGeometry(PosX, PosY, Width, Height)
        if hasattr(LCARS.Protocol.Align, "WidgetAttribute"):
            self.setAttribute(LCARS.Protocol.Align.WidgetAttribute.WA_DeleteOnClose, True)

        # Створення внутрішнього макета
        self.NodeLayout = LCARS.Vertical(self)
        self.NodeLayout.setContentsMargins(0, 0, 0, 0)
        self.NodeLayout.setSpacing(0)

        self.PrimitiveWidget = self.BuildPrimitive(self.PrimitiveType, self.LabelText, self.ChipNumber, self.ColorHex)
        if self.PrimitiveWidget:
            TargetW = self.PrimitiveWidget.widget if hasattr(self.PrimitiveWidget, "widget") else self.PrimitiveWidget
            TargetW.setAttribute(LCARS.Protocol.Align.WidgetAttribute.WA_TransparentForMouseEvents, True)
            self.NodeLayout.addWidget(TargetW)

        self.UpdateSelectionVisuals(False)
        self.show()

    def BuildPrimitive(self, PType, Text, Num, Col):
        if PType == "BUTTON":
            btn = LCARSButton(Text=Text, Number=Num, Form=LCARSButton.Soft, Parent=self)
            btn.ColorGroup = "buttons"
            return btn
        elif PType == "PILL":
            return LCARSButton(Text=Text, Number=Num, Form=LCARSButton.Pill, Parent=self)
        elif PType == "ELBOW":
            return LCARSElbow(Direction="top-left", Color=Col, Thickness=32, Radius=24, Parent=self)
        elif PType == "BAR":
            return LCARSBar(Type="rect", Color=Col, Height=28, Parent=self)
        elif PType == "LABEL":
            return LCARSLabel(Text=Text, Color=Col, FontSize=12, Parent=self)
        elif PType == "CARD":
            card = Segment(Parent=self)
            card.widget.setStyleSheet(f"background-color: #111118; border-left: 4px solid {Col}; border-radius: 4px;")
            cLay = LCARS.Vertical(card.widget)
            cLay.setContentsMargins(8, 6, 8, 6)
            tLbl = LCARSLabel(Text=Text, Color="#FFFFFF", FontSize=11, Parent=card.widget)
            cLay.addWidget(tLbl.widget)
            sLbl = LCARSLabel(Text=f"CHIP {Num} // OPERATIONAL", Color="#8899AA", FontSize=8, Parent=card.widget)
            cLay.addWidget(sLbl.widget)
            return card
        else:
            return LCARSButton(Text=Text, Number=Num, Form=LCARSButton.Soft, Parent=self)

    def mousePressEvent(self, event):
        if event.button() == Directive.Protocol.MouseButton.LeftButton:
            self.IsDragging = True
            self.DragStartPos = event.pos()
            self.raise_()
            if self.ArchitectEngine:
                self.ArchitectEngine.SelectActiveNode(self)

    def mouseMoveEvent(self, event):
        if self.IsDragging and self.DragStartPos:
            new_pos = self.pos() + (event.pos() - self.DragStartPos)
            # Прив'язка до сітки 10x10
            snapped_x = max(0, (new_pos.x() // 10) * 10)
            snapped_y = max(0, (new_pos.y() // 10) * 10)
            self.move(snapped_x, snapped_y)
            if self.ArchitectEngine:
                self.ArchitectEngine.UpdateInspectorPanel()

    def mouseReleaseEvent(self, event):
        self.IsDragging = False

    def UpdateSelectionVisuals(self, is_selected):
        self.IsSelected = is_selected
        accent = Palette.Buttons[4] if len(Palette.Buttons) > 4 else "#FFCC33"
        if is_selected:
            self.setStyleSheet(f"background: transparent; border: 2px dashed {accent}; border-radius: 4px;")
        else:
            self.setStyleSheet("background: transparent; border: none;")

    def ExportDict(self):
        return {
            "type": self.PrimitiveType,
            "text": self.LabelText,
            "number": self.ChipNumber,
            "color": self.ColorHex,
            "x": self.x(),
            "y": self.y(),
            "w": self.width(),
            "h": self.height(),
        }


# =========================================================================
# ГОЛОВНИЙ ДВИГУН АРХІТЕКТОРА (TITANIUM ARCHITECT ENGINE)
# =========================================================================

class TitaniumArchitectEngine(LCARSProgramPanel):
    """Повнофункціональне середовище візуального редагування інтерфейсів LCARS."""

    def __init__(self, EraRef=None, FactionRef=None, ParentNode=None):
        self.ActiveNodes: list[DraggableNode] = []
        self.SelectedNode: DraggableNode | None = None
        self.StatusMsgLabel = None
        self.StorageDir = REPO_ROOT / "storage" / "layouts"
        self.StorageDir.mkdir(parents=True, exist_ok=True)
        self.CurrentLayoutFile = self.StorageDir / "custom_desktop.json"

        super().__init__(
            TitleTextStr="LCARS INTERFACE CONSTRUCTOR & DESIGN STUDIO // EDIT MODE",
            EraRef=EraRef,
            FactionRef=FactionRef,
            AccentColorStr="#FF9933",
            ParentNode=ParentNode
        )

    def SetStatus(self, text: str):
        if hasattr(self, "StatusMsgLabel") and self.StatusMsgLabel and hasattr(self.StatusMsgLabel, "SetText"):
            self.StatusMsgLabel.SetText(text)

    def BuildUI(self, MainLayout):
        # 1. ВЕРХНЯ ПАНЕЛЬ ДІЙ (ACTION BAR)
        ActionBar = Segment(Parent=self)
        ActionBar.widget.setStyleSheet("background-color: #0d1218; border: 1px solid #1a2936; border-radius: 4px;")
        ActLayout = LCARS.Horizontal(ActionBar.widget)
        ActLayout.setContentsMargins(10, 6, 10, 6)
        ActLayout.setSpacing(8)

        # Кнопки збереження, завантаження, генерації коду Python
        BtnSave = LCARSButton(Text="SAVE CHIP", Form=LCARSButton.Soft, Number="47-01", Parent=ActionBar.widget)
        BtnSave.widget.setFixedHeight(34)
        BtnSave.Clicked.Connect(self.SaveToDatabaseChip)
        ActLayout.addWidget(BtnSave.widget)

        BtnGenPy = LCARSButton(Text="EXPORT CODE", Form=LCARSButton.Soft, Number="47-02", Parent=ActionBar.widget)
        BtnGenPy.widget.setFixedHeight(34)
        BtnGenPy.ColorGroup = "buttons"
        BtnGenPy.Clicked.Connect(self.WritePythonSourceFile)
        ActLayout.addWidget(BtnGenPy.widget)

        BtnLoad = LCARSButton(Text="LOAD CHIP", Form=LCARSButton.Soft, Number="47-03", Parent=ActionBar.widget)
        BtnLoad.widget.setFixedHeight(34)
        BtnLoad.Clicked.Connect(self.LoadFromDatabaseChip)
        ActLayout.addWidget(BtnLoad.widget)

        BtnApply = LCARSButton(Text="APPLY LAYOUT", Form=LCARSButton.Soft, Number="47-04", Parent=ActionBar.widget)
        BtnApply.widget.setFixedHeight(34)
        BtnApply.Clicked.Connect(self.ApplyToDesktop)
        ActLayout.addWidget(BtnApply.widget)

        BtnClear = LCARSButton(Text="CLEAR CANVAS", Form=LCARSButton.Soft, Number="47-05", Parent=ActionBar.widget)
        BtnClear.widget.setFixedHeight(34)
        BtnClear.ColorGroup = "red"
        BtnClear.Clicked.Connect(self.ClearCanvas)
        ActLayout.addWidget(BtnClear.widget)

        ActLayout.addStretch(1)

        self.StatusMsgLabel = LCARSLabel(Text="DESIGN STUDIO READY // EDITING ENABLED", Color=Palette.Buttons[2], FontSize=10, Parent=ActionBar.widget)
        ActLayout.addWidget(self.StatusMsgLabel.widget)

        MainLayout.addWidget(ActionBar.widget)

        # 2. ПАЛІТРА ПРИМІТИВІВ (TOOLBOX PALETTE)
        Toolbox = Segment(Parent=self)
        Toolbox.widget.setStyleSheet("background-color: #06090e; border: 1px solid #112233; border-radius: 4px;")
        ToolLayout = LCARS.Horizontal(Toolbox.widget)
        ToolLayout.setContentsMargins(8, 4, 8, 4)
        ToolLayout.setSpacing(6)

        PalTitle = LCARSLabel(Text="ADD ELEMENT:", Color=Palette.Buttons[4], FontSize=11, Parent=Toolbox.widget)
        ToolLayout.addWidget(PalTitle.widget)

        ToolItems = [
            ("BUTTON", "BUTTON", Palette.Buttons[0]),
            ("PILL", "PILL", Palette.Buttons[1]),
            ("ELBOW", "ELBOW", Palette.Buttons[3]),
            ("BAR", "BAR", Palette.Buttons[4]),
            ("LABEL", "LABEL", Palette.Buttons[2]),
            ("CARD", "CARD", Palette.Buttons[6]),
        ]

        for p_type, label, col in ToolItems:
            btn = LCARSButton(Text=label, Form=LCARSButton.Soft, Number="", Parent=Toolbox.widget)
            btn.widget.setFixedHeight(30)
            btn.Clicked.Connect(lambda *_, t=p_type: self.AddNode(t))
            ToolLayout.addWidget(btn.widget)

        ToolLayout.addStretch(1)
        MainLayout.addWidget(Toolbox.widget)

        # 3. ЦЕНТРАЛЬНА ЧАСТИНА: ПОЛОТНО + ПАНЕЛЬ ВЛАСТИВОСТЕЙ (CANVAS + INSPECTOR)
        CenterRow = Segment(Parent=self)
        CenterRow.widget.setStyleSheet("background-color: #000000; border: none;")
        CenterLayout = LCARS.Horizontal(CenterRow.widget)
        CenterLayout.setContentsMargins(0, 0, 0, 0)
        CenterLayout.setSpacing(10)

        # 3.1. Робоче полотно (Canvas)
        self.Canvas = Segment(Parent=CenterRow.widget)
        self.Canvas.widget.setStyleSheet(
            "background-color: #050508; border: 1px solid #223344; border-radius: 6px; "
            "background-image: radial-gradient(#15202b 1px, transparent 1px); background-size: 20px 20px;"
        )
        CenterLayout.addWidget(self.Canvas.widget, 4)

        # 3.2. Панель інспектора властивостей (Inspector)
        self.Inspector = Segment(Parent=CenterRow.widget)
        self.Inspector.widget.setFixedWidth(280)
        self.Inspector.widget.setStyleSheet("background-color: #0a0e14; border: 1px solid #1a2936; border-radius: 6px;")
        InspLayout = LCARS.Vertical(self.Inspector.widget)
        InspLayout.setContentsMargins(12, 12, 12, 12)
        InspLayout.setSpacing(8)

        InspTitle = LCARSLabel(Text="◤ ELEMENT INSPECTOR", Color=Palette.Buttons[4], FontSize=13, Parent=self.Inspector.widget)
        InspLayout.addWidget(InspTitle.widget)

        self.InspType = LCARSLabel(Text="TYPE: NONE SELECTED", Color="#8899AA", FontSize=10, Parent=self.Inspector.widget)
        InspLayout.addWidget(self.InspType.widget)

        self.InspGeom = LCARSLabel(Text="POSITION: 0, 0 | SIZE: 0x0", Color="#8899AA", FontSize=9, Parent=self.Inspector.widget)
        InspLayout.addWidget(self.InspGeom.widget)

        # Поле тексту
        LblText = LCARSLabel(Text="LABEL TEXT:", Color=Palette.Buttons[1], FontSize=10, Parent=self.Inspector.widget)
        InspLayout.addWidget(LblText.widget)
        self.InputText = LCARS.LineEdit(self.Inspector.widget)
        self.InputText.setStyleSheet("background-color: #111a24; color: #99CCFF; border: 1px solid #336699; padding: 4px; border-radius: 3px;")
        InspLayout.addWidget(self.InputText)

        # Поле чіпа
        LblChip = LCARSLabel(Text="CHIP NUMBER:", Color=Palette.Buttons[1], FontSize=10, Parent=self.Inspector.widget)
        InspLayout.addWidget(LblChip.widget)
        self.InputChip = LCARS.LineEdit(self.Inspector.widget)
        self.InputChip.setStyleSheet("background-color: #111a24; color: #99CCFF; border: 1px solid #336699; padding: 4px; border-radius: 3px;")
        InspLayout.addWidget(self.InputChip)

        # Розміри: Ширина та Висота
        SizeRow = Segment(Parent=self.Inspector.widget)
        SizeRow.widget.setStyleSheet("background-color: transparent; border: none;")
        SRLay = LCARS.Horizontal(SizeRow.widget)
        SRLay.setContentsMargins(0, 0, 0, 0)
        SRLay.setSpacing(6)

        self.InputW = LCARS.SpinBox(SizeRow.widget)
        self.InputW.setRange(40, 1000)
        self.InputW.setValue(180)
        self.InputW.setStyleSheet("background-color: #111a24; color: #FFF; border: 1px solid #336699;")
        SRLay.addWidget(self.InputW)

        self.InputH = LCARS.SpinBox(SizeRow.widget)
        self.InputH.setRange(20, 800)
        self.InputH.setValue(46)
        self.InputH.setStyleSheet("background-color: #111a24; color: #FFF; border: 1px solid #336699;")
        SRLay.addWidget(self.InputH)
        InspLayout.addWidget(SizeRow.widget)

        # Кнопка застосування змін
        BtnApplyProp = LCARSButton(Text="APPLY CHANGES", Form=LCARSButton.Soft, Number="", Parent=self.Inspector.widget)
        BtnApplyProp.widget.setFixedHeight(34)
        BtnApplyProp.Clicked.Connect(self.ApplyNodeProperties)
        InspLayout.addWidget(BtnApplyProp.widget)

        InspLayout.addStretch(1)

        # Кнопка видалення елемента
        BtnDelete = LCARSButton(Text="PURGE ELEMENT", Form=LCARSButton.Soft, Number="", Parent=self.Inspector.widget)
        BtnDelete.widget.setFixedHeight(32)
        BtnDelete.ColorGroup = "red"
        BtnDelete.Clicked.Connect(self.DeleteSelectedNode)
        InspLayout.addWidget(BtnDelete.widget)

        CenterLayout.addWidget(self.Inspector.widget, 1)
        MainLayout.addWidget(CenterRow.widget, 1)

        # Автозавантаження образу чіпа з бази даних
        self.LoadFromDatabaseChip("ISO-UI-DESKTOP")

    # ==========================================================
    # ОПЕРАЦІЇ З ВУЗЛАМИ ДИЗАЙНУ
    # ==========================================================

    def AddNode(self, PType, Label="NEW ELEMENT", Number="47", ColorHex=None, X=50, Y=50, W=200, H=48):
        Col = ColorHex or RandomButtonColor("LCARS_25TH")
        Node = DraggableNode(
            ParentCanvas=self.Canvas.widget,
            ArchitectRef=self,
            PrimitiveType=PType,
            LabelText=Label,
            Number=Number,
            ColorHex=Col,
            PosX=X,
            PosY=Y,
            Width=W,
            Height=H
        )
        self.ActiveNodes.append(Node)
        self.SelectActiveNode(Node)
        return Node

    def SelectActiveNode(self, Node: DraggableNode):
        for n in self.ActiveNodes:
            n.UpdateSelectionVisuals(False)
        self.SelectedNode = Node
        Node.UpdateSelectionVisuals(True)
        self.UpdateInspectorPanel()

    def UpdateInspectorPanel(self):
        if not self.SelectedNode:
            return
        n = self.SelectedNode
        if hasattr(self.InspType, "SetText"):
            self.InspType.SetText(f"TYPE: {n.PrimitiveType}")
        if hasattr(self.InspGeom, "SetText"):
            self.InspGeom.SetText(f"POSITION: {n.x()}, {n.y()} | SIZE: {n.width()}x{n.height()}")
        self.InputText.setText(n.LabelText)
        self.InputChip.setText(n.ChipNumber)
        self.InputW.setValue(n.width())
        self.InputH.setValue(n.height())

    def ApplyNodeProperties(self):
        if not self.SelectedNode:
            return
        n = self.SelectedNode
        n.LabelText = self.InputText.text().strip() or "ELEMENT"
        n.ChipNumber = self.InputChip.text().strip()
        new_w = self.InputW.value()
        new_h = self.InputH.value()

        # Оновлення геометрії
        n.resize(new_w, new_h)

        # Перебудова графічного елемента всередині вузла
        if hasattr(n.PrimitiveWidget, "deleteLater"):
            n.PrimitiveWidget.deleteLater()
        n.PrimitiveWidget = n.BuildPrimitive(n.PrimitiveType, n.LabelText, n.ChipNumber, n.ColorHex)
        if n.PrimitiveWidget:
            n.NodeLayout.addWidget(n.PrimitiveWidget.widget if hasattr(n.PrimitiveWidget, "widget") else n.PrimitiveWidget)

        self.UpdateInspectorPanel()
        self.SetStatus("ELEMENT PARAMETERS APPLIED // ACTIVE")

    def DeleteSelectedNode(self):
        if self.SelectedNode:
            node = self.SelectedNode
            if node in self.ActiveNodes:
                self.ActiveNodes.remove(node)
            node.deleteLater()
            self.SelectedNode = None
            if hasattr(self.InspType, "SetText"):
                self.InspType.SetText("TYPE: NONE SELECTED")
            if hasattr(self.InspGeom, "SetText"):
                self.InspGeom.SetText("POSITION: 0, 0 | SIZE: 0x0")
            self.SetStatus("ELEMENT PURGED FROM CANVAS")

    def ClearCanvas(self):
        for n in list(self.ActiveNodes):
            n.deleteLater()
        self.ActiveNodes.clear()
        self.SelectedNode = None
        self.SetStatus("CANVAS CLEARED")

    # ==========================================================
    # ПЕРСИСТЕНТНІСТЬ У БАЗІ ДАНИХ ТА ГЕНЕРАЦІЯ PYTHON-КОДУ
    # ==========================================================

    def GeneratePythonCode(self, ClassName="GeneratedLCARSScreen", ScreenTitle="LCARS GENERATED SCREEN") -> str:
        """Генерує чистий, валідний код Python для створення вікна інтерфейсу."""
        lines = [
            "# ◤ LCARS GENERATED SCREEN INTERFACE 🖖",
            "# Generated automatically by LCARS Titanium Interface Architect",
            "# Standard: Pure LCARS Component Architecture",
            "",
            "from __future__ import annotations",
            "import sys",
            "from pathlib import Path",
            "",
            "from lcars.base.type import LCARS",
            "from lcars.base.default import Palette",
            "from lcars.base.interface import LCARSProgramPanel, Segment",
            "from lcars.base.component import LCARSButton, LCARSLabel, LCARSElbow, LCARSBar",
            "",
            f"class {ClassName}(LCARSProgramPanel):",
            f"    \"\"\"{ScreenTitle}\"\"\"",
            "",
            "    def __init__(self, EraRef=None, FactionRef=None, ParentNode=None):",
            "        super().__init__(",
            f"            TitleTextStr=\"{ScreenTitle}\",",
            "            EraRef=EraRef,",
            "            FactionRef=FactionRef,",
            "            AccentColorStr=\"#FF9933\",",
            "            ParentNode=ParentNode",
            "        )",
            "",
            "    def BuildUI(self, MainLayout):",
            "        # Головне полотно екрана",
            "        Canvas = Segment(Parent=self)",
            "        Canvas.widget.setStyleSheet(\"background-color: #050508; border: 1px solid #1a2936; border-radius: 6px;\")",
            "        MainLayout.addWidget(Canvas.widget, 1)",
            "",
        ]

        for i, node in enumerate(self.ActiveNodes):
            el = node.ExportDict()
            ptype = el["type"]
            text = str(el.get("text", "NODE")).replace('"', '\\"')
            num = str(el.get("number", "47")).replace('"', '\\"')
            col = el.get("color", "#FF9900")
            x, y, w, h = el.get("x", 50), el.get("y", 50), el.get("w", 200), el.get("h", 46)

            lines.append(f"        # Element {i+1}: {ptype} [{text}]")
            if ptype == "BUTTON":
                lines.append(f"        btn_{i} = LCARSButton(Text=\"{text}\", Number=\"{num}\", Form=LCARSButton.Soft, Parent=Canvas.widget)")
                lines.append(f"        btn_{i}.widget.setGeometry({x}, {y}, {w}, {h})")
                lines.append(f"        btn_{i}.widget.show()")
            elif ptype == "PILL":
                lines.append(f"        pill_{i} = LCARSButton(Text=\"{text}\", Number=\"{num}\", Form=LCARSButton.Pill, Parent=Canvas.widget)")
                lines.append(f"        pill_{i}.widget.setGeometry({x}, {y}, {w}, {h})")
                lines.append(f"        pill_{i}.widget.show()")
            elif ptype == "LABEL":
                lines.append(f"        lbl_{i} = LCARSLabel(Text=\"{text}\", Color=\"{col}\", FontSize=12, Parent=Canvas.widget)")
                lines.append(f"        lbl_{i}.widget.setGeometry({x}, {y}, {w}, {h})")
                lines.append(f"        lbl_{i}.widget.show()")
            elif ptype == "ELBOW":
                lines.append(f"        elbow_{i} = LCARSElbow(Direction=\"top-left\", Color=\"{col}\", Thickness=32, Radius=24, Parent=Canvas.widget)")
                lines.append(f"        elbow_{i}.widget.setGeometry({x}, {y}, {w}, {h})")
                lines.append(f"        elbow_{i}.widget.show()")
            elif ptype == "BAR":
                lines.append(f"        bar_{i} = LCARSBar(Type=\"rect\", Color=\"{col}\", Height={h}, Parent=Canvas.widget)")
                lines.append(f"        bar_{i}.widget.setGeometry({x}, {y}, {w}, {h})")
                lines.append(f"        bar_{i}.widget.show()")
            elif ptype == "CARD":
                lines.append(f"        card_{i} = Segment(Parent=Canvas.widget)")
                lines.append(f"        card_{i}.widget.setGeometry({x}, {y}, {w}, {h})")
                lines.append(f"        card_{i}.widget.setStyleSheet(\"background-color: #111118; border-left: 4px solid {col}; border-radius: 4px;\")")
                lines.append(f"        clay_{i} = LCARS.Vertical(card_{i}.widget)")
                lines.append(f"        clay_{i}.setContentsMargins(8, 6, 8, 6)")
                lines.append(f"        tlbl_{i} = LCARSLabel(Text=\"{text}\", Color=\"#FFFFFF\", FontSize=11, Parent=card_{i}.widget)")
                lines.append(f"        clay_{i}.addWidget(tlbl_{i}.widget)")
                lines.append(f"        slbl_{i} = LCARSLabel(Text=\"CHIP {num} // OPERATIONAL\", Color=\"#8899AA\", FontSize=8, Parent=card_{i}.widget)")
                lines.append(f"        clay_{i}.addWidget(slbl_{i}.widget)")
                lines.append(f"        card_{i}.widget.show()")
            lines.append("")

        lines.extend([
            "if __name__ == '__main__':",
            "    app = LCARS.Application.instance() or LCARS.Application(sys.argv)",
            f"    screen = {ClassName}()",
            "    screen.show()",
            "    sys.exit(app.exec())",
            ""
        ])

        return "\n".join(lines)

    def WritePythonSourceFile(self, TargetPath=None) -> str:
        """Генерує та перезаписує файл вихідного коду Python."""
        OutputFile = Path(TargetPath) if TargetPath else REPO_ROOT / "programs" / "custom_screen.py"
        OutputFile.parent.mkdir(parents=True, exist_ok=True)
        py_code = self.GeneratePythonCode()
        try:
            with open(OutputFile, "w", encoding="utf-8") as f:
                f.write(py_code)
            self.SetStatus(f"PYTHON FILE GENERATED & SAVED: {OutputFile.name}")
            return py_code
        except Exception as e:
            self.SetStatus(f"PYTHON EXPORT ERROR: {e}")
            return py_code

    def SaveToDatabaseChip(self, ChipId="ISO-UI-DESKTOP", ScreenName="DESKTOP", Title="STARFLEET DESKTOP"):
        """Зберігає повний стан інтерфейсу як ізолінійний образ чіпа в SQLite БД без створення тимчасових файлів."""
        elements = [n.ExportDict() for n in self.ActiveNodes]
        try:
            mem = GetMemory()
            ok = mem.SaveUIChip(ChipId, ScreenName, Title, elements, "")
            if ok:
                self.SetStatus(f"CHIP IMAGE STORED IN DB: [{ChipId}] ({len(elements)} NODES)")
            else:
                self.SetStatus(f"DB SAVE FAILED: [{ChipId}]")
        except Exception as e:
            self.SetStatus(f"DB ERROR: {e}")

    def LoadFromDatabaseChip(self, ChipIdOrScreen="ISO-UI-DESKTOP"):
        """Відтворює інтерфейс безпосередньо з образу чіпа в базі даних SQLite."""
        try:
            mem = GetMemory()
            chip_data = mem.LoadUIChip(ChipIdOrScreen)
            if not chip_data or not chip_data.get("elements"):
                self.LoadDefaultTemplate()
                return

            self.ClearCanvas()
            for item in chip_data.get("elements", []):
                self.AddNode(
                    PType=item.get("type", "BUTTON"),
                    Label=item.get("text", "ELEMENT"),
                    Number=item.get("number", "47"),
                    ColorHex=item.get("color", Palette.Buttons[1]),
                    X=item.get("x", 50),
                    Y=item.get("y", 50),
                    W=item.get("w", 200),
                    H=item.get("h", 48)
                )
            self.SetStatus(f"CHIP RESTORED FROM DB: [{chip_data.get('chip_id')}] ({len(self.ActiveNodes)} NODES)")
        except Exception as e:
            self.SetStatus(f"DB LOAD ERROR: {e}")

    def LoadDefaultTemplate(self):
        self.ClearCanvas()
        Template = [
            ("BUTTON", "SCIENCE WORKBENCH", "47-01", Palette.Buttons[1], 40, 40, 220, 46),
            ("BUTTON", "INTERFACE DESIGNER", "47-02", Palette.Buttons[4], 280, 40, 220, 46),
            ("BUTTON", "COMMAND CONSOLE", "47-03", Palette.Buttons[0], 40, 100, 220, 46),
            ("BUTTON", "SOFTWARE CATALOG", "47-04", Palette.Buttons[2], 280, 100, 220, 46),
            ("CARD", "ISOLINEAR STORAGE", "47-05", Palette.Buttons[3], 40, 160, 220, 60),
            ("CARD", "COMMAND BRIDGE", "47-06", Palette.Buttons[6], 280, 160, 220, 60),
        ]
        for p_type, label, num, col, x, y, w, h in Template:
            self.AddNode(p_type, label, num, col, x, y, w, h)
        self.SaveToDatabaseChip()

    def ApplyToDesktop(self):
        self.SaveToDatabaseChip()
        ODN.Emit("System.LayoutUpdated", [n.ExportDict() for n in self.ActiveNodes])
        self.SetStatus("CHIP BROADCASTED TO ACTIVE DESKTOP // SYNCHRONIZED")


# =========================================================================
# ТОЧКА ВХОДУ (STANDALONE RUNNER)
# =========================================================================

if __name__ == "__main__":
    AppClass = LCARS.Application
    AppInstance = AppClass.instance() or AppClass(sys.argv)
    Studio = TitaniumArchitectEngine()
    Studio.show()
    sys.exit(AppInstance.exec())


