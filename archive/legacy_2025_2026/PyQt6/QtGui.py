class QColor:
    def __init__(self, *args, **kwargs):
        pass


class QFont:
    def __init__(self, *args, **kwargs):
        pass


class QPixmap:
    def __init__(self, *args, **kwargs):
        pass


class QPainter:
    def __init__(self, *args, **kwargs):
        pass

    def setRenderHint(self, *args, **kwargs):
        pass


class QPainterPath:
    def __init__(self):
        pass


class QFontDatabase:
    @staticmethod
    def addApplicationFont(path):
        return -1


class QLinearGradient:
    def __init__(self, *args, **kwargs):
        pass


class QCursor:
    def __init__(self, *args, **kwargs):
        pass



class QIcon:
    def __init__(self, *args, **kwargs):
        pass


class QBrush:
    def __init__(self, *args, **kwargs):
        pass


class QPen:
    def __init__(self, *args, **kwargs):
        pass


class QMouseEvent:
    def __init__(self, *args, **kwargs):
        self._x = 0
        self._y = 0

    def pos(self):
        class P:
            def x(self):
                return 0

            def y(self):
                return 0

        return P()


class QKeySequence:
    def __init__(self, seq=None):
        self.seq = seq


class QShortcut:
    def __init__(self, keyseq=None, parent=None):
        self.keyseq = keyseq
        self.parent = parent
        self.activated = None

# Export
QColor = QColor
QFont = QFont
QPixmap = QPixmap
QPainter = QPainter
QIcon = QIcon
QBrush = QBrush
QPen = QPen
QMouseEvent = QMouseEvent
QKeySequence = QKeySequence
QShortcut = QShortcut
