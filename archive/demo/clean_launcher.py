"""Простий компактний лаунчер, який підключає готові фракційні компоненти.

Мета: мінімально втручатися у головну панель, надаючи простий інтерфейс
для вибору фракції → епохи → запуску робочого столу, та використовувати
класні компоненти з `lcars.ui.factions` коли вони доступні.

Цей файл не міняє `demo/demo_launcher.py` — це альтернативний, чітко
сфокусований лаунчер для швидкої інтеграції фракційних UI.
"""
import sys
from pathlib import Path

from PyQt6.QtWidgets import (QApplication, QDialog, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QWidget, QFrame)
from PyQt6.QtCore import Qt

# Ensure repo root on sys.path
repo_root = Path(__file__).parent.parent
import sys as _sys
_sys.path.insert(0, str(repo_root))

# Try to import faction visual components (optional)
try:
    from lcars.ui.factions import klingon as klingon_mod
except Exception as e:
    logger.exception("Unhandled exception in %s", __file__)
    raise

    logger.exception("Unhandled exception in %s: %s", __file__, e)
    raise

    klingon_mod = None

try:
    from lcars.ui.factions import romulan as romulan_mod
except Exception as e:
    logger.exception("Unhandled exception in %s", __file__)
    raise

    logger.exception("Unhandled exception in %s: %s", __file__, e)
    raise

    romulan_mod = None

class CleanLauncher(QDialog):
    """Компактний діалог лаунчера.

    Порядок: вибрати фракцію → вибрати епоху → натиснути LAUNCH.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle('LCARS Clean Launcher')
        self.setStyleSheet('background-color: black; color: white;')
        self.resize(1100, 600)

        self.selected_faction = None
        self.selected_era = None

        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(18)

        # Header
        header = QHBoxLayout()
        head_frame = QFrame()
        head_frame.setFixedHeight(64)
        head_frame.setStyleSheet('background-color: #2f3642; border-radius:8px;')
        hlay = QHBoxLayout(head_frame)
        self.title_lbl = QLabel('◢ SYSTEM ACCESS // TEMPORAL ALIGNMENT')
        self.title_lbl.setStyleSheet('color: black;')
        hlay.addWidget(self.title_lbl)
        header.addWidget(head_frame)
        root.addLayout(header)

        # Main area
        main = QHBoxLayout()
        main.setSpacing(30)

        # Left decorative sidebar
        side = QFrame()
        side.setFixedWidth(180)
        side.setStyleSheet('background-color: #4b5160; border-radius:8px;')
        main.addWidget(side)

        # Center controls
        center = QVBoxLayout()
        center.setSpacing(18)

        # Info line (stardate)
        self.info_lbl = QLabel('STARDATE: -- // UNASSIGNED SECTOR')
        self.info_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center.addWidget(self.info_lbl)

        # Faction buttons
        factions_row = QHBoxLayout()
        factions_row.setSpacing(24)
        self.faction_buttons = {}
        for label, color in (('FEDERATION', '#F2C037'), ('KLINGON', '#F25C4A'), ('ROMULAN', '#2FB1A3'), ('CARDASSIAN', '#2A6F8F')):
            b = QPushButton(label)
            b.setFixedSize(180, 72)
            b.setStyleSheet(f'background-color: {color}; border-radius:6px;')
            b.clicked.connect(lambda _, l=label: self.select_faction(l))
            factions_row.addWidget(b)
            self.faction_buttons[label] = b
        center.addLayout(factions_row)

        # Era row (hidden until faction chosen)
        self.era_row = QHBoxLayout()
        self.era_row.setSpacing(16)
        self.era_buttons = {}
        for era in ('22ND', '23RD', '24TH', '25TH', '29TH'):
            eb = QPushButton(era)
            eb.setFixedSize(100, 44)
            eb.setStyleSheet('background-color: #2f7f9f; border-radius:6px;')
            eb.clicked.connect(lambda _, e=era: self.select_era(e))
            eb.setVisible(False)
            self.era_row.addWidget(eb)
            self.era_buttons[era] = eb
        center.addLayout(self.era_row)

        # Launch button
        self.launch_btn = QPushButton('LAUNCH SYSTEM')
        self.launch_btn.setFixedSize(220, 48)
        self.launch_btn.setEnabled(False)
        self.launch_btn.clicked.connect(self.launch_desktop)
        center.addWidget(self.launch_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        # Stretch
        center.addStretch()

        main.addLayout(center, 1)

        root.addLayout(main)

        # Footer spacer
        root.addStretch()

    def select_faction(self, label):
        self.selected_faction = label
        self.info_lbl.setText(f'STARDATE: {__import__("time").strftime("%Y.%m.%d")} // {label} SECTOR')
        # reveal era buttons
        for eb in self.era_buttons.values():
            eb.setVisible(True)
            eb.setEnabled(True)
        # visually highlight selected faction
        for k, b in self.faction_buttons.items():
            if k == label:
                b.setStyleSheet('background-color: #FFD54F; border-radius:6px;')
            else:
                b.setStyleSheet('background-color: #4b5160; color: white; border-radius:6px;')

    def select_era(self, era):
        self.selected_era = era
        # enable launch
        if self.selected_faction and self.selected_era:
            self.launch_btn.setEnabled(True)
        # preview: change header background to reflect chosen era palette
        era_colors = {
            '22ND': '#FFC107',
            '23RD': '#00E5FF',
            '24TH': '#BCAAA4',
            '25TH': '#39424B',
            '29TH': '#A7FFCC'
        }
        c = era_colors.get(era, '#2f3642')
        try:
            # Apply a subtle background color to the header frame
            self.title_lbl.parent().setStyleSheet(f'background-color: {c}; border-radius:8px;')
        except Exception as e:
            logger.exception("Unhandled exception in %s", __file__)
            raise

            logger.exception("Unhandled exception in %s: %s", __file__, e)
            raise

            pass

    def launch_desktop(self):
        # Build a desktop view using available faction modules/classes
        f = (self.selected_faction or '').upper()
        dlg = QDialog(self)
        dlg.setWindowTitle(f + ' - Desktop')
        dlg_layout = QVBoxLayout(dlg)

        # Try to embed faction-specific widgets; keep launcher intact
        if f == 'KLINGON' and klingon_mod:
            try:
                hdr_cls = getattr(klingon_mod, 'KlingonHeader', None)
                disp_cls = getattr(klingon_mod, 'KlingonDisplay', None)
                if hdr_cls:
                    dlg_layout.addWidget(hdr_cls("K'ara Command"))
                if disp_cls:
                    dlg_layout.addWidget(disp_cls('TACTICAL OVERVIEW'))
            except Exception as e:
                logger.exception("Unhandled exception in %s", __file__)
                raise

                logger.exception("Unhandled exception in %s: %s", __file__, e)
                raise

                dlg_layout.addWidget(QLabel('Klingon desktop failed to build'))
        elif f == 'ROMULAN' and romulan_mod:
            try:
                hdr_cls = getattr(romulan_mod, 'RomulanHeader', None)
                disp_cls = getattr(romulan_mod, 'RomulanDisplay', None)
                if hdr_cls:
                    dlg_layout.addWidget(hdr_cls('IMPERIAL ACCESS'))
                if disp_cls:
                    dlg_layout.addWidget(disp_cls('STATUS'))
            except Exception as e:
                logger.exception("Unhandled exception in %s", __file__)
                raise

                logger.exception("Unhandled exception in %s: %s", __file__, e)
                raise

                dlg_layout.addWidget(QLabel('Romulan desktop failed to build'))
        elif f == 'CARDASSIAN' and cardassian_mod:
            try:
                hdr_cls = getattr(cardassian_mod, 'CardassianHeader', None)
                disp_cls = getattr(cardassian_mod, 'CardassianMonitor', None)
                if hdr_cls:
                    dlg_layout.addWidget(hdr_cls('UNION COMMAND'))
                if disp_cls:
                    dlg_layout.addWidget(disp_cls('SYSTEM ONLINE'))
            except Exception as e:
                logger.exception("Unhandled exception in %s", __file__)
                raise

                logger.exception("Unhandled exception in %s: %s", __file__, e)
                raise

                dlg_layout.addWidget(QLabel('Cardassian desktop failed to build'))
        else:
            dlg_layout.addWidget(QLabel(f'{f} desktop - placeholder'))

        dlg.resize(900, 600)
        dlg.show()


def main():
    app = QApplication(sys.argv)
    dlg = CleanLauncher()
    dlg.show()
    app.processEvents()
    return app.exec()

if __name__ == '__main__':
    sys.exit(main())
