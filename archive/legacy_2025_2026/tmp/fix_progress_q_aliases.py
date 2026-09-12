from pathlib import Path

path = Path('programs/learning/ui/progress.py')
text = path.read_text(encoding='utf-8')
replacements = {
    'layout = QVBoxLayout(self)': 'layout = VBoxLayout(self)',
    'content_layout = QHBoxLayout()': 'content_layout = HBoxLayout()',
    'left_column = QVBoxLayout()': 'left_column = VBoxLayout()',
    'right_column = QVBoxLayout()': 'right_column = VBoxLayout()',
    'header_frame = QFrame()': 'header_frame = Frame()',
    'header_layout = QHBoxLayout(header_frame)': 'header_layout = HBoxLayout(header_frame)',
    'title = QLabel(': 'title = Label(',
    'progress_frame = QFrame()': 'progress_frame = Frame()',
    'progress_layout = QVBoxLayout(progress_frame)': 'progress_layout = VBoxLayout(progress_frame)',
    'self.overall_progress_bar = QProgressBar()': 'self.overall_progress_bar = ProgressBar()',
    'stats_grid = QGridLayout()': 'stats_grid = GridLayout()',
    'QLabel("Words Learned:"': 'Label("Words Learned:"',
    'QLabel("Accuracy:"': 'Label("Accuracy:"',
    'QLabel("Study Time:"': 'Label("Study Time:"',
    'level_frame = QFrame()': 'level_frame = Frame()',
    'level_layout = QVBoxLayout(level_frame)': 'level_layout = VBoxLayout(level_frame)',
    'req_label = QLabel(': 'req_label = Label(',
    'progress_bar = QProgressBar()': 'progress_bar = ProgressBar()',
    'stats_frame = QFrame()': 'stats_frame = Frame()',
    'stats_layout = QVBoxLayout(stats_frame)': 'stats_layout = VBoxLayout(stats_frame)',
    'title = QLabel("◤ STATISTICS"': 'title = Label("◤ STATISTICS"',
    'period_layout = QHBoxLayout()': 'period_layout = HBoxLayout()',
    'achievements_frame = QFrame()': 'achievements_frame = Frame()',
    'achievements_layout = QVBoxLayout(achievements_frame)': 'achievements_layout = VBoxLayout(achievements_frame)',
    'self.achievements_list = QListWidget()': 'self.achievements_list = ListWidget()',
    'item = QListWidgetItem(display_text)': 'item = ListWidgetItem(display_text)',
    'item.setForeground(QColor(': 'item.setForeground(Color(',
}

for old, new in replacements.items():
    if old not in text:
        print('missing', old)
    text = text.replace(old, new)

path.write_text(text, encoding='utf-8')
print('done')
