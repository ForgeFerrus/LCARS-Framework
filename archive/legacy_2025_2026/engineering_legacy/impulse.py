# Цей файл більше не використовується. Весь функціонал рушія (Impulse та Warp режими) переміщено в engine.py
from lcars.engineering.telemetry import emit_telemetry

class ImpulseDrive:
    # Імпульсний двигун (Impulse Drive) - відповідає за "повільні" локальні зв'язки.
    # Відправляє TCP/JSON команди іншим програмам на цьому ПК (наприклад, Blender).
    # Використовує socket.connect_ex замість try/except для безпечного керування помилками.
    
    def __init__(self, host: str = "localhost", port: int = 12345):
        self.host = host
        self.port = port
        self.socket: Optional[socket.socket] = None
        self.status = "OFFLINE"

    def engage(self) -> bool:
        emit_telemetry("Impulse", f"Engaging impulse thrusters to {self.host}:{self.port}...")
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(2.0)
        
        # connect_ex повертає 0 при успіху (ніяких except)
        result = self.socket.connect_ex((self.host, self.port))
        
        if result == 0:
            self.status = "ONLINE"
            emit_telemetry("Impulse", "Impulse link successfully established.", "success")
            return True
        else:
            self.status = "FAILED"
            emit_telemetry("Impulse", f"Failed to engage impulse link. Error code: {result}", "error")
            self.socket.close()
            self.socket = None
            return False

    def transmit(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        if self.status != "ONLINE" or not self.socket:
            emit_telemetry("Impulse", "Transmission failed: Impulse drive is offline.", "warning")
            return {"status": "error", "message": "Offline"}

        cmd_json = json.dumps(payload)
        
        # Передаємо байти напряму 
        bytes_sent = self.socket.send((cmd_json + "\n").encode())
        if bytes_sent == 0:
            emit_telemetry("Impulse", "Transmission line collapsed during send.", "error")
            self.status = "OFFLINE"
            return {"status": "error", "message": "Line collapsed"}

        # Читаємо безпечно
        resp = self.socket.recv(4096)
        if not resp:
            return {"status": "ok", "message": "Delivered, no response"}
            
        decoded = resp.decode().strip()
        
        # Сувора перевірка JSON без try/except
        if decoded.startswith("{") and decoded.endswith("}"):
            return json.loads(decoded)
        
        return {"status": "ok", "raw": decoded}
