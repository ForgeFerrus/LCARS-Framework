# ◤ LCARS LINGUISTIC TOOL — Standalone Application
# LCARS Framework :: ENGLISH LEARNING APPLICATION
# ОПИС: Незалежний застосунок для вивчення англійської мови
# ВЕРСІЯ: Делегована з lcars.base.version

# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import os

# Додати корінь проєкту в шлях
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Titanium Bridge Migration: from typing import Optional, List, Dict, Any
# Titanium Bridge Migration: from dataclasses import dataclass
# Titanium Bridge Migration: from datetime import datetime

from lcars.base.info import getVersion
from lcars.modules.Linguistic import LinguisticMatrix, LinguisticChip, TitaniumLinguisticMatrix

__version__ = getVersion()


@dataclass
class VocabularyEntry:
    # Запис словника
    English: str
    Ukrainian: str
    Level: str = "A1"
    Faction: str = "federation"

class LinguisticPanel(QMainWindow):
    """Linguistic Panel for LCARS UI - Integrated English Learning System"""

    # Signals
    session_completed = pyqtSignal(dict)
    level_achieved = pyqtSignal(str)

    def __init__(self, era=LCARSEra.LCARS_24TH, faction: str | None = None, parent=None):
        super().__init__(parent)
        self.era = era
        self.faction = faction
        self.colors = get_theme(era, faction)
        self.sound_manager = None

        # Initialize core components
        self.database = LinguisticDatabase()
        self.learning_engine = LearningEngine(self.database)
        self.progress_tracker = ProgressTracker(self.database)

        # Session tracking
        self.session_start_time = None
        self.session_timer = QTimer()
        self.session_timer.timeout.connect(self.update_session_time)

        # UI init
        self.init_ui()
        self.setup_connections()
        self.apply_lcars_styling()
        self.start_learning_session()

    def init_ui(self):
        self.setWindowTitle("◤ LINGUISTIC MATRIX - ENGLISH ACQUISITION SYSTEM")
        self.setGeometry(100, 100, 1600, 1000)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sections
        self.create_command_section(main_layout)
        self.create_main_display(main_layout)
        self.create_status_section(main_layout)

        # Menu & status
        self.create_menu_bar()
        self.create_status_bar()

    def create_command_section(self, main_layout):
        command_frame = QFrame()
        command_frame.setFixedWidth(280)
        command_frame.setStyleSheet(f"""
            QFrame {{
                background-color: #000000;
                border-right: 2px solid {self.colors['accent']};
            }}
        """)

        command_layout = QVBoxLayout(command_frame)
        command_layout.setContentsMargins(15, 15, 15, 15)
        command_layout.setSpacing(12)

        elbow = LCARSElbow("top-left", color=self.colors['palette'][0])
        elbow.setFixedSize(250, 70)
        command_layout.addWidget(elbow)

        title = QLabel("LINGUISTIC MATRIX")
        title.setStyleSheet(f"""
            color: {self.colors['accent']};
            {get_lcars_font_style(18, 'normal')}
            padding: 10px;
            background-color: #111111;
            border: 1px solid {self.colors['accent']};
        """)
        command_layout.addWidget(title)

        self.command_buttons = {}
        commands = [
            ("◤ MAIN DISPLAY", "dashboard", self.colors['palette'][1]),
            ("◤ VOCABULARY BANK", "dictionary", self.colors['palette'][2]),
            ("◤ TRAINING MODULES", "exercises", self.colors['palette'][3]),
            ("◤ GRAMMAR CORE", "grammar", self.colors['palette'][4]),
            ("◤ PROGRESS ANALYSIS", "progress", self.colors['palette'][5]),
        ]

        for cmd_text, cmd_key, color in commands:
            btn = LCARSButton(cmd_text, color, shape="left", era=self.era)
            btn.setMinimumHeight(45)
            btn.clicked.connect(lambda checked, k=cmd_key: self.activate_module(k))
            self.command_buttons[cmd_key] = btn
            command_layout.addWidget(btn)

        command_layout.addStretch()

        control_frame = QFrame()
        control_frame.setStyleSheet(f"""
            QFrame {{
                background-color: #111111;
                border: 1px solid {self.colors['palette'][6]};
                border-radius: 5px;
            }}
        """)
        control_layout = QVBoxLayout(control_frame)

        level_label = QLabel("◤ DIFFICULTY MATRIX")
        level_label.setStyleSheet(f"""
            color: {self.colors['palette'][6]};
            {get_lcars_font_style(14, 'normal')}
            margin-bottom: 5px;
        """)
        control_layout.addWidget(level_label)

        self.level_selector = LCARSButton("A1 - FOUNDATION", self.colors['palette'][6])
        self.level_selector.setMinimumHeight(35)
        self.level_selector.clicked.connect(self.cycle_level)
        control_layout.addWidget(self.level_selector)

        exit_btn = LCARSButton("◤ TERMINATE SESSION", "#FF0000", shape="left")
        exit_btn.setMinimumHeight(45)
        exit_btn.clicked.connect(self.terminate_session)
        control_layout.addWidget(exit_btn)

        command_layout.addWidget(control_frame)
        main_layout.addWidget(command_frame)

    def create_main_display(self, main_layout):
        display_frame = QFrame()
        display_frame.setStyleSheet(f"""
            QFrame {{
                background-color: #000000;
                border-top: 2px solid {self.colors['accent']};
                border-bottom: 2px solid {self.colors['accent']};
            }}
        """)

        display_layout = QVBoxLayout(display_frame)
        display_layout.setContentsMargins(20, 20, 20, 20)

        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)

        contour = LCARSContour(self.colors['palette'][0])
        contour.setFixedHeight(60)
        header_layout.addWidget(contour)

        self.module_title = QLabel("MAIN DISPLAY - READY")
        self.module_title.setStyleSheet(f"""
            color: {self.colors['palette'][0]};
            {get_lcars_font_style(24, 'normal')}
            padding: 15px;
        """)
        self.module_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(self.module_title, 1)

        self.system_status = QLabel("◤ SYSTEM: ONLINE")
        self.system_status.setStyleSheet(f"""
            color: #00FF00;
            font-size: 16px;
            font-weight: normal;
            padding: 15px;
            background-color: #001100;
            border: 1px solid #00FF00;
        """)
        header_layout.addWidget(self.system_status)

        display_layout.addWidget(header_frame)

        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("""
            QStackedWidget {
                background-color: #000000;
                border: none;
            }
        """)

        self.dashboard = DashboardWidget(self.database, self.progress_tracker)
        self.dictionary = DictionaryWidget(self.database)
        self.exercises = ExercisesWidget(self.database, self.learning_engine)
        self.grammar = GrammarWidget(self.database)
        self.progress = ProgressWidget(self.database, self.progress_tracker)

        self.content_stack.addWidget(self.dashboard)
        self.content_stack.addWidget(self.dictionary)
        self.content_stack.addWidget(self.exercises)
        self.content_stack.addWidget(self.grammar)
        self.content_stack.addWidget(self.progress)

        display_layout.addWidget(self.content_stack, 1)

        self.scanning_bar = ScanningBar()
        self.scanning_bar.setFixedHeight(30)
        display_layout.addWidget(self.scanning_bar)

        main_layout.addWidget(display_frame, 1)

    def create_status_section(self, main_layout):
        status_frame = QFrame()
        status_frame.setFixedWidth(320)
        status_frame.setStyleSheet(f"""
            QFrame {{
                background-color: #000000;
                border-left: 2px solid {self.colors['accent']};
            }}
        """)

        status_layout = QVBoxLayout(status_frame)
        status_layout.setContentsMargins(15, 15, 15, 15)
        status_layout.setSpacing(12)

        elbow = LCARSElbow("top-right", color=self.colors['accent'])
        elbow.setFixedSize(250, 70)
        status_layout.addWidget(elbow, 0, Qt.AlignmentFlag.AlignRight)

        self.create_status_indicators(status_layout)
        self.create_progress_display(status_layout)
        self.create_session_info(status_layout)

        status_layout.addStretch()
        main_layout.addWidget(status_frame)

    def create_status_indicators(self, layout):
        indicators_frame = QFrame()
        indicators_frame.setStyleSheet(f"""
            QFrame {{
                background-color: #111111;
                border: 2px solid {self.colors['palette'][1]};
                border-radius: 10px;
            }}
        """)

        indicators_layout = QVBoxLayout(indicators_frame)
        indicators_layout.setContentsMargins(12, 12, 12, 12)

        title = QLabel("◤ SYSTEM STATUS")
        title.setStyleSheet(f"""
            color: {self.colors['palette'][1]};
            font-size: 16px;
            font-weight: normal;
            margin-bottom: 10px;
        """)
        indicators_layout.addWidget(title)

        status_items = [
            ("DATABASE", "#00FF00", "ONLINE"),
            ("LEARNING ENGINE", "#00FF00", "ACTIVE"),
            ("PROGRESS TRACKER", "#00FF00", "MONITORING"),
            ("AUDIO SYSTEM", "#FFFF00", "READY"),
        ]

        for item_name, color, status in status_items:
            item_layout = QHBoxLayout()
            name_label = QLabel(f"◤ {item_name}:")
            name_label.setStyleSheet(f"color: {color}; font-size: 12px; font-weight: normal;")
            item_layout.addWidget(name_label)
            status_label = QLabel(status)
            status_label.setStyleSheet(f"color: {color}; font-size: 12px;")
            item_layout.addWidget(status_label)
            indicators_layout.addLayout(item_layout)

        layout.addWidget(indicators_frame)

    def create_progress_display(self, layout):
        progress_frame = QFrame()
        progress_frame.setStyleSheet(f"""
            QFrame {{
                background-color: #111111;
                border: 2px solid {self.colors['palette'][2]};
                border-radius: 10px;
            }}
        """)

        progress_layout = QVBoxLayout(progress_frame)
        progress_layout.setContentsMargins(12, 12, 12, 12)

        title = QLabel("◤ ACQUISITION PROGRESS")
        title.setStyleSheet(f"""
            color: {self.colors['palette'][2]};
            font-size: 16px;
            font-weight: normal;
            margin-bottom: 10px;
        """)
        progress_layout.addWidget(title)

        self.current_level_label = QLabel("A1 - FOUNDATION")
        self.current_level_label.setStyleSheet(f"""
            color: {self.colors['palette'][3]};
            font-size: 18px;
            font-weight: normal;
            padding: 8px;
            background-color: #000000;
            border: 1px solid {self.colors['palette'][3]};
        """)
        progress_layout.addWidget(self.current_level_label)

        from PyQt6.QtWidgets import QProgressBar
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid {self.colors['palette'][4]};
                border-radius: 5px;
                text-align: center;
                color: white;
                font-weight: normal;
                font-size: 12px;
            }}
            QProgressBar::chunk {{
                background-color: {self.colors['palette'][4]};
                border-radius: 3px;
            }}
        """)
        self.progress_bar.setRange(0, 100)
        progress_layout.addWidget(self.progress_bar)

        self.stats_label = QLabel("Words: 0 | Accuracy: 0%")
        self.stats_label.setStyleSheet(f"""
            color: {self.colors['palette'][5]};
            font-size: 12px;
            padding: 8px;
            background-color: #000000;
            border: 1px solid {self.colors['palette'][5]};
        """)
        progress_layout.addWidget(self.stats_label)

        layout.addWidget(progress_frame)

    def create_session_info(self, layout):
        session_frame = QFrame()
        session_frame.setStyleSheet(f"""
            QFrame {{
                background-color: #111111;
                border: 2px solid {self.colors['palette'][6]};
                border-radius: 10px;
            }}
        """)

        session_layout = QVBoxLayout(session_frame)
        session_layout.setContentsMargins(12, 12, 12, 12)

        title = QLabel("◤ SESSION DATA")
        title.setStyleSheet(f"""
            color: {self.colors['palette'][6]};
            font-size: 16px;
            font-weight: normal;
            margin-bottom: 10px;
        """)
        session_layout.addWidget(title)

        self.session_timer_label = QLabel("00:00:00")
        self.session_timer_label.setStyleSheet(f"""
            color: {self.colors['palette'][7]};
            font-size: 20px;
            font-weight: normal;
            padding: 10px;
            background-color: #000000;
            border: 2px solid {self.colors['palette'][7]};
        """)
        self.session_timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        session_layout.addWidget(self.session_timer_label)

        self.session_stats_label = QLabel("Exercises: 0 | Score: 0%")
        self.session_stats_label.setStyleSheet(f"""
            color: {self.colors['palette'][8]};
            font-size: 12px;
            padding: 8px;
            background-color: #000000;
            border: 1px solid {self.colors['palette'][8]};
        """)
        session_layout.addWidget(self.session_stats_label)

        layout.addWidget(session_frame)

    def apply_lcars_styling(self):
        font_css = self.colors.get('font', get_lcars_font_style(12))
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: #000000;
                color: white;
            }}
            QLabel {{
                color: white;
                {font_css}
            }}
        """)

    def setup_connections(self):
        self.progress_tracker.progress_updated.connect(self.update_progress_display)
        self.progress_tracker.level_achieved.connect(self.on_level_achieved)
        self.dashboard.start_exercise.connect(self.start_exercise_session)
        self.exercises.exercise_completed.connect(self.on_exercise_completed)

    def create_menu_bar(self):
        menubar = self.menuBar()
        menubar.setStyleSheet(f"""
            QMenuBar {{
                background-color: #000000;
                color: white;
                border-bottom: 2px solid {self.colors['accent']};
            }}
            QMenuBar::item {{
                background-color: transparent;
                padding: 8px 15px;
                font-weight: normal;
            }}
            QMenuBar::item:selected {{
                background-color: {self.colors['palette'][0]};
            }}
        """)
        system_menu = menubar.addMenu('◤ SYSTEM')
        system_menu.addAction('◤ Initialize Database')
        system_menu.addAction('◤ Export Progress')
        system_menu.addAction('◤ Reset Progress')
        system_menu.addSeparator()
        system_menu.addAction('◤ System Diagnostics')
        learning_menu = menubar.addMenu('◤ LEARNING')
        learning_menu.addAction('◤ Quick Start Session')
        learning_menu.addAction('◤ Review Mode')
        learning_menu.addAction('◤ Pronunciation Practice')
        learning_menu.addAction('◤ Custom Training')
        help_menu = menubar.addMenu('◤ HELP')
        help_menu.addAction('◤ User Manual')
        help_menu.addAction('◤ System Information')
        help_menu.addAction('◤ About Linguistic Matrix')

    def create_status_bar(self):
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet(f"""
            QStatusBar {{
                background-color: #000000;
                color: white;
                border-top: 2px solid {self.colors['accent']};
                font-weight: normal;
            }}
        """)
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("◤ LINGUISTIC MATRIX SYSTEM READY")

    def activate_module(self, module_key):
        module_map = {
            'dashboard': 0,
            'dictionary': 1,
            'exercises': 2,
            'grammar': 3,
            'progress': 4
        }
        if module_key in module_map:
            self.content_stack.setCurrentIndex(module_map[module_key])
            titles = {
                'dashboard': 'MAIN DISPLAY - DASHBOARD',
                'dictionary': 'MAIN DISPLAY - VOCABULARY BANK',
                'exercises': 'MAIN DISPLAY - TRAINING MODULES',
                'grammar': 'MAIN DISPLAY - GRAMMAR CORE',
                'progress': 'MAIN DISPLAY - PROGRESS ANALYSIS'
            }
            self.module_title.setText(titles.get(module_key, 'MAIN DISPLAY'))
            self.status_bar.showMessage(f"◤ MODULE ACTIVATED: {module_key.upper()}")
            self.sound_manager.play_sound('click')

    def cycle_level(self):
        levels = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
        current_text = self.level_selector.text()
        current_level = None
        for level in levels:
            if level in current_text:
                current_level = level
                break
        if current_level:
            current_index = levels.index(current_level)
            next_index = (current_index + 1) % len(levels)
            next_level = levels[next_index]
        else:
            next_level = 'A1'
        level_names = {
            'A1': 'A1 - FOUNDATION',
            'A2': 'A2 - ELEMENTARY',
            'B1': 'B1 - INTERMEDIATE',
            'B2': 'B2 - UPPER INTERMEDIATE',
            'C1': 'C1 - ADVANCED',
            'C2': 'C2 - MASTERY'
        }
        self.level_selector.setText(level_names[next_level])
        self.status_bar.showMessage(f"◤ DIFFICULTY SET TO: {next_level}")
        self.learning_engine.set_current_level(next_level)

    def start_learning_session(self):
        self.session_start_time = datetime.now()
        self.session_timer.start(1000)
        self.progress_tracker.start_session()
        self.system_status.setText("◤ SYSTEM: ACTIVE")
        self.system_status.setStyleSheet("""
            color: #00FF00;
            font-size: 16px;
            font-weight: normal;
            padding: 15px;
            background-color: #001100;
            border: 1px solid #00FF00;
        """)

    def update_session_time(self):
        if self.session_start_time:
            elapsed = datetime.now() - self.session_start_time
            hours, remainder = divmod(elapsed.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            self.session_timer_label.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")

    def update_progress_display(self):
        progress = self.progress_tracker.get_overall_progress()
        self.progress_bar.setValue(int(progress))
        current_level = self.progress_tracker.get_current_level()
        level_names = {
            'A1': 'A1 - FOUNDATION',
            'A2': 'A2 - ELEMENTARY', 
            'B1': 'B1 - INTERMEDIATE',
            'B2': 'B2 - UPPER INTERMEDIATE',
            'C1': 'C1 - ADVANCED',
            'C2': 'C2 - MASTERY'
        }
        self.current_level_label.setText(level_names.get(current_level, current_level))
        stats = self.progress_tracker.get_learning_statistics()
        if 'words' in stats:
            words_stats = stats['words']
            words_learned = words_stats.get('learned_words', 0)
            accuracy = words_stats.get('accuracy_rate', 0) * 100
            self.stats_label.setText(f"Words: {words_learned} | Accuracy: {accuracy:.1f}%")

    def start_exercise_session(self, exercise_type):
        self.activate_module('exercises')

    def on_exercise_completed(self, result):
        if hasattr(self, 'session_exercises'):
            self.session_exercises += 1
        else:
            self.session_exercises = 1
        self.session_stats_label.setText(f"Exercises: {self.session_exercises} | Score: Active")

    def on_level_achieved(self, new_level):
        self.status_bar.showMessage(f"◤ LEVEL ACHIEVED: {new_level}")

    def terminate_session(self):
        reply = QMessageBox.question(
            self, '◤ TERMINATE SESSION',
            'Are you sure you want to terminate the current learning session?\n\nYour progress will be saved.',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.close()

    def closeEvent(self, event: QCloseEvent):
        if self.session_start_time:
            elapsed = datetime.now() - self.session_start_time
            self.progress_tracker.end_session(elapsed.seconds // 60)
        self.database.close()
        self.sound_manager.play_sound('shutdown')
        event.accept()

class LinguisticTool:
    # Незалежний інструмент для роботи з лінгвістичною матрицею

    def __init__(self):
        self.Matrix = TitaniumLinguisticMatrix
        self.SessionStart = datetime.now()
        self.SessionStats = {"words": 0, "exercises": 0, "correct": 0}

    def Translate(self, Text: str, SourceLang: str = "en", TargetLang: Optional[str] = None) -> str:
        # Переклад тексту
        return self.Matrix.TranslateText(Text, SourceLang, TargetLang)

    def Lookup(self, Term: str, LanguageCode: str = "en", Limit: int = 20) -> List[Dict[str, Any]]:
        # Пошук терміна в словнику
        return self.Matrix.LookupTerm(Term, LanguageCode, Limit)

    def AddWord(self, English: str, Ukrainian: str, Level: str = "A1", Faction: str = "federation") -> bool:
        # Додавання слова в словник
        return self.Matrix.AddVocabularyEntry(English, Ukrainian, level=Level, faction=Faction)

    def GetStats(self) -> Dict[str, Any]:
        # Статистика навчання
        Stats = self.Matrix.GetLinguisticStats()
        Elapsed = datetime.now() - self.SessionStart
        Stats["session_minutes"] = Elapsed.seconds // 60
        Stats["session_stats"] = self.SessionStats
        return Stats

    def GetSupportedLanguages(self) -> Dict[str, str]:
        # Список підтримуваних мов
        return self.Matrix.GetSupportedLanguages()

    def SetFaction(self, Faction: str):
        # Встановлення фракції
        self.Matrix.SetActiveFaction(Faction)
        print(f"◤ LINGUISTIC_TOOL :: FACTION_SET: {Faction}")

    def InteractiveMode(self):
        # Інтерактивний режим CLI
        print(f"◤ LINGUISTIC TOOL v{__version__}")
        print("◤ COMMANDS: translate | lookup | add | stats | languages | faction | exit")

        while True:
            if True:
                Command = input("\n◤ > ").strip().lower()

                if Command == "exit":
                    print("◤ SESSION TERMINATED")
                    break

                elif Command == "translate":
                    Text = input("◤ TEXT: ")
                    Src = input("◤ FROM (en/uk): ") or "en"
                    Tgt = input("◤ TO (en/uk): ") or None
                    Result = self.Translate(Text, Src, Tgt)
                    print(f"◤ RESULT: {Result}")

                elif Command == "lookup":
                    Term = input("◤ TERM: ")
                    Lang = input("◤ LANGUAGE (en/uk): ") or "en"
                    Results = self.Lookup(Term, Lang, 10)
                    for R in Results:
                        print(f"◤ {R.get('english', '-')} = {R.get('ukrainian', '-')}")

                elif Command == "add":
                    Eng = input("◤ ENGLISH: ")
                    Ukr = input("◤ UKRAINIAN: ")
                    Lvl = input("◤ LEVEL (A1-C2): ") or "A1"
                    if self.AddWord(Eng, Ukr, Lvl):
                        print("◤ WORD ADDED")
                    else:
                        print("◤ FAILED")

                elif Command == "stats":
                    Stats = self.GetStats()
                    print(f"◤ VOCABULARY: {Stats.get('vocabulary_count', 0)} words")
                    print(f"◤ SESSION: {Stats.get('session_minutes', 0)} minutes")

                elif Command == "languages":
                    Langs = self.GetSupportedLanguages()
                    for Code, Name in Langs.items():
                        print(f"◤ {Code}: {Name}")

                elif Command == "faction":
                    Faction = input("◤ FACTION (federation/klingon/etc): ")
                    self.SetFaction(Faction)

                else:
                    print("◤ UNKNOWN COMMAND")

            if False: # Removed except block
                print("\n◤ SESSION TERMINATED")
                break
            if False: # Removed except block
                print(f"◤ ERROR: {E}")


def main():
    # Точка входу
    Tool = LinguisticTool()

    # Якщо є аргументи командного рядка — виконати і вийти
    if len(sys.argv) > 1:
        Command = sys.argv[1]

        if Command == "translate" and len(sys.argv) > 2:
            Text = sys.argv[2]
            Result = Tool.Translate(Text)
            print(Result)

        elif Command == "lookup" and len(sys.argv) > 2:
            Term = sys.argv[2]
            Results = Tool.Lookup(Term)
            for R in Results:
                print(f"{R.get('english', '-')} = {R.get('ukrainian', '-')}")

        elif Command == "stats":
            Stats = Tool.GetStats()
            print(f"Vocabulary: {Stats.get('vocabulary_count', 0)}")

        else:
            print("◤ USAGE: linguistic_tool.py [translate|lookup|stats] [arg]")

    else:
        # Інтерактивний режим
        Tool.InteractiveMode()


if __name__ == "__main__":
    main()


__all__ = ["LinguisticTool", "VocabularyEntry", "main"]
