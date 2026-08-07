from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QListWidget, QListWidgetItem, QTextEdit, QLineEdit, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, QThread
from pathlib import Path
import sys
import os
import subprocess

from lcars.ui.widgets.common import create_lcars_button, get_lcars_font_style
from lcars.themes.lcars_palette import get_era_palette, LCARSEra
from lcars.modules.project_manager import ProjectManager
from lcars.core.task_executor import TaskExecutor

# Основний віджет операцій симуляції для управління проектами Geant4
class OperationsWidget(QWidget):
    # Ініціалізація віджета та налаштування стану
    def __init__(self, parent=None):
        super().__init__(parent)
        self.era = LCARSEra.LCARS_25TH
        self.colors = get_era_palette(self.era)

        # Ініціалізація основної логіки
        self.geant4_root = Path(__file__).resolve().parents[3] / "Geant4" / "Enterprise"
        self.pm = ProjectManager(self.geant4_root)
        self.executor = TaskExecutor()

        # Поточний стан
        self.current_project = None
        self.current_thread = None

        self.SetupUi()

        # Таймер для опитування виводу виконавця
        self.poll_timer = QTimer(self)
        self.poll_timer.timeout.connect(self.PollOutput)
        self.poll_timer.start(100)

    # Налаштування інтерфейсу користувача
    def SetupUi(self):
        layout = QHBoxLayout(self)  # Горизонтальний макет для двоколонкового вигляду
        layout.setSpacing(20)
        layout.setContentsMargins(10, 10, 10, 10)

        # --- ЛІВА КОЛОНКА: Список проектів ---
        left_col = QVBoxLayout()

        title = QLabel("PROJECTS")
        title.setStyleSheet(f"color: {self.colors['button_colors'][1]}; {get_lcars_font_style(20, 'normal')}")
        left_col.addWidget(title)

        self.project_list = QListWidget()
        self.project_list.setStyleSheet(f"""
            QListWidget {{
                background-color: #050505;
                color: {self.colors['button_colors'][3]};
                border: 2px solid {self.colors['button_colors'][0]};
                border-radius: 2px;
                font-size: 14pt;
            }}
            QListWidget::item {{
                padding: 10px;
            }}
            QListWidget::item:selected {{
                background-color: {self.colors['button_colors'][0]};
                color: black;
            }}
        """)
        self.RefreshProjects()
        self.project_list.currentItemChanged.connect(self.OnProjectSelected)
        left_col.addWidget(self.project_list)

        refresh_btn = create_lcars_button("REFRESH LIST", parent=self, width=150, height=45)
        refresh_btn.clicked.Connect(self.RefreshProjects)
        left_col.addWidget(refresh_btn)

        layout.addLayout(left_col, 1)  # Вага 1

        # --- ПРАВА КОЛОНКА: Деталі та дії ---
        right_col = QVBoxLayout()

        self.lbl_title = QLabel("SELECT A TARGET")
        self.lbl_title.setStyleSheet(f"color: #FFF; {get_lcars_font_style(24, 'normal')}")
        right_col.addWidget(self.lbl_title)

        # Рядок дій
        actions = QHBoxLayout()

        self.btn_build = create_lcars_button("BUILD", parent=self, width=120, height=50)
        self.btn_build.clicked.Connect(self.BuildProject)

        self.btn_run = create_lcars_button("RUN", parent=self, width=120, height=50)
        self.btn_run.clicked.Connect(self.RunProject)

        self.btn_open = create_lcars_button("OPEN FOLDER", parent=self, width=140, height=50)
        self.btn_open.clicked.Connect(self.OpenProjectFolder)

        actions.addWidget(self.btn_build)
        actions.addWidget(self.btn_run)
        actions.addWidget(self.btn_open)
        actions.addStretch()
        right_col.addLayout(actions)

        # Термінал / Журнал
        term_label = QLabel("SYSTEM TERMINAL")
        term_label.setStyleSheet(f"color: {self.colors['button_colors'][2]}; font-size: 12pt;")
        right_col.addWidget(term_label)

        self.terminal = QTextEdit()
        self.terminal.setReadOnly(True)
        self.terminal.setStyleSheet("background-color: #080808; color: #BBB; font-family: Consolas; font-size: 11pt; border: none;")
        right_col.addWidget(self.terminal, 1)

        # Ручний ввід команди
        cmd_row = QHBoxLayout()
        self.cmd_input = QLineEdit()
        self.cmd_input.setPlaceholderText("Enter system command...")
        self.cmd_input.setStyleSheet("background-color: #222; color: #FFF; padding: 5px; font-family: Consolas;")
        self.cmd_input.returnPressed.connect(self.ExecCmd)
        cmd_row.addWidget(self.cmd_input, 1)

        cmd_btn = create_lcars_button("EXECUTE", parent=self, width=100, height=35)
        cmd_btn.clicked.Connect(self.ExecCmd)
        cmd_row.addWidget(cmd_btn)

        right_col.addLayout(cmd_row)

        layout.addLayout(right_col, 2)  # Вага 2

    # Оновлення списку проектів з файлової системи
    def RefreshProjects(self):
        self.pm = ProjectManager(self.geant4_root)
        self.project_list.clear()
        projects = self.pm.get_all_projects()

        # Якщо проекти не знайдені, вивести повідомлення
        if not projects:
            self.terminal.append("[SCAN] No projects found in " + str(self.geant4_root))

        for p in projects:
            item = QListWidgetItem(p.name)
            item.setData(Qt.ItemDataRole.UserRole, p)
            self.project_list.addItem(item)

    # Обробка вибору проекту зі списку
    def OnProjectSelected(self, current, previous=None):
        if not current:
            return
        p = current.data(Qt.ItemDataRole.UserRole)
        self.current_project = p
        self.lbl_title.setText(f"{p.name.upper()}")
        self.terminal.append(f"Target locked: {p.name}")

    # Додавання тексту до терміналу з автопрокруткою
    def AppendTerminal(self, text: str):
        self.terminal.append(text)
        # Автопрокрутка до кінця
        cursor = self.terminal.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.terminal.setTextCursor(cursor)

    # Опитування виводу виконавця задач
    def PollOutput(self):
        item = self.executor.get_output()
        if item:
            kind, data = item
            # Обробка різних типів виводу
            if kind == 'output':
                self.AppendTerminal(data.rstrip('\n'))
            elif kind == 'error':
                self.AppendTerminal(f"[ERR] {data}")
            elif kind == 'complete':
                self.AppendTerminal(f"[DONE] Process finished with code {data}\n")

    # Запуск процесу збірки поточного проекту
    def BuildProject(self):
        if not self.current_project:
            self.AppendTerminal('[ERROR] SELECT A PROJECT FIRST')
            return
        p = self.current_project
        build_dir = p.build_dir or (p.path / 'build')
        build_dir.mkdir(parents=True, exist_ok=True)

        cmd = f'cmake -S "{p.path}" -B "{build_dir}" && cmake --build "{build_dir}" --config Release'
        self.AppendTerminal(f'Init sequence: BUILD {p.name}...')
        thread = self.executor.execute_command(
            cmd,
            cwd=str(build_dir),
            on_output=self.OnOut,
            on_error=self.OnErr,
            on_complete=self.OnComplete
        )
        thread.start()
        self.current_thread = thread

    # Запуск виконання поточного проекту
    def RunProject(self):
        if not self.current_project:
            self.AppendTerminal('[ERROR] SELECT A PROJECT FIRST')
            return
        p = self.current_project
        exe = p.executable
        # Спроба визначити виконуваний файл з каталогу збірки
        if not exe:
            build_dir = p.build_dir or (p.path / 'build')
            exe = None
            # Пошук будь-якого виконуваного файлу в каталозі збірки
            if build_dir.exists():
                candidates = list(build_dir.glob("*.exe")) + list(build_dir.glob("**/*.exe"))
                if candidates:
                    exe = candidates[0]

        if not exe:
            self.AppendTerminal('[ERROR] No executable found. Try building first.')
            return

        cmd = f'"{exe}"'
        self.AppendTerminal(f'Init sequence: RUN {p.name}...')
        thread = self.executor.execute_command(
            cmd,
            cwd=str(p.path),
            on_output=self.OnOut,
            on_error=self.OnErr,
            on_complete=self.OnComplete
        )
        thread.start()
        self.current_thread = thread

    # Відкриття каталогу проекту у файловому менеджері
    def OpenProjectFolder(self):
        if not self.current_project:
            return
        path = str(self.current_project.path)
        self.AppendTerminal(f"Accessing filesystem: {path}")
        # Відкриття залежно від платформи
        if sys.platform == 'win32':
            os.startfile(path)
        else:
            subprocess.Popen(['xdg-open', path])

    # Виконання ручної команди з поля введення
    def ExecCmd(self):
        cmd = self.cmd_input.text().strip()
        if not cmd:
            return
        cwd = str(self.current_project.path) if self.current_project else None

        self.AppendTerminal(f"> {cmd}")
        thread = self.executor.execute_command(
            cmd,
            cwd=cwd,
            on_output=self.OnOut,
            on_error=self.OnErr,
            on_complete=self.OnComplete
        )
        thread.start()
        self.cmd_input.clear()

    # Зворотні виклики для TaskExecutor
    def OnOut(self, line: str):
        # Передача виводу в чергу
        self.executor.output_queue.put(('output', line))

    def OnErr(self, err: str):
        # Передача помилок у чергу
        self.executor.output_queue.put(('error', err))

    def OnComplete(self, code: int):
        # Повідомлення про завершення процесу
        self.executor.output_queue.put(('complete', code))
