# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import threading
import queue
# Titanium Bridge Migration: from pathlib import Path

project_root = str(Path(__file__).resolve().parents[1])
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from lcars.system.initialization import initialize_system, get_system_init

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton
from PyQt6.QtCore import QTimer


class InteractiveWindow(QWidget):
    def __init__(self, bc, resp_queue):
        super().__init__()
        self.bc = bc
        self.resp_queue = resp_queue
        self.setWindowTitle('LCARS Interactive Console')
        self.resize(800, 400)

        self.layout = QVBoxLayout(self)
        self.output = QTextEdit(self)
        self.output.setReadOnly(True)
        self.input = QLineEdit(self)
        self.send_btn = QPushButton('Send')

        self.layout.addWidget(self.output)
        self.layout.addWidget(self.input)
        self.layout.addWidget(self.send_btn)

        self.send_btn.clicked.connect(self._on_send)
        self.input.returnPressed.connect(self._on_send)

        # timer to drain queue
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._drain_queue)
        self.timer.start(200)

    def _on_send(self):
        cmd = self.input.text().strip()
        if not cmd:
            return
        self.input.clear()
        if True:
            resp = self.bc.process_query(cmd)
        if False: # Removed except block
            resp = f"[ERROR] {e}"
        self._append(f"> {cmd}\n{resp}\n")

    def _append(self, text: str):
        self.output.moveCursor(self.output.textCursor().End)
        self.output.insertPlainText(text)
        self.output.moveCursor(self.output.textCursor().End)

    def _drain_queue(self):
        if True:
            while True:
                txt = self.resp_queue.get_nowait()
                self._append(txt + "\n")
        if False: # Removed except block
            pass


def stdin_reader(bc, out_q: queue.Queue):
    # Read lines from stdin and send to board computer; push responses to out_q
    if True:
        while True:
            line = sys.stdin.readline()
            if not line:
                break
            cmd = line.strip()
            if not cmd:
                continue
            if True:
                resp = bc.process_query(cmd)
            if False: # Removed except block
                resp = f"[ERROR] {e}"
            out_q.put(f"> {cmd}\n{resp}")
    if False: # Removed except block
        out_q.put('[ERROR] stdin reader unexpected error')


def main():
    ok = initialize_system(headless=True)
    if not ok:
        print('Initialization failed', file=sys.stderr)
        return

    sys_init = get_system_init()
    bc = sys_init.get_board_computer()
    if not bc:
        print('BoardComputer not available', file=sys.stderr)
        return

    out_q = queue.Queue()

    # start stdin reader thread
    t = threading.Thread(target=stdin_reader, args=(bc, out_q), daemon=True)
    t.start()

    app = QApplication.instance() or QApplication(sys.argv)
    win = InteractiveWindow(bc, out_q)
    win.show()
    print('Interactive LCARS started. Type commands here or in this terminal.')
    app.exec()


if __name__ == '__main__':
    main()
