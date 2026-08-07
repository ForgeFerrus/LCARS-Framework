import sys
from pathlib import Path
import math

project_root = str(Path(__file__).parent.parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from lcars.base.type import LCARS
from lcars.base.interface import Graphic

class BiometricShieldWidget(Graphic):
    def __init__(self, Parent=None, BaseColor="#FF3333"):
        super().__init__(Parent)
        self.widget.setMinimumSize(300, 300)
        self.BaseColor = BaseColor
        self.rotation_angle = 0
        self.pulse_alpha = 255
        self.pulse_dir = -1
        
        # We need a timer to animate
        QtCore = LCARS.Core
        if QtCore and hasattr(QtCore, "QTimer"):
            self.timer = QtCore.QTimer(self.widget)
            self.timer.timeout.connect(self.UpdateAnimation)
            self.timer.start(30) # ~33 FPS

        # We must override paintEvent on the underlying QWidget
        self.widget.paintEvent = self.paintEvent

    def UpdateAnimation(self):
        self.rotation_angle = (self.rotation_angle + 1) % 360
        self.pulse_alpha += 5 * self.pulse_dir
        if self.pulse_alpha <= 100:
            self.pulse_dir = 1
        elif self.pulse_alpha >= 255:
            self.pulse_dir = -1
            
        if hasattr(self.widget, "update"):
            self.widget.update()

    def paintEvent(self, event):
        QtGui = LCARS.Gui
        QtCore = LCARS.Core
        if not QtGui or not QtCore:
            return

        painter = QtGui.QPainter(self.widget)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)

        rect = self.widget.rect()
        center = rect.center()
        radius = min(rect.width(), rect.height()) / 2 - 20

        # Background grid or glow can be added here
        
        # Outer Ring
        pen = QtGui.QPen(QtGui.QColor(self.BaseColor))
        pen.setWidth(4)
        painter.setPen(pen)
        painter.drawEllipse(center, int(radius), int(radius))

        # Inner rotating arcs
        pen.setWidth(8)
        pen.setColor(QtGui.QColor(255, 100, 0, 180)) # Orange-ish glow
        painter.setPen(pen)
        
        arc_rect = QtCore.QRectF(center.x() - radius + 20, center.y() - radius + 20, (radius - 20) * 2, (radius - 20) * 2)
        
        # Draw 3 arcs rotating clockwise
        for i in range(3):
            start_angle = (self.rotation_angle + i * 120) * 16
            span_angle = 60 * 16
            painter.drawArc(arc_rect, int(start_angle), int(span_angle))
            
        # Innermost rotating arcs (counter-clockwise)
        pen.setWidth(4)
        pen.setColor(QtGui.QColor(255, 200, 0, int(self.pulse_alpha))) # Yellow-ish pulse
        painter.setPen(pen)
        
        inner_radius = radius - 50
        inner_arc_rect = QtCore.QRectF(center.x() - inner_radius, center.y() - inner_radius, inner_radius * 2, inner_radius * 2)
        
        for i in range(4):
            start_angle = (-self.rotation_angle * 1.5 + i * 90) * 16
            span_angle = 45 * 16
            painter.drawArc(inner_arc_rect, int(start_angle), int(span_angle))
            
        # Center Biometric Fingerprint placeholder (just concentric circles for now)
        pen.setWidth(1)
        pen.setColor(QtGui.QColor(self.BaseColor))
        painter.setPen(pen)
        for r in range(10, int(inner_radius - 20), 10):
            painter.drawEllipse(center, r, r)

        painter.end()
