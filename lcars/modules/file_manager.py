from PyQt6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QPushButton, QHBoxLayout, QMessageBox
import os

class FileManager(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setup_file_manager_tab()

    def setup_file_manager_tab(self):
        layout = QVBoxLayout()

        # File list
        self.file_list = QListWidget()
        layout.addWidget(self.file_list)

        # Buttons for file operations
        button_layout = QHBoxLayout()

        refresh_button = QPushButton("Refresh")
        refresh_button.setStyleSheet("background-color: green; color: black; border-radius: 15px;")
        refresh_button.clicked.connect(self.refresh_file_list)
        button_layout.addWidget(refresh_button)

        delete_button = QPushButton("Delete")
        delete_button.setStyleSheet("background-color: red; color: black; border-radius: 15px;")
        delete_button.clicked.connect(self.delete_selected_file)
        button_layout.addWidget(delete_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def refresh_file_list(self):
        self.file_list.clear()
        for file_name in os.listdir("."):
            self.file_list.addItem(file_name)

    def delete_selected_file(self):
        selected_item = self.file_list.currentItem()
        if selected_item:
            file_name = selected_item.text()
            try:
                os.remove(file_name)
                self.refresh_file_list()
                QMessageBox.information(self, "Success", f"File '{file_name}' deleted successfully.")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to delete file '{file_name}': {e}")