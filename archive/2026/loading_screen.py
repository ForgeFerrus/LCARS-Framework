from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QFrame,
    QHBoxLayout,
    QApplication,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from lcars.themes.palette import (
    LCARSColorGenerator,
    LCARSEra,
    get_era_palette,
    get_lcars_font_style,
    setup_lcars_font,
)


class LCARSLoadingScreen(QWidget):
    """
    LCARS System Boot Sequence - Centered Splash Style
    """

    loading_finished = pyqtSignal()

    def __init__(self, era: LCARSEra = LCARSEra.LCARS_25TH):
        super().__init__()
        setup_lcars_font()
        self.era = era
        self.lcars_palette = get_era_palette(self.era)
        self.color_gen = LCARSColorGenerator(self.era)

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setStyleSheet(f"background-color: black; border: none;")

        screen = QApplication.primaryScreen()
        if screen:
            self.setGeometry(screen.geometry())

        self.steps = [
            "SCANNING CORE BUFFER",
            "INITIALIZING NEURAL NETS",
            "CALIBRATING OPTICAL DATA",
            "ESTABLISHING SECURE PROTOCOLS",
            "SYNCHRONIZING TEMPORAL DATA",
            "RECOGNIZING SYSTEM AUTHORITY",
            "READY FOR INTERFACE.",
        ]
        self.progress = 0
        self._dot_index = 0

        self.init_ui()
        self.showFullScreen()

        # Ultra-fast boot sequence for Mission Ready status
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(50)

        # Slow atmosphere cycle for the frame
        self.color_timer = QTimer(self)
        self.color_timer.timeout.connect(self.cycle_atmospheric_colors)
        self.color_timer.start(6000)

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Decorative Framing (Optional but keeps LCARS feel)
        # --- Top Elbows ---
        top_frame = QHBoxLayout()
        top_frame.setSpacing(10)
        self.elbow_l = QFrame()
        self.elbow_l.setFixedSize(180, 50)
        self.elbow_l.setStyleSheet(
            f"background-color: {self.color_gen.get_color_at_index(0)}; border-top-left-radius: 40px;"
        )
        top_frame.addWidget(self.elbow_l)

        self.title_bar = QFrame()
        self.title_bar.setFixedHeight(50)
        self.title_bar.setStyleSheet(
            f"background-color: {self.color_gen.get_color_at_index(1)}; border-radius: 4px;"
        )
        top_frame.addWidget(self.title_bar, 1)

        self.elbow_r = QFrame()
        self.elbow_r.setFixedSize(40, 50)
        self.elbow_r.setStyleSheet(
            f"background-color: {self.color_gen.get_color_at_index(2)}; border-top-right-radius: 25px;"
        )
        top_frame.addWidget(self.elbow_r)
        main_layout.addLayout(top_frame)

        # --- Center Splash ---
        main_layout.addStretch(1)

        center_container = QWidget()
        center_layout = QVBoxLayout(center_container)
        center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_layout.setSpacing(25)

        # 1. Centered Blue Circle (The "Blue Dot")
        self.logo = QFrame()
        self.logo.setFixedSize(140, 140)
        self.logo.setStyleSheet("background-color: #0077EE; border-radius: 70px;")
        center_layout.addWidget(self.logo, 0, Qt.AlignmentFlag.AlignCenter)

        # 2. Main Title - Non Bold, Large
        title = QLabel("LCARS OPERATING SYSTEM")
        title.setStyleSheet(f"color: #9EA5BA; {get_lcars_font_style(56, 'normal')}")
        center_layout.addWidget(title, 0, Qt.AlignmentFlag.AlignCenter)

        # 3. Version Info
        version = QLabel("SYSTEM BOOT SEQUENCE - MULTI-CORE ANALYSIS")
        version.setStyleSheet(f"color: #3399CC; {get_lcars_font_style(32, 'normal')}")
        center_layout.addWidget(version, 0, Qt.AlignmentFlag.AlignCenter)

        center_layout.addSpacing(10)

        # 4. Progress Dots
        self.dots_lbl = QLabel("● ● ● ● ● ● ●")
        self.dots_lbl.setStyleSheet(
            f"color: #52596E; {get_lcars_font_style(22, 'normal')}"
        )
        center_layout.addWidget(self.dots_lbl, 0, Qt.AlignmentFlag.AlignCenter)

        # 5. Detail Text
        self.step_lbl = QLabel("INITIALIZING...")
        self.step_lbl.setStyleSheet(
            f"color: #556677; {get_lcars_font_style(28, 'normal')}"
        )
        center_layout.addWidget(self.step_lbl, 0, Qt.AlignmentFlag.AlignCenter)

        main_layout.addWidget(center_container)
        main_layout.addStretch(1)

        # --- Footer ---
        footer_layout = QHBoxLayout()
        self.footer_l = QFrame()
        self.footer_l.setFixedSize(180, 30)
        self.footer_l.setStyleSheet(
            f"background-color: {self.color_gen.get_color_at_index(3)}; border-bottom-left-radius: 40px;"
        )
        footer_layout.addWidget(self.footer_l)

        self.footer_main = QFrame()
        self.footer_main.setFixedHeight(30)
        self.footer_main.setStyleSheet(
            f"background-color: {self.color_gen.get_color_at_index(4)}; border-radius: 4px;"
        )
        footer_layout.addWidget(self.footer_main, 1)

        main_layout.addLayout(footer_layout)

    def update_progress(self):
        self.progress += 1

        # Dot animation (sliding red dot)
        dots = ["●"] * 7
        dots[self.progress % 7] = "<font color='#4BBEBF'>●</font>"
        self.dots_lbl.setText(" ".join(dots))

        # Text Step update
        step_idx = (self.progress // 4) % len(self.steps)
        self.step_lbl.setText(self.steps[step_idx])

        if self.progress >= len(self.steps) * 6:  # Total time ~7.5s
            self.timer.stop()
            self.step_lbl.setText("SYSTEM ONLINE")
            QTimer.singleShot(800, self.finish)

    def cycle_atmospheric_colors(self):
        # Update frame colors very slowly
        self.elbow_l.setStyleSheet(
            f"background-color: {self.color_gen.get_color_at_index(0)}; border-top-left-radius: 40px;"
        )
        self.title_bar.setStyleSheet(
            f"background-color: {self.color_gen.get_color_at_index(1)}; border-radius: 4px;"
        )
        self.elbow_r.setStyleSheet(
            f"background-color: {self.color_gen.get_color_at_index(2)}; border-top-right-radius: 25px;"
        )
        self.footer_l.setStyleSheet(
            f"background-color: {self.color_gen.get_color_at_index(3)}; border-bottom-left-radius: 40px;"
        )
        self.footer_main.setStyleSheet(
            f"background-color: {self.color_gen.get_color_at_index(4)}; border-radius: 4px;"
        )

    def finish(self):
        self.loading_finished.emit()
        self.close()
