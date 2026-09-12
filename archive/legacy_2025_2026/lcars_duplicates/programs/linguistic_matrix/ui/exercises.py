"""Exercises UI (migrated)."""
from PyQt6.QtWidgets import QWidget
from lcars.themes.lcars_palette import get_theme, LCARSEra

class ExercisesWidget(QWidget):
    def __init__(self, database, engine):
        super().__init__()
        self.db = database
        self.engine = engine
        self.era = LCARSEra.LCARS_24TH
        self.colors = get_theme(self.era)
        # UI implementation copied from module
