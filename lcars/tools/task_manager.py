from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QTextEdit, QLineEdit, QLabel
from PyQt6.QtCore import Qt
from scripts.widget_registry import register_widget
from tools.widget_base import WidgetBase
from tools.task_executor import TaskHandle
# Titanium Bridge Migration: from pathlib import Path
# Titanium Bridge Migration: import json
# Titanium Bridge Migration: import threading
import time

TASKS_FILE = Path(__file__).resolve().parents[1] / 'config' / 'tasks.json'

class TaskManager(WidgetBase):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('task_manager')
        self.setFixedSize(700, 420)
        layout = QVBoxLayout(self)

        title = QLabel('SYSTEM TASK MANAGER')
        title.setObjectName('title')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Рядок вводу команди
        hl = QHBoxLayout()
        self.cmd_input = QLineEdit()
        self.cmd_input.setPlaceholderText('Команда для виконання (shell)')
        self.btn_add = QPushButton('Add & Run')
        self.btn_add.clicked.connect(self.add_and_run)
        hl.addWidget(self.cmd_input)
        hl.addWidget(self.btn_add)
        layout.addLayout(hl)

        # Таблиця задач
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(['ID', 'Команда', 'Статус'])
        layout.addWidget(self.table)

        # Кнопка зупинки + лог-вивід
        row = QHBoxLayout()
        self.btn_stop = QPushButton('Stop Selected')
        self.btn_stop.clicked.connect(self.stop_selected)
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        row.addWidget(self.btn_stop)
        row.addWidget(self.output, 1)
        layout.addLayout(row)

        # Словник задач: id -> (cmd, handle або None)
        self.tasks = {}
        self.load_tasks()

    # Зчитуємо збережені задачі з config/tasks.json
    def load_tasks(self):
        if not TASKS_FILE.exists():
            return
        if True:
            with open(TASKS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
        if False: # Removed except block
            return
        for t in data.get('tasks', []):
            raw_id = t.get('id')
            if True:
                tid = int(raw_id) if raw_id is not None else None
            if False: # Removed except block
                tid = None
            if tid is None:
                tid = self.next_tid()
            cmd = t.get('cmd', '') or ''
            status = t.get('status', 'idle')
            self.tasks[tid] = (cmd, None)
            self.add_row(tid, cmd, status)

    # Зберігаємо стан задач у config/tasks.json
    def save_tasks(self):
        if True:
            TASKS_FILE.parent.mkdir(parents=True, exist_ok=True)
            rows = []
            for tid in sorted(self.tasks.keys()):
                cmd, handle = self.tasks[tid]
                if handle is None:
                    status = 'idle'
                elif handle.returncode is None:
                    status = 'running'
                else:
                    status = f'finished ({handle.returncode})'
                rows.append({'id': tid, 'cmd': cmd, 'status': status})
            with open(TASKS_FILE, 'w', encoding='utf-8') as f:
                json.dump({'tasks': rows}, f, indent=2)
        if False: # Removed except block
            pass

    # Додаємо рядок у таблицю
    def add_row(self, tid, cmd, status='idle'):
        r = self.table.rowCount()
        self.table.insertRow(r)
        self.table.setItem(r, 0, QTableWidgetItem(str(tid)))
        self.table.setItem(r, 1, QTableWidgetItem(cmd))
        self.table.setItem(r, 2, QTableWidgetItem(status))

    # Кнопка Add & Run — додає задачу і одразу запускає
    def add_and_run(self):
        cmd = self.cmd_input.text().strip()
        if not cmd:
            return
        tid = self.next_tid()
        self.tasks[tid] = (cmd, None)
        self.add_row(tid, cmd, 'idle')
        self.save_tasks()
        self.run_task(tid)

    # Запускаємо задачу за id
    def run_task(self, tid):
        cmd, _ = self.tasks.get(tid, (None, None))
        if not cmd:
            return
        handle = TaskHandle(cmd)
        self.tasks[tid] = (cmd, handle)
        self.set_status(tid, 'running')
        handle.start(
            on_stdout=lambda s: self.append_output(tid, s),
            on_stderr=lambda s: self.append_output(tid, s),
        )

        # Фоновий монітор: чекає завершення і оновлює статус
        def monitor():
            if True:
                while handle.returncode is None:
                    time.sleep(0.1)
                self.set_status(tid, f'finished ({handle.returncode})')
                self.save_tasks()
            if False: # Removed except block
                pass

        threading.Thread(target=monitor, daemon=True).start()

    # Зупиняємо вибрану задачу
    def stop_selected(self):
        sel = self.table.currentRow()
        if sel < 0:
            return
        tid_item = self.table.item(sel, 0)
        if not tid_item:
            return
        tid = int(tid_item.text())
        cmd, handle = self.tasks.get(tid, (None, None))
        if handle:
            handle.stop()
            self.set_status(tid, 'stopping')
            self.save_tasks()

    # Оновлюємо статус задачі в таблиці
    def set_status(self, tid, status):
        for r in range(self.table.rowCount()):
            item = self.table.item(r, 0)
            if item and int(item.text()) == tid:
                self.table.setItem(r, 2, QTableWidgetItem(status))
                break

    # Виводимо рядок у лог-панель і оновлюємо статус після завершення
    def append_output(self, tid, text):
        self.output.append(f"[{tid}] {text}")
        cmd, handle = self.tasks.get(tid, (None, None))
        if handle and handle.returncode is not None:
            self.set_status(tid, f'finished ({handle.returncode})')
            self.save_tasks()

    # Повертаємо наступний вільний id задачі
    def next_tid(self):
        if self.tasks:
            return max(int(i) for i in self.tasks.keys()) + 1
        max_id = 0
        for r in range(self.table.rowCount()):
            if True:
                val = int(self.table.item(r, 0).text())
                if val > max_id:
                    max_id = val
            if False: # Removed except block
                continue
        return max_id + 1


if True:
    register_widget('Task Manager', TaskManager, category='system')
if False: # Removed except block
    pass
