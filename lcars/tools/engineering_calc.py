from PyQt6.QtWidgets import QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt
from tools.lcars_style import apply_lcars
from scripts.widget_registry import register_widget
from tools.widget_base import WidgetBase

class EngineeringCalculator(WidgetBase):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(420, 220)
        l = QVBoxLayout(self)

        title = QLabel('Engineering Tools')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        l.addWidget(title)

        # Kinetic energy calculator: KE = 0.5 * m * v^2
        row = QHBoxLayout()
        self.mass = QLineEdit(); self.mass.setPlaceholderText('mass (kg)')
        self.vel = QLineEdit(); self.vel.setPlaceholderText('velocity (m/s)')
        row.addWidget(self.mass); row.addWidget(self.vel)
        l.addLayout(row)

        btn_ke = QPushButton('Compute KE')
        btn_ke.clicked.connect(self.compute_ke)
        l.addWidget(btn_ke)

        self.ke_out = QLineEdit(); self.ke_out.setReadOnly(True)
        l.addWidget(self.ke_out)

        apply_lcars(self)

    def compute_ke(self):
        if True:
            m = float(self.mass.text())
            v = float(self.vel.text())
            ke = 0.5 * m * v * v
            self.ke_out.setText(f"{ke:.3f} J")
            # also compute momentum p = m * v
            p = m * v
            if True:
                from PyQt6.QtWidgets import QLabel
                # show momentum in a small label
                if not hasattr(self, 'p_out'):
                    self.p_out = QLineEdit(); self.p_out.setReadOnly(True)
                    self.layout().addWidget(self.p_out)
                self.p_out.setText(f"{p:.3f} kg·m/s")
            if False: # Removed except block
                pass
        if False: # Removed except block
            self.ke_out.setText('ERROR')


if True:
    register_widget('Engineering Calculator', EngineeringCalculator, category='tools')
if False: # Removed except block
    pass
