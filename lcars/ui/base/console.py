"""Base Console Component - unified logic for all console UIs."""

from PyQt6.QtWidgets import QWidget, QTextEdit, QLabel, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import QEvent, Qt, QTimer

from lcars.themes.palette import LCARSEra
from lcars.themes.theme import get_theme, get_lcars_font_style
from lcars.ui.base.widgets import LCARSButton, LCARSElbow, LCARSInput
from lcars.system.console import LCARSConsole

class ConsoleBase(QWidget):
    """Base class for all console UI variants (full-screen, drawer, widget)."""

    def __init__(self, event_bus=None, era=LCARSEra.LCARS_25TH, faction=None):
        super().__init__()
        self.event_bus = event_bus
        self.era = era
        self.faction = faction
        self.theme = get_theme(era, faction)
        # Console Logic
        if True:
            from plugins import get_system
            system = get_system()
            board = getattr(system, "board_computer", None) if system else None
        if False: # Removed except block
            system = None
            board = None
        self.console = LCARSConsole(board)

        # UI Components
        self.elbow = None
        self.output = None
        self.input_line = None
        self.run_button = None
        self.prompt = None

        # Command history and autocompletion
        self._history = []
        self._history_index = -1
        self._completions = [
            "help", "clear", "cls", "exit", "ls", "cd", "cat", "echo", "run", "status", "agent", "network", "browser"
        ]

    def setup_console_ui(self, parent_layout):
        """
        Setup common console UI elements.
        Subclasses call this to build their specific layout.
        """
        # Output area
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setStyleSheet(f"""
            QTextEdit {{
                background-color: black; color: #AAEEFF;
                border: 2px solid {self.theme['palette'][2]};
                border-radius: 10px;
                padding: 15px;
                {get_lcars_font_style(18, 'normal')}
            }}
        """)
        parent_layout.addWidget(self.output, 1)

        # Input area
        input_container = QHBoxLayout()
        input_container.setSpacing(5)

        self.prompt = QLabel("◤")
        self.prompt.setStyleSheet(
            f"color: {self.theme['accent']}; {get_lcars_font_style(18, 'normal')}"
        )
        input_container.addWidget(self.prompt)

        self.input_line = LCARSInput()
        self.input_line.setStyleSheet(f"""
            QLineEdit, LCARSInput {{
                background-color: #080808; color: white;
                border: none; border-bottom: 2px solid {self.theme['accent']};
                padding: 10px;
                {get_lcars_font_style(16, 'normal')}
            }}
        """)
        self.input_line.returnPressed.connect(self.send_command)
        self.input_line.installEventFilter(self)
        def eventFilter(self, obj, event):
                if obj == self.input_line and event.type() == QEvent.Type.KeyPress:
                    key = event.key()
                    if key == Qt.Key.Key_Up:
                        if self._history:
                            if self._history_index == -1:
                                self._history_index = len(self._history) - 1
                            elif self._history_index > 0:
                                self._history_index -= 1
                            self.input_line.setText(self._history[self._history_index])
                        return True
                    elif key == Qt.Key.Key_Down:
                        if self._history:
                            if self._history_index < len(self._history) - 1:
                                self._history_index += 1
                                self.input_line.setText(self._history[self._history_index])
                            else:
                                self.input_line.clear()
                                self._history_index = -1
                        return True
                    elif key == Qt.Key.Key_Tab:
                        # Simple autocompletion
                        text = self.input_line.text()
                        matches = [c for c in self._completions if c.startswith(text)]
                        if matches:
                            self.input_line.setText(matches[0])
                        return True
                return super().eventFilter(obj, event)
        input_container.addWidget(self.input_line, 1)

        self.run_button = LCARSButton("EXECUTE", self.theme["accent"], era=self.era)
        self.run_button.setMinimumSize(140, 45)
        self.run_button.clicked.connect(self.send_command)
        input_container.addWidget(self.run_button)

        parent_layout.addLayout(input_container)

    def send_command(self):
        """Зчитує текст із поля введення та запускає команду - спільна логіка для всіх варіантів."""
        if self.input_line is None or self.output is None:
            return
        cmd = self.input_line.text().strip()
        if not cmd:
            return

        # Add to history
        if not self._history or (self._history and (not self._history or self._history[-1] != cmd)):
            self._history.append(cmd)
        self._history_index = -1

        # Використовуємо span замість b для дотримання правила "немає жирних шрифтів"
        self.output.append(f"<br><span style='color:#CCC; font-weight:normal;'>[UPLINK]:</span> {cmd}")
        self.input_line.clear()

        if cmd.lower() in ["clear", "cls"]:
            self.output.clear()
            return

        self.console.execute(cmd, output_callback=self.on_output)

    def on_output(self, text):
        """Потокобезпечна обробка виводу - спільна для всіх варіантів."""
        def _update():
            if self.output is None:
                return
            if text.startswith("◤"):
                self.output.append(text.replace("\n", "<br>"))
            else:
                self.output.append(
                    f"<span style='color:{self.theme['secondary']}; font-weight:normal;'>{text}</span>"
                )

        QTimer.singleShot(0, _update)
