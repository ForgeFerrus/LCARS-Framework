"""Application entry for Linguistic Matrix (program) — moved from modules."""
from __future__ import annotations
from lcars.themes.lcars_palette import get_theme, LCARSEra
from lcars.modules.linguistic_matrix import LinguisticDatabase, LearningEngine, ProgressTracker
from .main_window import LinguisticPanel
from lcars.modules.sound_manager import get_sound_manager

class LinguisticMatrixApp:
    def __init__(self, era=LCARSEra.LCARS_24TH, faction: str | None = None):
        self.era = era
        self.faction = faction
        self.colors = get_theme(era, faction)
        self.sound_manager = get_sound_manager()
        self.main_window = None

    def initialize(self):
        try:
            self.main_window = LinguisticPanel(self.era, faction=self.faction)
            self.sound_manager.play_sound('startup')
            return True
        except Exception as e:
            return False

    def show(self):
        if self.main_window:
            self.main_window.show()

    def cleanup(self):
        if self.main_window:
            self.main_window.close()
        self.sound_manager.play_sound('shutdown')
