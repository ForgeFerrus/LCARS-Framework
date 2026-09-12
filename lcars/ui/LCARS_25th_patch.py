# Patch file for LCARS_25th.py - contains fixes to apply
# This file documents what needs to be fixed in LCARS_25th.py

# 1. Add QApplication and QMessageBox to imports (line 11)
# FROM:
# from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
#                             QLabel, QPushButton, QGridLayout, QGroupBox, 
#                             QTextEdit, QProgressBar, QTabWidget, QListWidget,
#                             QFrame, QTableWidget, QTableWidgetItem, QHeaderView)
# TO:
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QGridLayout, QGroupBox, 
                            QTextEdit, QProgressBar, QTabWidget, QListWidget,
                            QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
                            QApplication, QMessageBox)

# 2. Fix self.thread attribute naming - rename to self.worker_thread
# Replace in setup_ui method and exec_build/exec_run methods

# 3. Remove tab hiding that fails:
# FROM: self.display_stack.tabBar().hide()  # line 197
# TO: # Tab bar hiding not supported in PyQt6, remove this line

# 4. For analysis table header, wrap in null check:
# FROM: self.analysis_table.horizontalHeader().setSectionResizeMode(...)
# TO: if self.analysis_table.horizontalHeader():
#         self.analysis_table.horizontalHeader().setSectionResizeMode(...)
