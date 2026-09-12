from lcars.base.type import Frame, Widget, BoxLayout
from lcars.base.component import LCARSButton, LCARSLabel, LCARSFrame
from lcars.base.signal import ODN
from lcars.themes.palette import LCARSEra, get_theme, get_lcars_font_style

class PortablePADD(LCARSFrame):
    def __init__(self, title="◤ DATA MODULE", era=LCARSEra.LCARS_25TH, faction=None, parent=None):
        super().__init__(parent)
        self.era = era
        self.faction = faction
        self.theme = get_theme(era, faction)
        self.accent = self.theme.get('accent', '#3366CC')
        self.dragPos = None
        self.resizing = False
        self.resizeEdge = None
        self.margin = 8
        self.setFrameless(True)
        self.setStayOnTop(True)
        self.setTranslucent(True)
        self.setMouseTracking(True)
        self.initPaddUi(title)

    def initPaddUi(self, title):
        self.masterLayout = BoxLayout.Vertical(self)
        self.masterLayout.setContentsMargins(5, 5, 5, 5)
        self.paddFrame = LCARSFrame()
        self.paddFrame.setObjectName("PaddFrame")
        accent = self.accent
        bg = "rgba(5, 5, 8, 245)"
        self.paddFrame.setStyleSheet(f"background: {bg}; border: 2px solid {accent}; border-radius: 12px;")
        
        self.contentLayout = BoxLayout.Vertical(self.paddFrame)
        self.contentLayout.setContentsMargins(15, 15, 15, 15)
        self.contentLayout.setSpacing(10)
        self.headerRow = BoxLayout.Horizontal()
        self.titleLbl = LCARSLabel(title.upper())
        self.titleLbl.setStyleSheet(f"color: {accent}; {get_lcars_font_style(18, 'normal')}; letter-spacing: 1px;")
        self.headerRow.addWidget(self.titleLbl, 1)
        self.btnClose = LCARSButton("DISMISS", "#CE6363", shape="pill")
        self.btnClose.setMinimumSize(90, 24)
        self.btnClose.clicked.connect(self.hide)
        self.headerRow.addWidget(self.btnClose)
        self.contentLayout.addLayout(self.headerRow)
        line = LCARSFrame()
        line.setMinimumHeight(1)
        line.setStyleSheet(f"background-color: {accent}55;")
        self.contentLayout.addWidget(line)
        self.moduleContainer = BoxLayout.Vertical()
        self.contentLayout.addLayout(self.moduleContainer, 1)
        self.sizeGripLbl = LCARSLabel("")
        self.sizeGripLbl.setMinimumSize(14, 14)
        self.sizeGripLbl.setStyleSheet(f"color: {accent}AA; {get_lcars_font_style(8, 'normal')}")
        self.contentLayout.addWidget(self.sizeGripLbl, align="right")
        self.masterLayout.addWidget(self.paddFrame)

    def setContent(self, widget: Widget):
        while self.moduleContainer.count():
            child = self.moduleContainer.takeAt(0)
            if child.widget(): child.widget().deleteLater()
        self.moduleContainer.addWidget(widget)
        ODN.Emit("PADD.ContentChanged", {"widget": widget})

    def _get_edge(self, pos):
        """Визначає, на якому краї знаходиться курсор (для адаптивного ресайзу)."""
        w, h = self.width(), self.height()
        x, y = pos.x(), pos.y()
        m = self.margin
        
        if x < m and y < m: return Qt.Edge.TopEdge | Qt.Edge.LeftEdge
        if x > w - m and y > h - m: return Qt.Edge.BottomEdge | Qt.Edge.RightEdge
        if x < m: return Qt.Edge.LeftEdge
        if x > w - m: return Qt.Edge.RightEdge
        if y < m: return Qt.Edge.TopEdge
        if y > h - m: return Qt.Edge.BottomEdge
        return None

    def mousePressEvent(self, a0):
        """Обробка натискання: перетягування або початок ресайзу.
        Якщо клік на дочірньому віджеті (кнопка, список тощо), дозволяємо йому
        обробити подію замість перехоплення для перетягування.
        """
        if a0 is None: return
        if a0.button() != Qt.MouseButton.LeftButton:
            return super().mousePressEvent(a0)

        # check if a child widget exists under cursor and is an interactive control
        local_pt = a0.position().toPoint()
        child = self.childAt(local_pt)
        # only treat certain widgets as clickable; everything else should count as background
        from PyQt6.QtWidgets import QPushButton, QAbstractButton, QLineEdit, QComboBox, QTextEdit
        interactive = (QPushButton, QAbstractButton, QLineEdit, QComboBox, QTextEdit)
        if child and not isinstance(child, interactive) and child is not self:
            # if it's a non-interactive frame/label, allow dragging
            pass
        elif child and isinstance(child, interactive):
            # let button or text field handle the click normally
            return super().mousePressEvent(a0)

        edge = self._get_edge(local_pt)
        if edge:
            self.resizing = True
            self.resize_edge = edge
            handle = self.windowHandle()
            if handle:
                handle.startSystemResize(edge)
        else:
            self.drag_pos = a0.globalPosition().toPoint() - self.frameGeometry().topLeft()
        a0.accept()

    def mouseReleaseEvent(self, a0):
        if a0 is None: return
        self.drag_pos = None
        self.resizing = False
        a0.accept()

    def mouseMoveEvent(self, a0):
        """Адаптивне керування вікном (Cursors & Dragging)."""
        if a0 is None: return
        # Зміна курсора при наведенні на краї
        if not a0.buttons():
            edge = self._get_edge(a0.position().toPoint())
            if edge == Qt.Edge.LeftEdge or edge == Qt.Edge.RightEdge:
                self.setCursor(Qt.CursorShape.SizeHorCursor)
            elif edge == Qt.Edge.TopEdge or edge == Qt.Edge.BottomEdge:
                self.setCursor(Qt.CursorShape.SizeVerCursor)
            elif edge and (edge & Qt.Edge.BottomEdge and edge & Qt.Edge.RightEdge):
                self.setCursor(Qt.CursorShape.SizeFDiagCursor)
            else:
                self.setCursor(Qt.CursorShape.ArrowCursor)
            return

        # Переміщення
        if a0.buttons() == Qt.MouseButton.LeftButton and self.drag_pos is not None and not self.resizing:
            pos = a0.globalPosition().toPoint()
            self.move(pos - self.drag_pos)
            a0.accept()
