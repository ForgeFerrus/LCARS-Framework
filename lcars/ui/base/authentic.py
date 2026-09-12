from lcars.base.type import Widget, Frame, Primitives
from lcars.base.signal import ODN
from lcars.themes.palette import get_theme, LCARSEra

class LCARSComplexElbow(Widget):
    def __init__(self, color=None, direction="bottom-left", radius=40, thickness=20, armH=100, armV=100, text="", textColor="black", era=LCARSEra.LCARS_24TH, parent=None):
        super().__init__(parent)
        self.era = era
        self.theme = get_theme(era)
        
        self.color = color or self.theme.get("button_colors", ["#FF9900", "#CC99CC"])[1]

        self.direction = direction
        self.radius = radius
        self.thickness = thickness
        self.armH = armH
        self.armV = armV
        self.text = text
        self.textColor = textColor
        self.setMinimumSize(max(radius, armH), max(radius, armV))

    def setColor(self, colorCode):
        self.color = colorCode
        ODN.Emit("Elbow.ColorChanged", {"widget": self, "color": colorCode})

    def render(self, painter):
        path = Primitives.Path()
        
        # Dimensions
        w = self.width()
        h = self.height()
        r = self.radius
        t = self.thickness
        
        # Logic for different orientations
        if self.direction == "bottom-left":
            # Outer corner is at (0, h)
            # Inner corner is at (t, h-t)
            
            # Start at top of vertical arm
            path.moveTo(0, 0) 
            path.lineTo(0, h - r) # Down to start of outer curve
            path.quadTo(0, h, r, h) # Curve to bottom
            path.lineTo(w, h) # Right to end of horizontal arm
            path.lineTo(w, h - t) # Up (thickness)
            path.lineTo(r, h - t) # Left to start of inner curve
            # Inner curve logic: 
            # If radius > thickness, we have a curved inner corner.
            # If radius <= thickness, inner corner is sharp or different.
            # Standard LCARS usually has concentric curves.
            
            inner_r = max(0, r - t)
            if inner_r > 0:
                # curve from (r, h-t) to (t, h-r)
                # Control point would be (t, h-t) roughly?
                # Actually standard SVG arc logic:
                # center is (r, h-r). 
                # Inner arc: center (r, h-r), radius inner_r.
                # From angle 270 (bottom) to 180 (left).
                
                # Simplified quadTo for visual approximation
                # path.quadTo(t, h - t, t, h - r) 
                
                # Better: ArcTo
                # outer arc was centered at (r, h-r) with radius r
                # inner arc is centered at (r, h-r) with radius r-t
                path.arcTo(QRectF(t, h - r - inner_r, inner_r * 2, inner_r * 2), 270, 90)
                
            else:
                path.lineTo(t, h - t)

            path.lineTo(t, 0) # Up to top of inner vertical
            path.closeSubpath()
            
            # Text drawing (usually in the horizontal bar part)
            if self.text:
                painter.setPen(self.text_color)
                painter.setFont("Impact", int(t * 0.6))
                # Draw text at the end of the horizontal bar, right aligned
                painter.drawText(r + 10, h - t, w - r - 20, t, self.text.upper(), align="right")

        elif self.direction == "top-left":
            path.moveTo(0, h)
            path.lineTo(0, r)
            path.quadTo(0, 0, r, 0)
            path.lineTo(w, 0)
            path.lineTo(w, t)
            path.lineTo(r, t)
            
            inner_r = max(0, r - t)
            if inner_r > 0:
                path.arcTo(QRectF(t, t - inner_r, inner_r * 2, inner_r * 2), 90, 90)
            else:
                path.lineTo(t, t)
                
            path.lineTo(t, h)
            path.closeSubpath()

            if self.text:
                painter.setPen(self.text_color)
                font = QFont("Impact", int(t * 0.6)) 
                painter.setFont(font)
                rect_text = QRectF(r, 0, w - r - 10, t)
                painter.drawText(rect_text, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, self.text.upper())

        elif self.direction == "top-right":
            # Outer corner: (w, 0)
            # Inner corner: (w-t, t)
            
            path.moveTo(w, h) # Start at bottom of vertical arm
            path.lineTo(w, r) # Up to start of outer curve
            path.quadTo(w, 0, w - r, 0) # Curve to top-left
            path.lineTo(0, 0) # Left to end of horizontal arm
            path.lineTo(0, t) # Down (thickness)
            path.lineTo(w - r, t) # Right to start of inner curve
            
            inner_r = max(0, r - t)
            if inner_r > 0:
                # Arc from (w-r, t) to (w-t, r)
                # Center is (w-r, r)
                # Angle 90 (top) to 0 (right)
                path.arcTo(QRectF(w - r - inner_r, t - inner_r, inner_r * 2, inner_r * 2), 90, -90)
            else:
                path.lineTo(w - t, t)
                
            path.lineTo(w - t, h) # Down to bottom of inner vertical
            path.closeSubpath()

            if self.text:
                painter.setPen(self.text_color)
                font = QFont("Impact", int(t * 0.6))
                painter.setFont(font)
                rect_text = QRectF(10, 0, w - r - 20, t)
                painter.drawText(rect_text, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, self.text.upper())

        elif self.direction == "bottom-right":
            # Outer corner: (w, h)
            # Inner corner: (w-t, h-t)
            
            path.moveTo(w, 0) # Start at top of vertical arm
            path.lineTo(w, h - r) # Down to start of outer curve
            path.quadTo(w, h, w - r, h) # Curve to bottom-left
            path.lineTo(0, h) # Left to end of horizontal arm
            path.lineTo(0, h - t) # Up (thickness)
            path.lineTo(w - r, h - t) # Right to start of inner curve
            
            inner_r = max(0, r - t)
            if inner_r > 0:
                # Arc from (w-r, h-t) to (w-t, h-r)
                # Center is (w-r, h-r)
                # Angle 270 (bottom) to 360/0 (right)
                path.arcTo(QRectF(w - r - inner_r, h - r - inner_r, inner_r * 2, inner_r * 2), 270, -90)
            else:
                path.lineTo(w - t, h - t)
                
            path.lineTo(w - t, 0) # Up to top of inner vertical
            path.closeSubpath()

            if self.text:
                painter.setPen(self.textColor)
                painter.setFont("Impact", int(t * 0.6))
                painter.drawText(10, h - t, w - r - 20, t, self.text.upper(), align="right")

        painter.setPen(None)
        painter.setBrush(self.color)
        painter.drawPath(path)

class WarpCoreStatus(Widget):
    """
    A complex widget simulating the Warp Core display shown in user images.
    """
    def __init__(self, era=LCARSEra.LCARS_24TH, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 600)
        self.timerVal = 0
        self.era = era
        self.theme = get_theme(era)
        
    def render(self, painter):
        w = self.width()
        h = self.height()
        painter.fillRect(0, 0, w, h, "#000000")
        
        # Draw central core (blue pulsing segments)
        cx = w / 2
        core_width = 80
        seg_h = 25
        gap = 6
        
        startY = 120
        endY = h - 120
        colors = self.theme.get("button_colors", ["#FF9900"])
        archColor = colors[1] if len(colors) > 1 else "#FF9900"
        painter.setBrush(archColor)
        painter.setPen(None)
        
        pathL = Primitives.Path()
        pathL.moveTo(cx - 70, startY - 40)
        pathL.lineTo(cx - 70, endY + 40)
        pathL.lineTo(cx - 180, endY + 40)
        pathL.lineTo(cx - 180, endY + 15)
        pathL.lineTo(cx - 100, endY + 15)
        pathL.lineTo(cx - 100, startY - 15)
        pathL.lineTo(cx - 180, startY - 15)
        pathL.lineTo(cx - 180, startY - 40)
        pathL.closeSubpath()
        painter.drawPath(pathL)
        
        pathR = Primitives.Path()
        pathR.moveTo(cx + 70, startY - 40)
        pathR.lineTo(cx + 70, endY + 40)
        pathR.lineTo(cx + 180, endY + 40)
        pathR.lineTo(cx + 180, endY + 15)
        pathR.lineTo(cx + 100, endY + 15)
        pathR.lineTo(cx + 100, startY - 15)
        pathR.lineTo(cx + 180, startY - 15)
        pathR.lineTo(cx + 180, startY - 40)
        pathR.closeSubpath()
        painter.drawPath(pathR)
        
        numSegs = int((endY - startY) / (seg_h + gap))
        if numSegs < 1: return
        rectX = cx - core_width/2
        for i in range(numSegs):
            y = startY + i * (seg_h + gap)
            pulsePhase = abs(((i + self.timerVal) % 12) / 12.0 - 0.5) * 2
            intensity = int(120 + 135 * pulsePhase)
            c = f"rgb(100, 180, 255, {intensity})"
            painter.setBrush(c)
            painter.drawRect(int(rectX), int(y), int(core_width), int(seg_h))
            if i % 3 == 0:
                injectorCol = colors[6] if len(colors) > 6 else "#CC0000"
                painter.setBrush(injectorCol)
                painter.drawRect(int(rectX - 40), int(y + 8), 40, 8)
                painter.drawRect(int(rectX + core_width), int(y + 8), 40, 8)


    main_window.setWindowTitle("Authentic LCARS Widgets - 24th Century Okudagram Style")
    main_window.setGeometry(100, 100, 1000, 800)
    main_window.setStyleSheet("background-color: #000;")
    
    # Container
    container = QWidget()
    layout = QVBoxLayout(container)
    layout.setSpacing(20)
    layout.setContentsMargins(30, 30, 30, 30)
    
    # Add header
    from PyQt6.QtWidgets import QLabel
    header = QLabel("AUTHENTIC LCARS WIDGETS - 24TH CENTURY")
    header.setStyleSheet("color: #FF9900; font-size: 24px; font-weight: bold; font-family: Impact;")
    layout.addWidget(header)
    
    # Elbows showcase
    elbows_container = QWidget()
    elbows_layout = QHBoxLayout(elbows_container)
    
    # Create all 4 elbow directions
    elbow_bl = LCARSComplexElbow(direction="bottom-left", color="#FF9900", arm_h=150, arm_v=100)
    elbow_tl = LCARSComplexElbow(direction="top-left", color="#CC66FF", arm_h=150, arm_v=100)
    elbow_tr = LCARSComplexElbow(direction="top-right", color="#99CCFF", arm_h=150, arm_v=100)
    elbow_br = LCARSComplexElbow(direction="bottom-right", color="#66CC99", arm_h=150, arm_v=100)
    
    for elbow in [elbow_bl, elbow_tl, elbow_tr, elbow_br]:
        elbows_layout.addWidget(elbow)
    
    layout.addWidget(elbows_container)
    
    # Warp Core Status
    warp_core = WarpCoreStatus(era=LCARSEra.LCARS_24TH)
    layout.addWidget(warp_core, 1)
    
    main_window.setCentralWidget(container)
    main_window.show()
    
    print("=== Authentic LCARS Widgets Demo ===")
    print("✅ LCARSComplexElbow - 4 directions (bottom-left, top-left, top-right, bottom-right)")
    print("✅ High-fidelity QPainter curves with arcTo/quadTo")
    print("✅ WarpCoreStatus - Golden arch frames with pulsing core")
    print("✅ 24th Century Okudagram style")
    print("====================================")
    
    app.exec()


