"""Progress UI (migrated)."""
from PyQt6.QtWidgets import QWidget
from lcars.themes.lcars_palette import get_theme, LCARSEra

class ProgressWidget(QWidget):
    def __init__(self, database, tracker):
        super().__init__()
        self.db = database
        self.tracker = tracker
        self.era = LCARSEra.LCARS_24TH
        self.colors = get_theme(self.era)
        # UI implementation copied from module
