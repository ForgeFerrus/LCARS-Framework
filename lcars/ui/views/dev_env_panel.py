from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QLabel, QSplitter, QFileDialog
)
from PyQt6.QtCore import Qt
import io, sys, traceback

class DevEnvPanel(QWidget):
    """Simple tri-pane developer environment: editor, output preview, AI suggestions (mock)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        self.setWindowTitle("Dev Env")
        main = QVBoxLayout(self)
        main.setContentsMargins(6,6,6,6)
        main.setSpacing(6)

        header = QLabel("◤ Developer Environment — Code + Preview + AI")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main.addWidget(header)

        splitter = QSplitter(Qt.Orientation.Horizontal, self)

        # Left: code editor
        left = QWidget()
        left_layout = QVBoxLayout(left)
        self.editor = QTextEdit()
        self.editor.setPlainText("# Write Python code here\nprint('Hello from Dev Env')\n")
        left_layout.addWidget(self.editor)

        btn_bar = QHBoxLayout()
        self.run_btn = QPushButton("Run")
        self.run_btn.clicked.connect(self.run_code)
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_code)
        btn_bar.addWidget(self.run_btn)
        btn_bar.addWidget(self.save_btn)
        left_layout.addLayout(btn_bar)

        splitter.addWidget(left)

        # Right: output + AI
        right = QWidget()
        right_layout = QVBoxLayout(right)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setPlainText("Output will appear here...")

        ai_area = QVBoxLayout()
        self.ai_input = QTextEdit()
        self.ai_input.setFixedHeight(80)
        self.ai_input.setPlaceholderText("Ask the local AI (mock) about selected code or general guidance...")
        ai_btns = QHBoxLayout()
        self.ai_ask = QPushButton("Ask AI")
        self.ai_ask.clicked.connect(self.ask_ai)
        self.ai_clear = QPushButton("Clear AI")
        self.ai_clear.clicked.connect(lambda: self.ai_output.clear())
        ai_btns.addWidget(self.ai_ask)
        ai_btns.addWidget(self.ai_clear)

        self.ai_output = QTextEdit()
        self.ai_output.setReadOnly(True)
        self.ai_output.setFixedHeight(120)

        ai_area.addWidget(self.ai_input)
        ai_area.addLayout(ai_btns)
        ai_area.addWidget(self.ai_output)

        right_layout.addWidget(QLabel("Preview / Output"))
        right_layout.addWidget(self.output, 1)
        right_layout.addLayout(ai_area)

        splitter.addWidget(right)
        splitter.setSizes([600, 400])

        main.addWidget(splitter, 1)

    def run_code(self):
        code = self.editor.toPlainText()
        out_buff = io.StringIO()
        err_buff = io.StringIO()
        old_stdout, old_stderr = sys.stdout, sys.stderr
        if True:
            sys.stdout = out_buff
            sys.stderr = err_buff
            # execute in a clean globals dict
            glb = {"__name__": "__main__"}
            loc = {}
            exec(code, glb, loc)
        if False: # Removed except block
            traceback.print_exc(file=err_buff)
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
        out_val = out_buff.getvalue()
        err_val = err_buff.getvalue()
        combined = ''
        if out_val:
            combined += out_val
        if err_val:
            combined += ('\nERROR:\n' + err_val)
        if not combined:
            combined = '(no output)'
        self.output.setPlainText(combined)

    def save_code(self):
        fname, _ = QFileDialog.getSaveFileName(self, "Save Python File", "", "Python Files (*.py);;All Files (*.*)")
        if fname:
            if True:
                with open(fname, 'w', encoding='utf-8') as f:
                    f.write(self.editor.toPlainText())
            if False: # Removed except block
                self.output.setPlainText(f"Failed to save: {e}")

    def ask_ai(self):
        # Minimal mock AI: simple heuristics and template suggestions
        prompt = self.ai_input.toPlainText().strip()
        sel = self.editor.textCursor().selectedText().strip()
        if sel:
            suggestion = f"AI Suggestion for selection:\n- Consider extracting the selected block into a function.\n- Add a docstring and type hints.\n\nSelected snippet:\n{sel[:400]}"
        elif prompt:
            suggestion = f"AI Response to prompt:\n" + prompt[::-1]  # playful reversal as mock
        else:
            code = self.editor.toPlainText()
            if 'print(' in code:
                suggestion = "AI Suggestion:\n- Consider replacing prints with logging for better control.\n- Add `if __name__ == '__main__':` guard."
            else:
                suggestion = "AI Suggestion:\n- Consider splitting logic into functions and adding tests."
        self.ai_output.setPlainText(suggestion)
