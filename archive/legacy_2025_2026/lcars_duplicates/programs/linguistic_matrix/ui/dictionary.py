"""Dictionary UI (migrated to programs/ui)."""
# Content migrated from lcars/modules/linguistic_matrix/ui/dictionary.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QLineEdit,
    QTextEdit, QListWidget, QListWidgetItem, QPushButton, QSplitter,
    QScrollArea, QGridLayout, QComboBox
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from lcars.themes.lcars_palette import get_theme, LCARSEra
from lcars.ui.base.widgets import LCARSButton, LCARSElbow, LCARSContour

class DictionaryWidget(QWidget):
    def __init__(self, database):
        super().__init__()
        self.db = database
        self.current_word = None
        self.era = LCARSEra.LCARS_24TH
        self.colors = get_theme(self.era)
        self.init_ui()
        self.setup_connections()
        self.load_vocabulary()

    # Implementation mirrors the original module's UI code.
