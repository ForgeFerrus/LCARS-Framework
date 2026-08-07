import sys
import os
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QFrame, QApplication, QPlainTextEdit
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QColor, QFont, QFontDatabase
from lcars.core.signal import ODN

# Функція отримання шрифту LCARS з перевіркою наявності модуля
def GetLcarsFont(size, bold=False):
    font = QFont("Arial", size)
    font.setBold(bold)
    font.setCapitalization(QFont.Capitalization.AllUppercase)
    # Якщо проєктний шрифт доступний, завантажуємо його; Arial — запасний варіант
    if hasattr(__builtins__, '__import__') or True:
        import importlib.util
        if importlib.util.find_spec("lcars.themes.theme") is not None:
            from lcars.themes.theme import get_lcars_font_style
    return font

def GetFontStyle(size, bold=False):
    weight = "bold" if bold else "normal"
    # standard LCARS font family fallback
    return f"font-family: 'Antonio', 'Arial', sans-serif; font-size: {size}px; font-weight: {weight}; text-transform: uppercase;"

# --- Colors ---
C_CYAN = "#99CCFF"
C_BLUE = "#66AAFF"
C_DBLUE = "#0066CC"
C_LORANGE = "#FFCC66"
C_DORANGE = "#FF9933"
C_RED = "#CC0000"
C_GRAY = "#555555"
C_YELLOW = "#FFCC00"
C_WHITE = "#FFFFFF"
C_BLACK = "#000000"

class Block(QLabel):
    """A simple LCARS rectangular block with optional text."""
    def __init__(self, text="", color=C_BLUE, text_color=C_BLACK, align=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom):
        super().__init__(text)
        self.setAlignment(align)
        self.setStyleSheet(f"background-color: {color}; color: {text_color}; {GetFontStyle(18, True)}; padding: 2px 6px;")

class PillBlock(QLabel):
    """A block with rounded corners."""
    def __init__(self, text="", color=C_BLUE, text_color=C_BLACK, shape="rect", radius=15):
        super().__init__(text)
        self.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)
        
        rad_css = f"border-radius: {radius}px;"
        if shape == "left":
            rad_css = f"border-top-left-radius: {radius}px; border-bottom-left-radius: {radius}px;"
        elif shape == "right":
            rad_css = f"border-top-right-radius: {radius}px; border-bottom-right-radius: {radius}px;"
            
        self.setStyleSheet(f"background-color: {color}; color: {text_color}; {GetFontStyle(16, True)}; {rad_css}; padding: 2px 6px;")

class AppRow(QWidget):
    def __init__(self, code, name, code_col, name_col=C_GRAY, launch_col=C_DBLUE):
        super().__init__()
        self.setFixedHeight(30)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(4)
        
        b1 = PillBlock(code, color=code_col, shape="left", radius=15)
        b1.setFixedWidth(60)
        b1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        b2 = Block("LAUNCH", color=launch_col)
        b2.setFixedWidth(80)
        b2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        b3 = PillBlock(name, color=name_col, shape="right", radius=15)
        b3.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        b3.setStyleSheet(b3.styleSheet() + " padding-left: 10px;")
        
        lay.addWidget(b1)
        lay.addWidget(b2)
        lay.addWidget(b3, 1)

class LaunchCenterView(QWidget):
    """Exact replica of LaunchCenter 3.6"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #000000;")
        self.SetupUi()
        ODN.Channel("Telemetry.Event").Connect(self.OnTelemetryEvent)
        
    def SetupUi(self):
        main_lay = QHBoxLayout(self)
        main_lay.setContentsMargins(20, 20, 20, 20)
        main_lay.setSpacing(10)
        
        # --- LEFT COLUMN ---
        left_col = QVBoxLayout()
        left_col.setSpacing(6)
        
        # Top Header (LCARS FULLSCREEN)
        t_head = QHBoxLayout()
        t_head.setSpacing(6)
        
        elb_top = QLabel("LCARS")
        elb_top.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)
        elb_top.setStyleSheet(f"background-color: {C_CYAN}; color: {C_BLACK}; {GetFontStyle(20, True)}; border-top-left-radius: 40px; padding: 4px 8px;")
        elb_top.setFixedSize(140, 100)
        
        fs_block = Block("FULLSCREEN", color=C_DBLUE)
        fs_block.setFixedHeight(100)
        fs_block.setFixedWidth(120)
        
        t_head.addWidget(elb_top)
        t_head.addWidget(fs_block)
        
        spacer_block = PillBlock(shape="right", color=C_CYAN, radius=40)
        spacer_block.setFixedHeight(100)
        t_head.addWidget(spacer_block, 1)
        
        left_col.addLayout(t_head)
        
        # Select Application Label
        lbl_sel = QLabel("SELECT APPLICATION")
        lbl_sel.setStyleSheet(f"color: {C_YELLOW}; {GetFontStyle(22, False)}")
        
        sel_row = QHBoxLayout()
        sel_row.setSpacing(6)
        stem1 = Block(color=C_CYAN)
        stem1.setFixedSize(140, 30)
        sel_row.addWidget(stem1)
        sel_row.addWidget(lbl_sel, 1)
        
        left_col.addLayout(sel_row)
        
        # App Rows
        apps = [
            ("VE05", "VEXILLUM", C_LORANGE, C_GRAY, C_DBLUE),
            ("PR06", "PROLIXUS", C_BLUE, C_GRAY, C_DBLUE),
            ("AN.B", "ANTICUUS", C_DORANGE, C_GRAY, C_DBLUE),
            ("HA.B", "HASTA", C_BLUE, C_GRAY, C_DBLUE),
            ("AL.A", "ALVEARIUM", C_CYAN, C_GRAY, C_DBLUE),
            ("GX.A", "GALAXIAE", C_BLUE, C_GRAY, C_DBLUE),
            ("DC.A", "DUPLEX CBSA", C_CYAN, C_GRAY, C_DBLUE),
            ("IM.A", "IMPERIUM", C_DORANGE, C_GRAY, C_DBLUE),
            ("0000", "NO FILE", C_RED, C_RED, C_RED),
            ("0000", "NO FILE", C_RED, C_RED, C_RED),
        ]
        
        for code, name, col1, col2, col3 in apps:
            r = QHBoxLayout()
            r.setSpacing(6)
            stem = Block(color=C_CYAN)
            stem.setFixedSize(140, 30)
            r.addWidget(stem)
            r.addWidget(AppRow(code, name, col1, col2, col3), 1)
            left_col.addLayout(r)
            
        left_col.addStretch(1)
        
        # Bottom Left Label Row
        btm_row = QHBoxLayout()
        btm_row.setSpacing(6)
        
        b_stem = Block(color=C_CYAN)
        b_stem.setFixedSize(140, 40)
        btm_row.addWidget(b_stem)
        
        lbl1 = Block("LCARS 47", color=C_WHITE, align=Qt.AlignmentFlag.AlignCenter)
        lbl2 = Block("Build 6.3", color=C_DBLUE, text_color=C_CYAN, align=Qt.AlignmentFlag.AlignCenter)
        lbl3 = Block("LaunchCenter 3.6", color=C_BLUE, align=Qt.AlignmentFlag.AlignCenter)
        
        btm_row.addWidget(lbl1)
        btm_row.addWidget(lbl2)
        btm_row.addWidget(lbl3, 1)
        
        left_col.addLayout(btm_row)
        
        # --- RIGHT COLUMN ---
        right_col = QVBoxLayout()
        right_col.setSpacing(6)
        
        # Top Grid
        grid = QGridLayout()
        grid.setSpacing(6)
        grid.setContentsMargins(0, 0, 0, 0)
        
        def GBlk(txt, color, shape="rect"):
            b = PillBlock(txt, color=color, shape=shape, radius=15)
            b.setMinimumHeight(40)
            b.setAlignment(Qt.AlignmentFlag.AlignCenter)
            return b
            
        grid.addWidget(GBlk("PROLIXUS / VEXILLUM", C_DBLUE), 0, 0)
        grid.addWidget(GBlk("GALAXIAE", C_RED), 0, 1)
        grid.addWidget(GBlk("", C_CYAN, "right"), 0, 2, 1, 3)
        
        grid.addWidget(GBlk("ANTICUUS", C_DBLUE), 1, 0)
        grid.addWidget(GBlk("DUPLEX CARBASA", C_RED), 1, 1)
        grid.addWidget(GBlk("", C_BLUE, "right"), 1, 2, 1, 3)
        
        grid.addWidget(GBlk("HASTA", C_RED), 2, 0)
        grid.addWidget(GBlk("IMPERIUM", C_RED), 2, 1)
        grid.addWidget(GBlk("", C_DBLUE, "right"), 2, 2, 1, 3)
        
        grid.addWidget(GBlk("ALVEARIUM", C_RED), 3, 0)
        grid.addWidget(GBlk("OFFLINE", C_RED), 3, 1)
        grid.addWidget(GBlk("SYSTEM INFORMATION", C_DBLUE), 3, 2)
        grid.addWidget(GBlk("COMM", C_BLUE), 3, 3)
        grid.addWidget(GBlk("EXIT", C_CYAN, "right"), 3, 4)
        
        right_col.addLayout(grid)
        
        right_col.addSpacing(20)
        
        # Select App To Configure
        cfg_hdr = QHBoxLayout()
        cfg_hdr.setSpacing(6)
        
        cfg_elb = PillBlock(shape="left", color=C_BLUE, radius=20)
        cfg_elb.setFixedSize(50, 40)
        cfg_hdr.addWidget(cfg_elb)
        
        lbl_cfg = QLabel("SELECT APPLICATION TO CONFIGURE")
        lbl_cfg.setStyleSheet(f"color: {C_YELLOW}; {GetFontStyle(24, False)}")
        cfg_hdr.addWidget(lbl_cfg)
        
        cfg_hdr.addWidget(PillBlock(shape="right", color=C_DBLUE, radius=20), 1)
        right_col.addLayout(cfg_hdr)
        
        # Config Body
        cfg_body = QHBoxLayout()
        cfg_body.setSpacing(6)
        
        # Stems
        stem_lay = QVBoxLayout()
        stem_lay.setSpacing(6)
        
        stem2 = Block(color=C_GRAY)
        stem2.setFixedSize(50, 30)
        stem_lay.addWidget(stem2)
        
        stem3 = Block(color=C_GRAY)
        stem3.setFixedSize(50, 30)
        stem_lay.addWidget(stem3)
        
        stem_lay.addStretch()
        cfg_body.addLayout(stem_lay)
        
        # Offline buttons
        off_lay = QVBoxLayout()
        off_lay.setSpacing(6)
        
        off1 = PillBlock("OFFLINE", color=C_GRAY, text_color="#333333", radius=15)
        off1.setFixedSize(120, 30)
        off1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        off_lay.addWidget(off1)
        
        off2 = PillBlock("OFFLINE", color=C_GRAY, text_color="#333333", radius=15)
        off2.setFixedSize(120, 30)
        off2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        off_lay.addWidget(off2)
        
        off_lay.addStretch()
        cfg_body.addLayout(off_lay)
        
        cfg_body.addSpacing(50)
        
        # Launch buttons
        cmd_lay = QVBoxLayout()
        cmd_lay.setSpacing(6)
        
        for text in ["MASTER CTRL PL", "VOICE COMMAND"]:
            r = QHBoxLayout()
            r.setSpacing(6)
            b = PillBlock("LAUNCH", color=C_BLUE, shape="left", radius=15)
            b.setFixedSize(100, 30)
            b.setAlignment(Qt.AlignmentFlag.AlignCenter)
            r.addWidget(b)
            
            sep = Block(color=C_YELLOW)
            sep.setFixedSize(8, 30)
            r.addWidget(sep)
            
            l = QLabel(text)
            l.setStyleSheet(f"color: {C_YELLOW}; {GetFontStyle(20, False)}")
            r.addWidget(l)
            r.addStretch(1)
            cmd_lay.addLayout(r)
            
        cmd_lay.addStretch()
        cfg_body.addLayout(cmd_lay, 1)
        
        right_col.addLayout(cfg_body)

        # Live telemetry console so the launch view shows actual system traffic.
        telemetry_head = QLabel("SYSTEM TELEMETRY")
        telemetry_head.setStyleSheet(f"color: {C_CYAN}; {GetFontStyle(18, False)};")
        right_col.addWidget(telemetry_head)

        self.TelemetryBox = QPlainTextEdit()
        self.TelemetryBox.setReadOnly(True)
        self.TelemetryBox.setMaximumHeight(180)
        self.TelemetryBox.setStyleSheet(
            "background-color: #000000; color: #99CCFF; border: 1px solid #335577; "
            "font-family: 'Antonio', 'Arial', sans-serif; font-size: 14px;"
        )
        right_col.addWidget(self.TelemetryBox)

        # Brackets and Logo placeholder (bottom right)
        right_col.addStretch(1)
        
        # Starfleet logo (simplified representation or just text if logo missing)
        logo_row = QHBoxLayout()
        logo_row.addStretch()
        
        bracket_l = Block(color=C_CYAN)
        bracket_l.setFixedSize(15, 120)
        logo_row.addWidget(bracket_l)
        
        # Логотип LCARS або текстова заглушка
        logo_lbl = QLabel()
        logo_lbl.setFixedSize(150, 150)
        from PyQt6.QtGui import QPixmap
        px = QPixmap("lcars/ui/assets/icons/lcars.png")
        if not px.isNull():
            logo_lbl.setPixmap(px.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            logo_lbl.setText("[ LOGO ]")
            logo_lbl.setStyleSheet(f"color: white; {GetFontStyle(20, True)}")
        logo_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        logo_row.addWidget(logo_lbl)
        
        bracket_r = Block(color=C_CYAN)
        bracket_r.setFixedSize(15, 120)
        logo_row.addWidget(bracket_r)
        
        logo_row.addStretch()
        right_col.addLayout(logo_row)
        right_col.addStretch(1)
        
        # Bottom right lines
        btm_r_row = QHBoxLayout()
        btm_r_row.setSpacing(6)
        
        btm_r_row.addStretch(1)
        btm_r_row.addWidget(Block(color=C_CYAN, align=Qt.AlignmentFlag.AlignCenter), 2)
        btm_r_row.addWidget(Block(color=C_DBLUE, align=Qt.AlignmentFlag.AlignCenter), 1)
        btm_r_row.addWidget(Block(color=C_CYAN, align=Qt.AlignmentFlag.AlignCenter), 1)
        
        right_col.addLayout(btm_r_row)
        
        main_lay.addLayout(left_col, 1)
        main_lay.addLayout(right_col, 2)

    def OnTelemetryEvent(self, payload):
        if isinstance(payload, dict):
            line = payload.get("line")
            if line is None:
                source = str(payload.get("source", "TELEMETRY")).upper()
                level = str(payload.get("level", "INFO")).upper()
                message = str(payload.get("message", ""))
                line = f">> {source} [{level}]: {message}"
        else:
            line = str(payload)
        if hasattr(self, "TelemetryBox"):
            self.TelemetryBox.appendPlainText(line)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    view = LaunchCenterView()
    view.resize(1280, 720)
    view.show()
    sys.exit(app.exec())
