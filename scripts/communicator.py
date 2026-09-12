# ◤ LCARS SUBSPACE VOICE COMMUNICATOR DAEMON
# Автономний фоновий сервер для підключення смартфона (Android Combadge).
# СТАНДАРТ: Titanium (Zero-Except, Zero Underscores, Strict PascalCase, Pure LCARS Classes).

from __future__ import annotations
from lcars.base.type import LCARS
from lcars.service.bridge import Bridge
from lcars.service.communicator import SubspaceVoiceGateway, CommunicatorAccess

class CommunicatorDaemon(LCARS):
    @staticmethod
    def Main() -> None:
        Bridge().DisableBytecode()
        Time = Bridge().Load("System.Time")

        Port = 8047
        LocalIp = SubspaceVoiceGateway.GetLocalIp()
        CommunicatorAccess.StartGateway(Port)

        print("==========================================================")
        print("   LCARS SUBSPACE VOICE COMMUNICATOR ONLINE")
        print("==========================================================")
        print(f"\n[SUBSPACE] Local Wi-Fi Gateway: http://{LocalIp}:{Port}")
        print(f"[SUBSPACE] Localhost URL:      http://127.0.0.1:{Port}")
        print("\n>>> Open this URL in your Android phone browser <<<")
        print(">>> Tap the Combadge button and speak directives! <<<\n")
        print("[SUBSPACE] Listening for incoming voice packets from Android...")

        while True:
            if Time and hasattr(Time, "sleep"):
                Time.sleep(1.0)

if __name__ == "__main__":
    CommunicatorDaemon.Main()

