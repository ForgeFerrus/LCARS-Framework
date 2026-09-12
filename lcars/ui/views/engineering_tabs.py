from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QLabel, QPushButton
from PyQt6.QtCore import Qt
from lcars.core import EventBus

class NeuralLinkView(QWidget):
    """Interfaces with the Isolinear Core Directives."""
    def __init__(self, nexus, parent=None):
        super().__init__(parent)
        self.nexus = nexus
        self.init_ui()
        self.refresh_timer = None # Could be added later

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        lbl = QLabel("NEURAL SUBSTRATE DIRECTIVES (ODN FLOW)")
        lbl.setStyleSheet("color: #FFCC00; font-size: 18px; font-weight: normal; margin-bottom: 10px;")
        layout.addWidget(lbl)

        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["DIRECTIVE", "STATUS/VALUE"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #000;
                color: #00FF00;
                gridline-color: #333;
                border: none;
                font-family: 'Courier New';
            }
            QHeaderView::section {
                background-color: #222;
                color: #FFFFFF;
                border: 1px solid #444;
            }
        """)
        layout.addWidget(self.table)
        
        self.refresh_data()

        btn_sync = QPushButton("RESYNC CORE")
        btn_sync.setStyleSheet("background-color: #CC6600; color: white; padding: 10px; border-radius: 5px;")
        btn_sync.clicked.connect(self.refresh_data)
        layout.addWidget(btn_sync)

    def refresh_data(self):
        # Access directives from isolinear core through nexus
        if self.nexus and hasattr(self.nexus, 'isolinear'):
            directives = self.nexus.isolinear.directives
            self.table.setRowCount(len(directives))
            for i, (key, val) in enumerate(directives.items()):
                self.table.setItem(i, 0, QTableWidgetItem(str(key)))
                self.table.setItem(i, 1, QTableWidgetItem(str(val)))
        else:
            self.table.setRowCount(1)
            self.table.setItem(0, 0, QTableWidgetItem("CORE ERROR"))
            self.table.setItem(0, 1, QTableWidgetItem("SUBSTRATE NOT LINKED"))

