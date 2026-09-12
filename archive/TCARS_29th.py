#!/usr/bin/env python3
"""
TCARS 32nd Century - Повний інтерфейс з динамічними кольорами
"""

import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, 
                           QPushButton, QLineEdit, QFormLayout, QTabWidget, QHBoxLayout, QComboBox)
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from pathlib import Path

# Ensure project root is on sys.path so `lcars` package is importable
current_file = Path(__file__).resolve()
# Walk up until we find the folder that contains the `lcars` package (robust across locations)
project_root = current_file.parent
found = False
for _ in range(6):
    if (project_root / 'lcars').exists():
        found = True
        break
    if project_root.parent == project_root:
        break
    project_root = project_root.parent
if not found:
    # Fallback to parent (expected layout: <repo>/archive/*)
    project_root = current_file.parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from lcars.themes.lcars_palette import (
    get_era_palette, LCARSEra, get_random_button_color, setup_lcars_font
)
import logging
logger = logging.getLogger(__name__)

class TCARS32ndCentury(QMainWindow):
    """
    32nd Century Advanced Temporal Interface
    Incorporating temporal mechanics and quantum chronodynamics
    """
    
    temporal_alert = pyqtSignal(str)  # Signal for temporal anomalies
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TCARS 32nd Century (Universe Class)")
        
        # Підключаємо палітру 32го століття
        self.palette = get_era_palette(LCARSEra.TCARS_32ND)
        self.era = LCARSEra.TCARS_32ND
        
        # Налаштовуємо алгоритм кольорів
        # Load LCARS fonts if available
        try:
            setup_lcars_font()
        except Exception as e:
            logger.exception("Unhandled exception in %s", __file__)
            raise

            logger.exception("Unhandled exception in %s: %s", __file__, e)
            raise

            pass

        self.setup_color_algorithm()
        # Apply initial TCARS-specific styles
        self.apply_tcars_styles(get_random_button_color(self.era))
        
        # Створюємо інтерфейс
        self.setup_interface()
        
        # Запускаємо моніторинг
        self.start_temporal_monitoring()
        
    def setup_color_algorithm(self):
        """Налаштування алгоритму динамічних кольорів"""
        self.color_index = 0
        
        # Таймер для зміни кольорів
        self.color_timer = QTimer(self)
        self.color_timer.timeout.connect(self.update_colors)
        self.color_timer.start(2000)  # Зміна кожні 2 секунди
        
    def update_colors(self):
        """Оновлює кольори за алгоритмом"""
        # Генеруємо новий випадковий колір
        current_color = get_random_button_color(self.era)
        # Update centralized TCARS styles with new accent color
        self.apply_tcars_styles(current_color)
        
        print(f"🔄 Колір змінено на: {current_color}")
        
    def setup_interface(self):
        """Створення повного LCARS 32nd Century інтерфейсу"""
        # Create central widget
        central = QWidget()
        self.setCentralWidget(central)
        central.setStyleSheet(f"""
            QWidget {{
                background-color: {self.palette['background']};
                color: {get_random_button_color(self.era)};
            }}
        """)
        
        # Main layout: left elbow + main content column
        main_h = QHBoxLayout(central)
        main_h.setSpacing(12)
        main_h.setContentsMargins(20, 20, 20, 20)

        # Left elbow decorative panel
        left_elbow = QWidget()
        left_elbow.setObjectName("tcarsElbow")
        left_elbow.setFixedWidth(120)
        main_h.addWidget(left_elbow)

        # Main vertical content area
        main_area = QWidget()
        layout = QVBoxLayout(main_area)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)
        main_h.addWidget(main_area, 1)
        
        # LCARS стиль заголовок
        header = QLabel("TCARS 32nd CENTURY")
        header.setObjectName("tcarsHeader")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setFixedHeight(72)
        header.setStyleSheet("")
        # Use LCARS font if installed
        try:
            header.setFont(QFont('Roddenberry', 28))
        except Exception as e:
            logger.exception("Unhandled exception in %s", __file__)
            raise

            logger.exception("Unhandled exception in %s: %s", __file__, e)
            raise

            header.setFont(QFont('Arial', 28, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # Temporal status в LCARS стилі
        self.temporal_status = QLabel("TEMPORAL CORE: STABLE")
        self.temporal_status.setObjectName("tcarsStatus")
        self.temporal_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.temporal_status.setFixedHeight(52)
        self.temporal_status.setStyleSheet("")
        self.temporal_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        try:
            self.temporal_status.setFont(QFont('Roddenberry', 12))
        except Exception as e:
            logger.exception("Unhandled exception in %s", __file__)
            raise

            logger.exception("Unhandled exception in %s: %s", __file__, e)
            raise

            self.temporal_status.setFont(QFont('Arial', 12))
        layout.addWidget(self.temporal_status)
        
        # LCARS стилізовані вкладки
        self.timeline_monitor = QTabWidget()
        self.setup_timeline_tabs()
        self.timeline_monitor.setObjectName("tcarsTabs")
        self.timeline_monitor.setStyleSheet("")
        layout.addWidget(self.timeline_monitor)
        
        # Temporal control panel в LCARS стилі
        control_panel = QWidget()
        control_panel.setObjectName("tcarsControl")
        control_panel.setStyleSheet("")
        control_layout = QFormLayout()
        self.add_temporal_controls(control_layout)
        control_panel.setLayout(control_layout)
        layout.addWidget(control_panel)
        
        # LCARS стилізовані кнопки
        button_layout = QHBoxLayout()
        
        shields_btn = QPushButton("ENGAGE TEMPORAL SHIELDS")
        shields_btn.setObjectName("tcarsShields")
        shields_btn.setStyleSheet("")
        shields_btn.clicked.connect(self.toggle_temporal_shields)
        button_layout.addWidget(shields_btn)
        
        alert_btn = QPushButton("TEMPORAL ALERT TEST")
        alert_btn.setObjectName("tcarsAlert")
        alert_btn.setStyleSheet("")
        alert_btn.clicked.connect(lambda: self.temporal_alert.emit("Temporal anomaly detected!"))
        button_layout.addWidget(alert_btn)
        
        return_btn = QPushButton("RETURN TO TIMELINE ZERO")
        return_btn.setObjectName("tcarsReturn")
        return_btn.setStyleSheet("")
        return_btn.clicked.connect(self.return_to_main)
        button_layout.addWidget(return_btn)
        
        layout.addLayout(button_layout)
        # Add a compact era selector for quick theme preview (non-destructive)
        era_selector = QComboBox()
        for era in LCARSEra:
            era_selector.addItem(era.name)
        era_selector.setCurrentText(self.era.name)
        era_selector.currentTextChanged.connect(self._on_era_selected)
        layout.addWidget(era_selector)
        
    def setup_timeline_tabs(self):
        """Налаштування вкладок моніторингу часу"""
        # Prime Timeline
        prime_tab = QWidget()
        prime_layout = QVBoxLayout()
        prime_status = QLabel("Prime Timeline Integrity: 100%")
        prime_status.setStyleSheet("font-size: 16px; padding: 10px;")
        prime_layout.addWidget(prime_status)
        
        prime_info = QLabel("No temporal incursions detected\nAll timelines stable\nQuantum coherence: 99.8%")
        prime_info.setStyleSheet("font-size: 14px; padding: 10px;")
        prime_layout.addWidget(prime_info)
        
        prime_tab.setLayout(prime_layout)
        self.timeline_monitor.addTab(prime_tab, "Prime Timeline")
        
        # Alternate Timelines
        alt_tab = QWidget()
        alt_layout = QVBoxLayout()
        alt_status = QLabel("Alternate Timelines Monitoring")
        alt_status.setStyleSheet("font-size: 16px; padding: 10px;")
        alt_layout.addWidget(alt_status)
        
        alt_info = QLabel("Scanning for temporal anomalies...\n0 alternate timelines detected\nParadox level: 0.0%")
        alt_info.setStyleSheet("font-size: 14px; padding: 10px;")
        alt_layout.addWidget(alt_info)
        
        alt_tab.setLayout(alt_layout)
        self.timeline_monitor.addTab(alt_tab, "Alternate Timelines")
        
        # Temporal Nexus
        nexus_tab = QWidget()
        nexus_layout = QVBoxLayout()
        nexus_status = QLabel("Temporal Nexus Status")
        nexus_status.setStyleSheet("font-size: 16px; padding: 10px;")
        nexus_layout.addWidget(nexus_status)
        
        nexus_info = QLabel("Nexus stability: OPTIMAL\nChroniton flow: NORMAL\nTime displacement: 0.00ms")
        nexus_info.setStyleSheet("font-size: 14px; padding: 10px;")
        nexus_layout.addWidget(nexus_info)
        
        nexus_tab.setLayout(nexus_layout)
        self.timeline_monitor.addTab(nexus_tab, "Temporal Nexus")

    def apply_tcars_styles(self, accent_color: str):
        """Apply centralized TCARS styles using current palette and accent color."""
        bg = self.palette.get('background', '#000000')
        text = self.palette.get('text', '#FFFFFF')
        panel_border = self.palette.get('panel_border', '#444444')

        base = f"QWidget {{ background-color: {bg}; color: {text}; }}"

        header_style = f"#tcarsHeader {{ background-color: {accent_color}; color: {bg}; font-size: 32px; font-weight: bold; border-radius: 18px; padding: 12px 24px; margin: 6px; border: 3px solid {panel_border}; }}"
        status_style = f"#tcarsStatus {{ background-color: rgba(255,255,255,0.02); color: {accent_color}; font-size: 18px; padding: 8px; border-radius: 12px; border: 2px solid {panel_border}; margin: 6px; }}"

        tabs_style = f"#tcarsTabs QTabWidget::pane {{ border: 3px solid {panel_border}; background-color: {bg}; border-radius: 16px; }} #tcarsTabs QTabBar::tab {{ background-color: {accent_color}; color: {bg}; padding: 10px 18px; margin-right: 6px; border-top-left-radius: 12px; border-top-right-radius: 12px; font-weight: bold; }} #tcarsTabs QTabBar::tab:selected {{ background-color: {panel_border}; color: {bg}; }}"

        control_style = f"#tcarsControl {{ background-color: rgba(255,255,255,0.01); border: 2px solid {panel_border}; border-radius: 12px; padding: 12px; }}"

        btn_common = f"QPushButton {{ border-radius: 18px; padding: 12px 20px; font-weight: bold; font-size: 13px; }}"
        shields_style = f"#tcarsShields {{ background-color: {accent_color}; color: {bg}; border: 3px solid {panel_border}; }} #tcarsShields:hover {{ background-color: {panel_border}; }}"
        alert_style = f"#tcarsAlert {{ background-color: {self.palette.get('alert_colors',[ '#FFBB00' ])[0]}; color: {bg}; border: 3px solid {panel_border}; }} #tcarsAlert:hover {{ background-color: {self.palette.get('alert_colors',['#E60000'])[1] if len(self.palette.get('alert_colors',[]))>1 else panel_border}; }}"
        return_style = f"#tcarsReturn {{ background-color: {accent_color}; color: {bg}; border: 3px solid {panel_border}; }} #tcarsReturn:hover {{ background-color: {panel_border}; }}"

        full = "\n".join([base, header_style, status_style, tabs_style, control_style, btn_common, shields_style, alert_style, return_style])
        self.setStyleSheet(full)

    def _on_era_selected(self, text: str):
        try:
            era = LCARSEra[text]
            self.palette = get_era_palette(era)
            self.era = era
            # immediately apply a representative accent from the new era
            self.apply_tcars_styles(get_random_button_color(self.era))
        except Exception as e:
            logger.exception("Unhandled exception in %s", __file__)
            raise

            logger.exception("Unhandled exception in %s: %s", __file__, e)
            raise

            pass
        
    def add_temporal_controls(self, layout):
        """Додавання елементів управління часом"""
        # Quantum Chronometric Sensor
        chronometric = QLineEdit()
        chronometric.setPlaceholderText("Quantum Chronometric Reading")
        layout.addRow("Chronometric Sensor:", chronometric)
        
        # Timeline Stability Monitor
        stability = QLineEdit()
        stability.setPlaceholderText("100%")
        stability.setReadOnly(True)
        layout.addRow("Timeline Stability:", stability)
        
        # Temporal Coefficient
        coefficient = QLineEdit()
        coefficient.setPlaceholderText("1.0000")
        coefficient.setReadOnly(True)
        layout.addRow("Temporal Coefficient:", coefficient)
        
        # Paradox Level
        paradox = QLineEdit()
        paradox.setPlaceholderText("0.00%")
        paradox.setReadOnly(True)
        layout.addRow("Paradox Level:", paradox)
        
    def return_to_main(self):
        """Повернення до основної часової лінії"""
        self.close()
        
    def start_temporal_monitoring(self):
        """Запуск моніторингу часових систем"""
        self.monitor_timer = QTimer(self)
        self.monitor_timer.timeout.connect(self.update_temporal_status)
        self.monitor_timer.start(1000)  # Оновлення кожну секунду
        
        # Підключення обробника сигналів
        self.temporal_alert.connect(self.temporal_alert_handler)
        
    def update_temporal_status(self):
        """Оновлення дисплеїв моніторингу часу"""
        # Тут інтеграція з реальними часовими сенсорами
        pass
        
    def toggle_temporal_shields(self):
        """Перемикання часових щитів"""
        sender = self.sender()
        # Be case-insensitive and robust to text variants
        txt = sender.text().lower() if sender else ""
        if "engage" in txt or "engage" in txt.lower():
            sender.setText("DISENGAGE TEMPORAL SHIELDS")
            self.temporal_status.setText("TEMPORAL CORE: SHIELDS ACTIVE")
        else:
            sender.setText("ENGAGE TEMPORAL SHIELDS")
            self.temporal_status.setText("TEMPORAL CORE: STABLE")
            
    def temporal_alert_handler(self, message):
        """Обробка часових аномалій"""
        self.temporal_status.setText(f"TEMPORAL ALERT: {message}")
        self.temporal_status.setStyleSheet("""
            font-size: 18px;
            padding: 15px;
            border: 2px solid;
            border-radius: 20px;
            background-color: rgba(255, 0, 0, 0.1);
        """)

def main():
    app = QApplication(sys.argv)
    window = TCARS32ndCentury()
    window.showFullScreen()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
