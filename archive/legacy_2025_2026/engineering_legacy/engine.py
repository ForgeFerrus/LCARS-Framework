# LCARS FRAMEWORK v0.9.0-PRE
# Двигун системи (Warp Drive)

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtNetwork import QTcpSocket, QAbstractSocket


class WarpDrive(QObject):
    # Двигун з двома режимами: impulse (TCP) та warp (Geant4)

    StatusChanged = pyqtSignal(str)
    SubspaceTransmission = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.Mode = "standby"
        self.StructuralNodes = []

        self.Socket = QTcpSocket(self)
        self.Socket.connected.connect(self._on_connected)
        self.Socket.disconnected.connect(self._on_disconnected)
        self.Socket.readyRead.connect(self._on_ready_read)
        self.Socket.errorOccurred.connect(self._on_error)

    def SetMode(self, Mode: str):
        if Mode in ("impulse", "warp", "standby"):
            self.Mode = Mode

    def EngageImpulse(self, Host: str, Port: int):
        if self.Mode != "impulse":
            return
        if self.Socket.state() == QAbstractSocket.SocketState.ConnectedState:
            return
        self.Socket.connectToHost(Host, Port)

    def Transmit(self, Command: dict) -> bool:
        if self.Mode != "impulse":
            return False
        if self.Socket.state() != QAbstractSocket.SocketState.ConnectedState:
            return False
        Payload = str(Command).replace("'", '"') + "\n"
        return self.Socket.write(Payload.encode('utf-8')) != -1

    def _on_connected(self):
        self.StatusChanged.emit("ONLINE")

    def _on_disconnected(self):
        self.StatusChanged.emit("OFFLINE")

    def _on_error(self, SocketError):
        self.StatusChanged.emit("ERROR")

    def _on_ready_read(self):
        Raw = self.Socket.readAll()
        if Raw.isEmpty():
            return
        Data = Raw.data().decode('utf-8', errors='ignore').strip()
        if Data.startswith("{") and Data.endswith("}"):
            self.SubspaceTransmission.emit({"raw_payload": Data})

    def InjectWarpMatrix(self, Nodes: list):
        if self.Mode != "warp":
            return
        if not Nodes:
            return
        self.StructuralNodes = Nodes

    def GenerateWarpField(self) -> str:
        if self.Mode != "warp":
            return ""
        if not self.StructuralNodes:
            return ""
        Instructions = []
        for N in self.StructuralNodes:
            Name = N.get("name", "UnknownZone")
            Shape = N.get("type", "box")
            Instructions.append(f"/lcars/geom/add {Shape} {Name}")
        return "\n".join(Instructions)