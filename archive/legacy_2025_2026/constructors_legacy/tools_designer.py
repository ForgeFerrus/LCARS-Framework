# ◤ LCARS UI DESIGNER v2.0 — TITANIUM PADD BASED 🖖
# LCARS Framework :: VISUAL_DESIGNER // PADD_INTERFACE // NO_Q
# Based on LCARSPadd — uses native LCARS components only

import sys
import json
from pathlib import Path
from typing import List, Optional

# Add project root
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import LCARS Titanium components
from lcars.base.register import registry
from lcars.base.types import ODN, Matrix, Visual, Signal, Primitives
from lcars.base.components import LCARSFrame, LCARSButton, LCARSLabel, LCARSElbow, LCARSPill
from lcars.base.defaults import TitanPalette
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtWidgets import QMainWindow, QWidget, QFileDialog, QColorDialog, QTextEdit, QSpinBox


class LCARSDesigner(QMainWindow):
    """LCARS UI Designer — uses only native LCARS components."""
    
    def __init__(self, ParentNode=None):
        super().__init__(ParentNode)
        self.setWindowTitle("LCARS UI Designer v2.0")
        self.setStyleSheet("background-color: #000000;")
        self.resize(1600, 1000)
        
        # State
        self.ComponentStack: List[Visual.Widget] = []
        self.SelectedNode: Optional[Visual.Widget] = None
        self.DraggingNode: Optional[Visual.Widget] = None
        self.DragStartPos: QPoint = QPoint()
        self.NodeStartPos: QPoint = QPoint()
        
        # Central widget with LCARS styling
        self.CentralFrame = LCARSFrame()
        self.setCentralWidget(self.CentralFrame)
        self.MainLayout = ODN.Vertical(self.CentralFrame)
        self.MainLayout.setContentsMargins(10, 10, 10, 10)
        self.MainLayout.setSpacing(10)
        
        self.BuildInterface()
        self.Log("DESIGNER ONLINE. READY FOR CONSTRUCTION.")
    
    def BuildInterface(self):
        # === HEADER ===
        HeaderRow = ODN.Horizontal()
        HeaderRow.addWidget(LCARSLabel("◤ UI DESIGNER // TITANIUM ARCHITECT", Color=TitanPalette.Scientific[1], FontSize=14), 1)
        
        self.BtnSave = LCARSButton("SAVE", Type="rect", Color=TitanPalette.Accent[0])
        self.BtnSave.Clicked = self.SaveLayout
        HeaderRow.addWidget(self.BtnSave)
        
        self.BtnLoad = LCARSButton("LOAD", Type="rect", Color=TitanPalette.YellowAlert[0])
        self.BtnLoad.Clicked = self.LoadLayout
        HeaderRow.addWidget(self.BtnLoad)
        
        self.BtnExport = LCARSButton("EXPORT", Type="rect", Color=TitanPalette.Buttons[1])
        self.BtnExport.Clicked = self.ExportCode
        HeaderRow.addWidget(self.BtnExport)
        
        self.BtnExit = LCARSButton("EXIT", Type="rect", Color=TitanPalette.Alert[1])
        self.BtnExit.Clicked = self.close
        HeaderRow.addWidget(self.BtnExit)
        
        self.MainLayout.addLayout(HeaderRow)
        
        # === MAIN WORKSPACE ===
        Workspace = ODN.Horizontal()
        Workspace.setSpacing(10)
        
        # === LEFT PALETTE ===
        PaletteFrame = Matrix()
        PaletteFrame.setFixedWidth(260)
        PaletteLayout = ODN.Vertical(PaletteFrame)
        PaletteLayout.setSpacing(8)
        
        PaletteLayout.addWidget(LCARSLabel("◤ PALETTE", Color=TitanPalette.OrangeStd, FontSize=12))
        
        # Component buttons
        Components = [
            ("BUTTON", TitanPalette.Buttons[1], "Button"),
            ("LABEL", TitanPalette.Buttons[2], "Label"),
            ("ELBOW", TitanPalette.Alert[0], "Elbow"),
            ("PILL", TitanPalette.Panels[0], "Pill"),
        ]
        
        for Label, Color, Type in Components:
            Btn = LCARSButton(f"◤ {Label}", Type="rect", Color=Color)
            Btn.setFixedHeight(45)
            Btn.Clicked = lambda t=Type: self.AddComponent(t)
            PaletteLayout.addWidget(Btn)
        
        PaletteLayout.addSpacing(20)
        PaletteLayout.addWidget(LCARSLabel("◤ FACTIONS", Color="white", FontSize=10))
        
        # Faction colors
        Factions = [
            ("FEDERATION", "#3399FF"),
            ("KLINGON", "#FF3300"),
            ("ROMULAN", "#00FF88"),
        ]
        for Name, Color in Factions:
            Btn = LCARSButton(Name, Type="rounded", Color=Color)
            Btn.setFixedHeight(35)
            Btn.Clicked = lambda c=Color: self.ApplyFactionColor(c)
            PaletteLayout.addWidget(Btn)
        
        PaletteLayout.addStretch()
        Workspace.addWidget(PaletteFrame)
        
        # === CENTER CANVAS ===
        self.Canvas = Matrix()
        self.Canvas.setStyleSheet("background: #0A0A14; border: 2px solid #1A2535; border-radius: 10px;")
        self.Canvas.setMinimumSize(800, 700)
        Workspace.addWidget(self.Canvas, 1)
        
        # === RIGHT PROPERTIES ===
        PropFrame = Matrix()
        PropFrame.setFixedWidth(320)
        PropLayout = ODN.Vertical(PropFrame)
        PropLayout.setSpacing(10)
        
        PropLayout.addWidget(LCARSLabel("◤ PROPERTIES", Color=TitanPalette.OrangeStd, FontSize=12))
        
        # Text property
        PropLayout.addWidget(LCARSLabel("TEXT:", Color="#888", FontSize=9))
        self.TextEdit = QTextEdit()
        self.TextEdit.setFixedHeight(40)
        self.TextEdit.setStyleSheet("background: #1a1a2e; color: #fff; border: 1px solid #336699;")
        self.TextEdit.textChanged.connect(self.OnTextChanged)
        PropLayout.addWidget(self.TextEdit)
        
        # Color property
        PropLayout.addWidget(LCARSLabel("COLOR:", Color="#888", FontSize=9))
        self.BtnPickColor = LCARSButton("PICK COLOR", Type="rect", Color=TitanPalette.Buttons[2])
        self.BtnPickColor.Clicked = self.OnPickColor
        self.BtnPickColor.setFixedHeight(35)
        PropLayout.addWidget(self.BtnPickColor)
        
        # Position
        PropLayout.addWidget(LCARSLabel("POSITION (X,Y):", Color="#888", FontSize=9))
        PosRow = ODN.Horizontal()
        self.SpinX = QSpinBox()
        self.SpinX.setRange(0, 2000)
        self.SpinX.setStyleSheet("background: #1a1a2e; color: #fff; border: 1px solid #336699;")
        self.SpinX.valueChanged.connect(self.OnPositionChanged)
        PosRow.addWidget(self.SpinX)
        self.SpinY = QSpinBox()
        self.SpinY.setRange(0, 2000)
        self.SpinY.setStyleSheet("background: #1a1a2e; color: #fff; border: 1px solid #336699;")
        self.SpinY.valueChanged.connect(self.OnPositionChanged)
        PosRow.addWidget(self.SpinY)
        PropLayout.addLayout(PosRow)
        
        # Size
        PropLayout.addWidget(LCARSLabel("SIZE (W,H):", Color="#888", FontSize=9))
        SizeRow = ODN.Horizontal()
        self.SpinW = QSpinBox()
        self.SpinW.setRange(10, 1000)
        self.SpinW.setStyleSheet("background: #1a1a2e; color: #fff; border: 1px solid #336699;")
        self.SpinW.valueChanged.connect(self.OnSizeChanged)
        SizeRow.addWidget(self.SpinW)
        self.SpinH = QSpinBox()
        self.SpinH.setRange(10, 1000)
        self.SpinH.setStyleSheet("background: #1a1a2e; color: #fff; border: 1px solid #336699;")
        self.SpinH.valueChanged.connect(self.OnSizeChanged)
        SizeRow.addWidget(self.SpinH)
        PropLayout.addLayout(SizeRow)
        
        # Status log
        self.StatusLog = QTextEdit()
        self.StatusLog.setReadOnly(True)
        self.StatusLog.setStyleSheet("background: #000; color: #00FF81; font-family: 'Consolas'; font-size: 9pt;")
        PropLayout.addWidget(self.StatusLog, 1)
        
        # Delete button
        self.BtnDelete = LCARSButton("DELETE NODE", Type="rect", Color=TitanPalette.Alert[1])
        self.BtnDelete.Clicked = self.DeleteSelected
        self.BtnDelete.setFixedHeight(40)
        PropLayout.addWidget(self.BtnDelete)
        
        # Clear button
        self.BtnClear = LCARSButton("CLEAR ALL", Type="rect", Color=TitanPalette.Alert[0])
        self.BtnClear.Clicked = self.ClearCanvas
        self.BtnClear.setFixedHeight(40)
        PropLayout.addWidget(self.BtnClear)
        
        Workspace.addWidget(PropFrame)
        self.MainLayout.addLayout(Workspace, 1)
    
    def AddComponent(self, TypeStr: str):
        self.Log(f"ADDING: {TypeStr}")
        
        Node = None
        if TypeStr == "Button":
            Node = LCARSButton(f"BUTTON {len(self.ComponentStack)+1}", Type="rect", Color=TitanPalette.Buttons[1])
            Node.setFixedSize(140, 50)
        elif TypeStr == "Label":
            Node = LCARSLabel(f"◤ LABEL {len(self.ComponentStack)+1}", FontSize=14)
            Node.setFixedSize(200, 35)
        elif TypeStr == "Elbow":
            Node = LCARSElbow(Color=TitanPalette.Alert[0], Corner="top_left")
            Node.setFixedSize(140, 140)
        elif TypeStr == "Pill":
            Node = LCARSPill(Color=TitanPalette.Panels[0])
            Node.setFixedSize(120, 40)
        if Node:
            # Place on canvas
            Node.setParent(self.Canvas)
            x_pos = 60 + (len(self.ComponentStack) % 4) * 160
            y_pos = 60 + (len(self.ComponentStack) // 4) * 90
            Node.move(x_pos, y_pos)
            Node.show()
            
            # Enable drag
            Node.mousePressEvent = lambda e, n=Node: self.OnNodePress(e, n)
            Node.mouseMoveEvent = lambda e, n=Node: self.OnNodeMove(e, n)
            Node.mouseReleaseEvent = lambda e, n=Node: self.OnNodeRelease(e, n)
            
            self.ComponentStack.append(Node)
            self.SelectNode(Node)
            self.Log(f"PLACED: {TypeStr} at ({x_pos},{y_pos})")
    
    def SelectNode(self, Node):
        self.SelectedNode = Node
        if Node:
            # Get text
            Text = ""
            if hasattr(Node, 'text'):
                Text = Node.text()
            elif hasattr(Node, 'Text'):
                Text = Node.Text
            self.TextEdit.setPlainText(Text)
            
            # Update position spinners
            self.SpinX.setValue(Node.x())
            self.SpinY.setValue(Node.y())
            self.SpinW.setValue(Node.width())
            self.SpinH.setValue(Node.height())
    
    def OnNodePress(self, Event, Node):
        if Event.button() == Qt.MouseButton.LeftButton:
            self.DraggingNode = Node
            self.DragStartPos = Event.pos()
            self.NodeStartPos = Node.pos()
            self.SelectNode(Node)
    
    def OnNodeMove(self, Event, Node):
        if self.DraggingNode == Node:
            Delta = Event.pos() - self.DragStartPos
            NewX = self.NodeStartPos.x() + Delta.x()
            NewY = self.NodeStartPos.y() + Delta.y()
            Node.move(NewX, NewY)
            self.SpinX.setValue(NewX)
            self.SpinY.setValue(NewY)
    
    def OnNodeRelease(self, Event, Node):
        if Event.button() == Qt.MouseButton.LeftButton:
            self.DraggingNode = None
    
    def OnTextChanged(self):
        if self.SelectedNode:
            Text = self.TextEdit.toPlainText()
            if hasattr(self.SelectedNode, 'setText'):
                self.SelectedNode.setText(Text)
            elif hasattr(self.SelectedNode, 'SetText'):
                self.SelectedNode.SetText(Text)
    
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
                self.SelectedNode.SetColor(Color.name())
                self.Log(f"COLOR: {Color.name()}")
    
    def ApplyFactionColor(self, Color: str):
        if self.SelectedNode and hasattr(self.SelectedNode, 'SetColor'):
            self.SelectedNode.SetColor(Color)
            self.Log(f"FACTION COLOR: {Color}")
    
    def DeleteSelected(self):
        if self.SelectedNode:
            self.Log(f"DELETING: {self.SelectedNode.__class__.__name__}")
            self.ComponentStack.remove(self.SelectedNode)
            self.SelectedNode.setParent(None)
            self.SelectedNode.deleteLater()
            self.SelectedNode = None
    
    def ClearCanvas(self):
        self.Log("CLEARING ALL")
        for Node in self.ComponentStack:
            Node.setParent(None)
            Node.deleteLater()
        self.ComponentStack = []
        self.SelectedNode = None
    
    def SaveLayout(self):
        Path, _ = QFileDialog.getSaveFileName(self, "Save", "", "JSON (*.json)")
        if Path:
            Data = {
                'version': '2.0',
                'nodes': [
                    {
                        'type': N.__class__.__name__,
                        'x': N.x(),
                        'y': N.y(),
                        'w': N.width(),
                        'h': N.height(),
                        'text': getattr(N, 'text', lambda: '')() if hasattr(N, 'text') else ''
                    }
                    for N in self.ComponentStack
                ]
            }
            with open(Path, 'w') as F:
                json.dump(Data, F, indent=2)
            self.Log(f"SAVED: {Path}")
    
    def LoadLayout(self):
        Path, _ = QFileDialog.getOpenFileName(self, "Load", "", "JSON (*.json)")
        if Path:
            self.ClearCanvas()
            with open(Path, 'r') as F:
                Data = json.load(F)
            
            for NodeData in Data.get('nodes', []):
                TypeMap = {
                    'LCARSButton': 'Button',
                    'LCARSLabel': 'Label',
                    'LCARSElbow': 'Elbow',
                    'LCARSPill': 'Pill'
                }
                TypeStr = TypeMap.get(NodeData['type'], '')
                if TypeStr:
                    self.AddComponent(TypeStr)
                    if self.ComponentStack:
                        Node = self.ComponentStack[-1]
                        Node.move(NodeData.get('x', 50), NodeData.get('y', 50))
                        Node.setFixedSize(NodeData.get('w', 100), NodeData.get('h', 50))
            
            self.Log(f"LOADED: {Path}")
    
    def ExportCode(self):
        Lines = [
            "# Generated by LCARS Designer v2.0",
            "from lcars.base.components import LCARSButton, LCARSLabel, LCARSElbow, LCARSPill, LCARSScanningBar",
            "from lcars.base.types import Matrix, ODN",
            "from lcars.base.defaults import TitanPalette",
            "",
            "class GeneratedUI(Matrix):",
            "    def __init__(self, parent=None):",
            "        super().__init__(parent)",
            "        self.setStyleSheet('background: #0A0A14;')",
            "",
        ]
        
        for Node in self.ComponentStack:
            T = Node.__class__.__name__
            X, Y = Node.x(), Node.y()
            W, H = Node.width(), Node.height()
            Text = getattr(Node, 'text', lambda: '')() if hasattr(Node, 'text') else ''
            
            Lines.append(f"        # {T}")
            if T == 'LCARSButton':
                Lines.append(f"        self.btn = LCARSButton('{Text}', ColorHexStr=TitanPalette.Buttons[1])")
            elif T == 'LCARSLabel':
                Lines.append(f"        self.lbl = LCARSLabel('{Text}', FontSizeVal=14)")
            elif T == 'LCARSElbow':
                Lines.append(f"        self.elbow = LCARSElbow('top-left', ColorHexStr=TitanPalette.Alert[0])")
            elif T == 'LCARSPill':
                Lines.append(f"        self.pill = LCARSPill(ColorHexStr=TitanPalette.Panels[0])")
            
            Lines.append(f"        self.elem.setGeometry({X}, {Y}, {W}, {H})")
            Lines.append("")
        
        Code = '\n'.join(Lines)
        print('\n' + '═'*60 + '\n' + Code + '\n' + '═'*60)
        self.Log("CODE EXPORTED (see terminal)")
    
    def Log(self, Msg: str):
        self.StatusLog.append(f"◤ {Msg}")


def main():
    import argparse
    from PyQt6.QtWidgets import QApplication
    
    parser = argparse.ArgumentParser(description='LCARS UI Designer v2.0')
    parser.add_argument('--windowed', action='store_true')
    parser.add_argument('--width', type=int, default=1600)
    parser.add_argument('--height', type=int, default=1000)
    args = parser.parse_args()
    
    # Try registry first, fallback to QApplication
    AppCls = registry.Node("Technical.Application")
    if AppCls:
        AppInst = AppCls.instance() or AppCls(sys.argv)
    else:
        AppInst = QApplication(sys.argv)
    
    Designer = LCARSDesigner()
    
    if args.windowed:
        Designer.resize(args.width, args.height)
        Designer.show()
    else:
        Designer.showFullScreen()
    
    sys.exit(AppInst.exec())


if __name__ == "__main__":
    main()
