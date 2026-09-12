# ◤ TITANIUM UI ARCHITECT — v45.20 // MASTER DESIGNER 🖖
# LCARS Framework :: DEVELOPMENT_ENVIRONMENT // UI_CONSTRUCTION // NO_Q
# ─────────────────────────────────────────────────────────────────────────────
# ОПИС: Повнофункціональне середовище для проектування інтерфейсів Titanium.
# ФУНКЦІЇ: Редактор властивостей, генератор коду, палітри фракцій.
# СТАНДАРТ: Titanium CamelCase + Zero-Except (Architect Mode).
# ─────────────────────────────────────────────────────────────────────────────

import sys
import json
from typing import List, Optional, Dict
from lcars.base.register import registry
from lcars.base.types import ODN, Matrix, Visual, Signal, Primitives, Chassis, Directive
from lcars.base.components import LCARSPadd, LCARSButton, LCARSLabel, LCARSElbow, LCARSPill, LCARSScanningBar
from lcars.base.defaults import TitanPalette
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtWidgets import QFileDialog, QInputDialog, QColorDialog

class UIArchitect(LCARSPadd):
    # ГОЛОВНИЙ ВУЗОЛ КОНСТРУКЦІЇ (Master Architect Node)
    def __init__(self, ParentNode=None):
        super().__init__("◤ TITANIUM UI ARCHITECT v45.20", color=TitanPalette.Scientific[0], ParentNode=ParentNode)
        self.resize(1400, 950)
        
        # СТАН КОНСТРУКТОРА
        self.ComponentStack: List[Visual.Widget] = []
        self.SelectedNode: Optional[Visual.Widget] = None
        self.DraggingNode: Optional[Visual.Widget] = None
        self.DragStartPos: QPoint = QPoint()
        self.NodeStartPos: QPoint = QPoint()
        
        self.viewport().setStyleSheet("background: #000000; border: none;")
        self.MainLayout = self.ViewportLayout
        self.MainLayout.setContentsMargins(10, 10, 10, 10)
        self.MainLayout.setSpacing(10)
        
        self.BuildInterface()
        self.Log("ARCHITECT ENGINE ONLINE. READY FOR CONSTRUCTION.")

    def BuildInterface(self):
        # 1. HEADER (Command Row)
        HeaderRow = ODN.Horizontal()
        HeaderRow.addWidget(LCARSLabel("◤ UI CONSTRUCTION MATRIX", size=14, color=TitanPalette.Scientific[1]), 1)
        
        self.BtnExport = LCARSButton("◤ GENERATE CODE", ColorHexStr=TitanPalette.Scientific[2], shape="rect")
        self.BtnExport.clicked.connect(self.ExportUiCode)
        HeaderRow.addWidget(self.BtnExport)
        
        self.BtnExit = LCARSButton("◤ DISCONNECT", ColorHexStr=TitanPalette.Alert[1], shape="rect")
        self.BtnExit.clicked.connect(self.close)
        HeaderRow.addWidget(self.BtnExit)
        
        # ADD SAVE/LOAD BUTTONS
        self.BtnSave = LCARSButton("◤ SAVE", ColorHexStr=TitanPalette.Green[0], shape="rect")
        self.BtnSave.clicked.connect(self.SaveLayout)
        HeaderRow.addWidget(self.BtnSave)
        
        self.BtnLoad = LCARSButton("◤ LOAD", ColorHexStr=TitanPalette.Yellow[0], shape="rect")
        self.BtnLoad.clicked.connect(self.LoadLayout)
        HeaderRow.addWidget(self.BtnLoad)
        
        self.MainLayout.addLayout(HeaderRow)

        # 2. MAIN WORKSPACE
        Workspace = ODN.Horizontal()
        Workspace.setSpacing(10)

        # A. PALETTE (Left Sidebar)
        PaletteFrame = Matrix()
        PaletteFrame.setFixedWidth(280)
        PaletteLayout = ODN.Vertical(PaletteFrame)
        PaletteLayout.setSpacing(5)
        
        PaletteLayout.addWidget(LCARSLabel("◤ COMPONENT PALETTE", size=10, color="white"))
        
        Components = [
            ("ADD BUTTON", TitanPalette.Buttons[1], "Button"),
            ("ADD LABEL", TitanPalette.Buttons[2], "Label"),
            ("ADD ELBOW", TitanPalette.Alert[0], "Elbow"),
            ("ADD PILL", TitanPalette.Panels[0], "Pill"),
            ("ADD SCANNER", TitanPalette.Scientific[1], "Scanner")
        ]
        
        for Lbl, Col, Type in Components:
            Btn = LCARSButton(f"◤ {Lbl}", ColorHexStr=Col, shape="rect")
            Btn.clicked.connect(lambda t=Type: self.AddComponent(t))
            PaletteLayout.addWidget(Btn)

        PaletteLayout.addSpacing(20)
        PaletteLayout.addWidget(LCARSLabel("◤ FRACTION DNA", size=10, color="white"))
        
        Factions = [
            ("UNITED FEDERATION", "#3399FF"),
            ("ROMULAN EMPIRE", "#00FF88"),
            ("KLINGON EMPIRE", "#FF3300"),
            ("CARDASSIAN UNION", "#FFCC66")
        ]
        for Lbl, Col in Factions:
            Btn = LCARSButton(Lbl, ColorHexStr=Col, shape="rect")
            Btn.clicked.connect(lambda c=Col: self.ApplyFractionDna(c))
            PaletteLayout.addWidget(Btn)

        PaletteLayout.addStretch()
        Workspace.addWidget(PaletteFrame)

        # B. CANVAS (Center Area)
        self.Canvas = Matrix()
        self.Canvas.setStyleSheet("background: #020205; border: 1px solid #1A2535; border-radius: 10px;")
        self.CanvasLayout = ODN.Vertical(self.Canvas)
        self.CanvasLayout.setContentsMargins(40, 40, 40, 40)
        self.CanvasLayout.setSpacing(15)
        Workspace.addWidget(self.Canvas, 1)

        # C. PROPERTIES (Right Sidebar)
        self.PropFrame = Matrix()
        self.PropFrame.setFixedWidth(300)
        self.PropLayout = ODN.Vertical(self.PropFrame)
        self.PropLayout.setSpacing(10)
        
        self.PropLayout.addWidget(LCARSLabel("◤ NODE PROPERTIES", size=10, color="white"))
        
        # Property: Text
        self.PropLayout.addWidget(LCARSLabel("TEXT:", size=9, color="#666"))
        self.TextEdit = registry.Node("Technical.Visual.Output")()
        self.TextEdit.setFixedHeight(40)
        self.TextEdit.textChanged.connect(self.OnUpdateProperty)
        self.PropLayout.addWidget(self.TextEdit)
        
        # Property: Color
        self.PropLayout.addWidget(LCARSLabel("COLOR:", size=9, color="#666"))
        ColorRow = ODN.Horizontal()
        self.BtnColorPick = LCARSButton("PICK COLOR", ColorHexStr=TitanPalette.Buttons[2], shape="rect")
        self.BtnColorPick.clicked.connect(self.OnPickColor)
        ColorRow.addWidget(self.BtnColorPick)
        self.LblCurrentColor = LCARSLabel("#------", size=8, color="white")
        ColorRow.addWidget(self.LblCurrentColor)
        self.PropLayout.addLayout(ColorRow)
        
        # Property: Position
        self.PropLayout.addWidget(LCARSLabel("POSITION (X,Y):", size=9, color="#666"))
        PosRow = ODN.Horizontal()
        self.SpinX = registry.Node("Technical.Visual.Spin")()
        self.SpinX.setRange(0, 2000)
        self.SpinX.valueChanged.connect(self.OnPositionChanged)
        PosRow.addWidget(self.SpinX)
        self.SpinY = registry.Node("Technical.Visual.Spin")()
        self.SpinY.setRange(0, 2000)
        self.SpinY.valueChanged.connect(self.OnPositionChanged)
        PosRow.addWidget(self.SpinY)
        self.PropLayout.addLayout(PosRow)
        
        # Property: Size
        self.PropLayout.addWidget(LCARSLabel("SIZE (W,H):", size=9, color="#666"))
        SizeRow = ODN.Horizontal()
        self.SpinW = registry.Node("Technical.Visual.Spin")()
        self.SpinW.setRange(10, 1000)
        self.SpinW.valueChanged.connect(self.OnSizeChanged)
        SizeRow.addWidget(self.SpinW)
        self.SpinH = registry.Node("Technical.Visual.Spin")()
        self.SpinH.setRange(10, 1000)
        self.SpinH.valueChanged.connect(self.OnSizeChanged)
        SizeRow.addWidget(self.SpinH)
        self.PropLayout.addLayout(SizeRow)
        
        # Status Log
        self.StatusLog = Visual.Text()
        self.StatusLog.setReadOnly(True)
        self.StatusLog.setStyleSheet("background: #000; color: #00FF81; font-family: 'Consolas'; font-size: 9pt;")
        self.PropLayout.addWidget(self.StatusLog, 1)
        
        # Buttons
        self.BtnDelete = LCARSButton("DELETE NODE", ColorHexStr=TitanPalette.Alert[1], shape="rect")
        self.BtnDelete.clicked.connect(self.DeleteSelectedNode)
        self.PropLayout.addWidget(self.BtnDelete)
        
        self.BtnClear = LCARSButton("PURGE CANVAS", ColorHexStr=TitanPalette.Alert[0], shape="rect")
        self.BtnClear.clicked.connect(self.ClearCanvas)
        self.PropLayout.addWidget(self.BtnClear)

        Workspace.addWidget(self.PropFrame)
        self.MainLayout.addLayout(Workspace, 1)

    def AddComponent(self, TypeStr: str):
        self.Log(f"INITIATING_CONSTRUCTION: {TypeStr}")
        
        NewNode = None
        if TypeStr == "Button":
            NewNode = LCARSButton(f"UNIT {len(self.ComponentStack)+1}", ColorHexStr=TitanPalette.Buttons[1])
            NewNode.setFixedSize(120, 50)
        elif TypeStr == "Label":
            NewNode = LCARSLabel(f"◤ DATA STREAM {len(self.ComponentStack)+1}", FontSizeVal=14)
            NewNode.setFixedSize(200, 30)
        elif TypeStr == "Elbow":
            NewNode = LCARSElbow("top-left", ColorHexStr=TitanPalette.Alert[0])
            NewNode.setFixedSize(120, 120)
        elif TypeStr == "Pill":
            NewNode = LCARSPill(ColorHexStr=TitanPalette.Panels[0])
            NewNode.setFixedSize(100, 40)
        elif TypeStr == "Scanner":
            NewNode = LCARSScanningBar(ColorHexStr=TitanPalette.Scientific[1])
            NewNode.setFixedSize(200, 30)

        if NewNode:
            # Add to canvas with absolute positioning
            NewNode.setParent(self.Canvas)
            x_pos = 50 + (len(self.ComponentStack) % 5) * 140
            y_pos = 50 + (len(self.ComponentStack) // 5) * 80
            NewNode.move(x_pos, y_pos)
            NewNode.show()
            
            # Enable dragging
            NewNode.mousePressEvent = lambda e, n=NewNode: self.OnNodeMousePress(e, n)
            NewNode.mouseMoveEvent = lambda e, n=NewNode: self.OnNodeMouseMove(e, n)
            NewNode.mouseReleaseEvent = lambda e, n=NewNode: self.OnNodeMouseRelease(e, n)
            
            self.ComponentStack.append(NewNode)
            self.SelectNode(NewNode)
            self.Log(f"NODE_PLACED: {TypeStr} at ({x_pos},{y_pos})")
    
    def SelectNode(self, Node):
        self.SelectedNode = Node
        self.UpdatePropertyPanel()
    
    def UpdatePropertyPanel(self):
        if self.SelectedNode:
            # Update text
            Text = ""
            if hasattr(self.SelectedNode, 'text'):
                Text = self.SelectedNode.text()
            elif hasattr(self.SelectedNode, 'TitleStr'):
                Text = self.SelectedNode.TitleStr
            self.TextEdit.setPlainText(Text)
            
            # Update position
            self.SpinX.setValue(self.SelectedNode.x())
            self.SpinY.setValue(self.SelectedNode.y())
            
            # Update size
            self.SpinW.setValue(self.SelectedNode.width())
            self.SpinH.setValue(self.SelectedNode.height())
    
    def OnNodeMousePress(self, Event, Node):
        if Event.button() == Qt.MouseButton.LeftButton:
            self.DraggingNode = Node
            self.DragStartPos = Event.pos()
            self.NodeStartPos = Node.pos()
            self.SelectNode(Node)
    
    def OnNodeMouseMove(self, Event, Node):
        if self.DraggingNode == Node:
            Delta = Event.pos() - self.DragStartPos
            NewPos = self.NodeStartPos + Delta
            Node.move(NewPos)
            self.SpinX.setValue(NewPos.x())
            self.SpinY.setValue(NewPos.y())
    
    def OnNodeMouseRelease(self, Event, Node):
        if Event.button() == Qt.MouseButton.LeftButton:
            self.DraggingNode = None
    
    def OnPositionChanged(self):
        if self.SelectedNode:
            self.SelectedNode.move(self.SpinX.value(), self.SpinY.value())
    
    def OnSizeChanged(self):
        if self.SelectedNode:
            self.SelectedNode.setFixedSize(self.SpinW.value(), self.SpinH.value())
    
    def OnPickColor(self):
        if self.SelectedNode and hasattr(self.SelectedNode, 'SetColor'):
            Color = QColorDialog.getColor()
            if Color.isValid():
                HexColor = Color.name()
                self.SelectedNode.SetColor(HexColor)
                self.LblCurrentColor.SetText(HexColor)
    
    def DeleteSelectedNode(self):
        if self.SelectedNode:
            self.Log(f"DELETING_NODE: {self.SelectedNode.__class__.__name__}")
            self.ComponentStack.remove(self.SelectedNode)
            self.SelectedNode.setParent(None)
            self.SelectedNode.deleteLater()
            self.SelectedNode = None
    
    def SaveLayout(self):
        Path, _ = QFileDialog.getSaveFileName(self, "Save Layout", "", "JSON (*.json)")
        if Path:
            Data = {
                'version': '1.0',
                'nodes': []
            }
            for Node in self.ComponentStack:
                NodeData = {
                    'type': Node.__class__.__name__,
                    'x': Node.x(),
                    'y': Node.y(),
                    'width': Node.width(),
                    'height': Node.height()
                }
                if hasattr(Node, 'text'):
                    NodeData['text'] = Node.text()
                Data['nodes'].append(NodeData)
            
            with open(Path, 'w') as F:
                json.dump(Data, F, indent=2)
            self.Log(f"LAYOUT_SAVED: {Path}")
    
    def LoadLayout(self):
        Path, _ = QFileDialog.getOpenFileName(self, "Load Layout", "", "JSON (*.json)")
        if Path:
            self.ClearCanvas()
            with open(Path, 'r') as F:
                Data = json.load(F)
            
            for NodeData in Data.get('nodes', []):
                TypeStr = NodeData['type'].replace('LCARS', '').upper()
                if 'BUTTON' in TypeStr:
                    self.AddComponent('Button')
                elif 'LABEL' in TypeStr:
                    self.AddComponent('Label')
                elif 'ELBOW' in TypeStr:
                    self.AddComponent('Elbow')
                elif 'PILL' in TypeStr:
                    self.AddComponent('Pill')
                elif 'SCAN' in TypeStr:
                    self.AddComponent('Scanner')
                
                if self.ComponentStack:
                    Node = self.ComponentStack[-1]
                    Node.move(NodeData.get('x', 50), NodeData.get('y', 50))
                    Node.setFixedSize(NodeData.get('width', 100), NodeData.get('height', 50))
                    if 'text' in NodeData and hasattr(Node, 'setText'):
                        Node.setText(NodeData['text'])
            
            self.Log(f"LAYOUT_LOADED: {Path}")

    def OnUpdateProperty(self):
        if self.SelectedNode:
            NewText = self.TextEdit.toPlainText()
            if hasattr(self.SelectedNode, 'setText'):
                self.SelectedNode.setText(NewText)
            elif hasattr(self.SelectedNode, 'SetText'):
                self.SelectedNode.SetText(NewText)
            elif hasattr(self.SelectedNode, 'TitleStr'):
                self.SelectedNode.TitleStr = NewText

    def ApplyFractionDna(self, ColorStr: str):
        self.Log(f"APPLYING_DNA: {ColorStr}")
        self.Canvas.setStyleSheet(f"background: #020205; border: 2px solid {ColorStr}; border-radius: 10px;")

    def ExportUiCode(self):
        self.Log("EXPORTING_TITANIUM_CODE...")
        Code = [
            "# ◤ TITANIUM GENERATED SCHEMATIC 🖖",
            "from lcars.base.types import Matrix, ODN",
            "from lcars.base.components import LCARSButton, LCARSLabel, LCARSElbow, LCARSPill, LCARSScanningBar\n",
            "class GeneratedInterface(Matrix):",
            "    def __init__(self, parent=None):",
            "        super().__init__(parent)",
            "        Layout = ODN.Vertical(self)",
            "        Layout.setContentsMargins(20, 20, 20, 20)",
            "        Layout.setSpacing(10)\n"
        ]
        
        for Node in self.ComponentStack:
            Type = Node.__class__.__name__
            # Get text if available
            Text = ""
            if hasattr(Node, 'text'): Text = Node.text()
            elif hasattr(Node, 'text_node'): Text = Node.text_node().text()
            
            Code.append(f"        Layout.addWidget({Type}(text='{Text}'))")
            
        FinalStr = "\n".join(Code)
        print("\n" + "═"*50 + "\n" + FinalStr + "\n" + "═"*50)
        self.Log("CODE_EXPORTED: See terminal output.")

    def ClearCanvas(self):
        self.Log("PURGING_ALL_NODES...")
        for Node in self.ComponentStack:
            Node.setParent(None)
            Node.deleteLater()
        self.ComponentStack = []
        self.SelectedNode = None

    def Log(self, Msg: str):
        self.StatusLog.appendHtml(f"<font color='#00FF81'>◤ {Msg.upper()}</font>")

# РЕЄСТРАЦІЯ
registry.Register("Technical.Visual.UIArchitect", UIArchitect)

if __name__ == "__main__":
    AppCls = registry.Node("Technical.Application")
    AppInst = AppCls.instance() or AppCls(sys.argv)
    
    Architect = UIArchitect()
    Architect.showFullScreen()
    sys.exit(AppInst.exec())
