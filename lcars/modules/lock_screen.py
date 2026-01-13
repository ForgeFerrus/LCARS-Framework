"""
LCARS Login Screen - Minimal full-screen background environment
"""

from PyQt6.QtWidgets import QWidget, QPushButton, QLabel
from PyQt6.QtCore import Qt, pyqtSignal, QRect, QPoint, QSettings
from PyQt6.QtGui import QPixmap, QPainter, QFont, QColor
from pathlib import Path


class LCARSLoginScreen(QWidget):
    """Minimal login screen - full-screen background with invisible trigger zone"""
    
    login_successful = pyqtSignal()
    
    def __init__(self, parent=None, background_image: str = None):
        super().__init__(parent)
        
        # Full screen, frameless
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setGeometry(0, 0, 1920, 1080)  # Full screen resolution
        
        # Background image
        self.background_pixmap = None
        self.background_image_path = background_image
        
        # Load background if provided
        if background_image:
            self.load_background_image(background_image)
        else:
            # Default black background
            self.setStyleSheet("QWidget { background-color: #000000; }")
        
        # Create AUTHORIZE button - VISIBLE and DRAGGABLE
        self.authorize_button = QPushButton("ACCESS")
        self.authorize_button.setGeometry(1600, 950, 200, 80)  # Bottom center-right default
        self.authorize_button.setParent(self)
        self.authorize_button.setStyleSheet("background-color: rgb(231, 68, 42); color: white; border: none; border-radius: 15px;")
        self.authorize_button.clicked.connect(self.on_authorize_clicked)
        self.authorize_button.setToolTip("Click to authorize — drag to reposition")
        # For dragging button
        self.drag_position = None

        # Persisted position (QSettings must be available for mouseReleaseEvent)
        self.settings = QSettings("LCARS", "Enterprise")
        pos = self.settings.value("login/authorize_pos")
        if pos:
            try:
                if isinstance(pos, QPoint):
                    self.authorize_button.move(pos)
                else:
                    s = str(pos)
                    if "," in s:
                        x, y = map(int, s.strip().split(","))
                        self.authorize_button.move(x, y)
            except Exception:
                pass

        # Connect click and released (for saving position)
        self.authorize_button.clicked.connect(self.on_authorize_clicked)
        self.authorize_button.released.connect(lambda: self.settings.setValue("login/authorize_pos", self.authorize_button.pos()))

        # Show window
        self.showFullScreen()

        # DEBUG: Print button info
        print(f"🎯 AUTHORIZE button: visible and draggable at {self.authorize_button.geometry()}")

        # Update login screen styles for full-screen image
        self.background_image = QLabel(self)
        self.background_image.setPixmap(QPixmap(self.background_image_path))
        self.background_image.setScaledContents(True)
        self.background_image.setGeometry(self.rect())
        self.background_image.setStyleSheet("background-color: black;")

    def load_background_image(self, image_path: str):
        """Load background image"""
        path = Path(image_path)
        if path.exists():
            pixmap = QPixmap(str(path))
            if not pixmap.isNull():
                # Store original pixmap - will scale in paintEvent
                self.background_pixmap = pixmap
                print(f"✓ Background loaded: {image_path}")
                print(f"  Original size: {pixmap.width()}x{pixmap.height()}")
                self.update()
            else:
                print(f"✗ Cannot load image: {image_path}")
                self.setStyleSheet("QWidget { background-color: #000000; }")
        else:
            print(f"✗ Image not found: {image_path}")
            self.setStyleSheet("QWidget { background-color: #000000; }")

    def paintEvent(self, event):
        """Paint full-screen background with centered image"""
        painter = QPainter(self)

        # Fill entire screen with black
        painter.fillRect(self.rect(), Qt.GlobalColor.black)

        # Draw centered image if available
        if self.background_pixmap:
            # Calculate 90% of screen size, maintaining aspect ratio
            screen_width = self.width()
            screen_height = self.height()

            max_width = int(screen_width * 0.9)
            max_height = int(screen_height * 0.9)

            # Scale image maintaining aspect ratio
            scaled = self.background_pixmap.scaledToWidth(
                max_width,
                Qt.TransformationMode.SmoothTransformation
            )

            # If height still too large, scale by height
            if scaled.height() > max_height:
                scaled = self.background_pixmap.scaledToHeight(
                    max_height,
                    Qt.TransformationMode.SmoothTransformation
                )

            # Center the image
            x = (screen_width - scaled.width()) // 2
            y = (screen_height - scaled.height()) // 2

            painter.drawPixmap(x, y, scaled)

        painter.end()

    def on_trigger_clicked(self):
        """Invisible button clicked - login successful"""
        print("⚠ Environment accessed")
        self.login_successful.emit()
        self.close()

    def mousePressEvent(self, event):
        """Handle mouse press - start dragging button or other actions"""
        # Check if clicked on button (button handles its own click)
        if self.authorize_button.geometry().contains(event.pos()):
            # Button will handle the click itself
            return

        # If clicked elsewhere, start dragging the button
        self.drag_position = event.pos() - self.authorize_button.pos()

    def mouseMoveEvent(self, event):
        """Handle mouse move - drag button around"""
        if self.drag_position is not None:
            # Move button with mouse and constrain to window rect
            new_pos = event.pos() - self.drag_position
            w = self.authorize_button.width()
            h = self.authorize_button.height()
            max_x = self.width() - w
            max_y = self.height() - h
            x = max(0, min(new_pos.x(), max_x))
            y = max(0, min(new_pos.y(), max_y))
            self.authorize_button.move(x, y)

    def mouseReleaseEvent(self, event):
        """Handle mouse release - stop dragging"""
        # Save position when release
        if self.authorize_button:
            p = self.authorize_button.pos()
            # QSettings will store as 'QPoint' or as string depending on backend
            self.settings.setValue("login/authorize_pos", p)
        self.drag_position = None

    def on_authorize_clicked(self):
        """AUTHORIZE widget clicked"""
        pos = self.authorize_button.pos() if hasattr(self, 'authorize_button') else None
        print(f"✓ AUTHORIZE clicked at {pos}")
        print("⚠ Environment accessed")
        self.login_successful.emit()
        self.close()

    def keyPressEvent(self, event):
        """Allow triggering authorize with Enter/Return when focused and ESC to close"""
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.on_authorize_clicked()
        elif event.key() == Qt.Key.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)
