import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from lcars.base.components import (
    LCARSButton, LCARSLabel, LCARSPill, LCARSElbow, LCARSSegment, LCARSPadd, LCARSFrame,
    LCARSStatBar, LCARSDataBlock, LCARSScreen, LCARSScanningBar
)

class LCARSGalleryPure(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LCARS Components Gallery (Primitives Only)")
        layout = QVBoxLayout()
        layout.addWidget(QLabel("LCARSButton:"))
        layout.addWidget(LCARSButton("Button Example"))
        layout.addWidget(QLabel("LCARSLabel:"))
        layout.addWidget(LCARSLabel("Label Example"))
        layout.addWidget(QLabel("LCARSPill:"))
        layout.addWidget(LCARSPill("Pill Example"))
        layout.addWidget(QLabel("LCARSElbow:"))
        layout.addWidget(LCARSElbow())
        layout.addWidget(QLabel("LCARSSegment:"))
        layout.addWidget(LCARSSegment())
        layout.addWidget(QLabel("LCARSPadd:"))
        layout.addWidget(LCARSPadd("PADD Example"))
        layout.addWidget(QLabel("LCARSFrame:"))
        layout.addWidget(LCARSFrame())
        layout.addWidget(QLabel("LCARSStatBar:"))
        layout.addWidget(LCARSStatBar("Stat Example", 75))
        layout.addWidget(QLabel("LCARSDataBlock:"))
        layout.addWidget(LCARSDataBlock("DataBlock", 42))
        layout.addWidget(QLabel("LCARSScreen:"))
        layout.addWidget(LCARSScreen("Screen Example"))
        layout.addWidget(QLabel("LCARSScanningBar:"))
        layout.addWidget(LCARSScanningBar())
        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gallery = LCARSGalleryPure()
    gallery.show()
    sys.exit(app.exec())