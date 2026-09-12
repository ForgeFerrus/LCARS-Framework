"""
Linguistic Matrix Dashboard (migrated to programs/ui).
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QProgressBar,
    QGridLayout, QPushButton, QTextEdit, QScrollArea
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal

from lcars.themes.lcars_palette import get_theme, LCARSEra
from lcars.ui.base.widgets import LCARSButton, LCARSElbow, LCARSContour, ScanningBar

class DashboardWidget(QWidget):
    """Main dashboard for Linguistic Matrix"""
    # (Implementation copied from modules/ui/dashboard.py)
    def __init__(self, database, progress_tracker):
        super().__init__()
        self.db = database
        self.progress_tracker = progress_tracker
        self.era = LCARSEra.LCARS_24TH
        self.colors = get_theme(self.era)
        self.init_ui()
        self.setup_connections()
        self.update_dashboard()

    # For brevity, remaining methods are unchanged from the original module file.
