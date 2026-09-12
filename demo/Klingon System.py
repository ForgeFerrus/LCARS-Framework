"""
Klingon System Demo — окремий вхід для Klingon UI

Цей файл запускає окрему демонстраційну систему з відмінним "візуальним і звуковим"
стилем, відмінним від Federation. Це забезпечує, щоб вибір фракції в лаунчері
справді запускав іншу систему з власним виглядом.

Коментарі українською для зручності розробки.
"""
import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt

# Ensure repo root is importable
project_root = Path(__file__).parent.absolute()
repo_root = project_root.parent
sys.path.insert(0, str(repo_root))

from lcars.themes.lcars_palette import get_lcars_font_style, setup_lcars_font, get_random_button_color
from PyQt6.QtWidgets import QPushButton
from lcars.modules.sound_manager import get_sound_manager


def build_klingon_window():
    """Побудувати вікно Klingon UI — яскраво відрізняється від Federation."""
    w = QWidget()
    w.setWindowTitle("Klingon Empire - Command Interface")
    w.setStyleSheet("background-color: #070202;")
    layout = QVBoxLayout(w)
    layout.setContentsMargins(24, 24, 24, 24)
    layout.setSpacing(12)

    # Header
    header = QHBoxLayout()
    # Decorative elbow replacement (plain frame styled for Klingon)
    elb = QFrame()
    elb.setFixedSize(200, 70)
    elb.setStyleSheet("background-color: #2B0B0B; border-top-left-radius: 40px; border-bottom-left-radius: 4px;")
    header.addWidget(elb)

    title = QFrame()
    title.setFixedHeight(70)
    accent = get_random_button_color(None) or '#C03030'
    title.setStyleSheet(f"background-color: {accent}; border-radius: 6px;")
    t_layout = QHBoxLayout(title)
    t_label = QLabel("K'ara Command - KLINGON EMPIRE")
    t_label.setStyleSheet(f"color: black; {get_lcars_font_style(20, 'bold')}")
    t_layout.addWidget(t_label)
    header.addWidget(title, 1)

    cap = QFrame()
    cap.setFixedSize(80, 70)
    cap.setStyleSheet("background-color: #2B0B0B; border-top-right-radius: 40px; border-bottom-right-radius: 4px;")
    header.addWidget(cap)
    layout.addLayout(header)

    # Main body: simple tactical panels
    body = QHBoxLayout()
    left = QVBoxLayout()
    left_panel = QFrame()
    left_panel.setFixedWidth(300)
    left_panel.setStyleSheet("background-color: #2E1A1A; border-radius: 6px;")
    lp = QVBoxLayout(left_panel)
    lp.setContentsMargins(12, 12, 12, 12)
    lp.addWidget(QLabel("WAR COUNCIL"))
    for n in ("TACTICAL", "BATTLE MAP", "TARGETING"):
        b = QPushButton(n)
        b.setFixedSize(260, 56)
        b.setStyleSheet("background-color: #8A1F1F; color: black; border-radius: 4px;")
        lp.addWidget(b)
    lp.addStretch()
    left.addWidget(left_panel)
    body.addLayout(left)

    center = QVBoxLayout()
    status = QFrame()
    status.setFixedHeight(120)
    status.setStyleSheet(f"background-color: {accent}; border-radius: 6px;")
    s_l = QVBoxLayout(status)
    s_l.addWidget(QLabel("MAIN WAR STATUS"))
    s_l.addWidget(QLabel("SHIELDS: 78% | ARMOR: 64% | TORPEDOES: 120"))
    center.addWidget(status)
    body.addLayout(center, 1)

    right = QVBoxLayout()
    r_panel = QFrame()
    r_panel.setFixedWidth(220)
    r_panel.setStyleSheet("background-color: #3B1212; border-radius: 6px;")
    rp_l = QVBoxLayout(r_panel)
    rp_l.addWidget(QLabel("SENSORS"))
    rp_l.addWidget(QLabel("LONG RANGE: ACTIVE"))
    rp_l.addStretch()
    right.addWidget(r_panel)
    body.addLayout(right)

    layout.addLayout(body)

    footer = QHBoxLayout()
    footer.addStretch()
    footer_label = QLabel("KHAN'IL SYSTEM - HONOR ABOVE ALL")
    footer_label.setStyleSheet(f"color: #FFCFCF; {get_lcars_font_style(12)}")
    footer.addWidget(footer_label)
    layout.addLayout(footer)

    return w


def main():
    app = QApplication(sys.argv)
    setup_lcars_font()
    sound_mgr = get_sound_manager()
    sound_mgr.play('acknowledge')

    win = build_klingon_window()
    win.resize(1200, 700)
    win.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
