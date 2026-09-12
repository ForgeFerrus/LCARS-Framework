"""Wi‑Fi scanner adapter (lightweight, non-privileged stub).

This adapter provides a simple list of nearby networks. It is intentionally
conservative and does not perform privileged wireless scanning; it can be
replaced with a platform-specific implementation later.
"""
import random
from lcars.system.scanner_system import BaseScanner, ScannerRegistry


class WifiScanner(BaseScanner):
    def __init__(self):
        super().__init__(name="wifi_scanner", category="network", description="Lightweight Wi‑Fi scanner stub")

    def scan(self, *args, **kwargs):
        # Return a small deterministic set plus some random RSSI values
        samples = [
            {"ssid": "LCARS_NET", "bssid": "00:11:22:33:44:55", "signal": -40, "channel": 6},
            {"ssid": "STARFLEET_GUEST", "bssid": "66:77:88:99:AA:BB", "signal": -68, "channel": 11},
        ]
        # add a couple of ephemeral sample networks
        for i in range(2):
            samples.append({
                "ssid": f"NEIGHBOR_{i}",
                "bssid": ":".join([f"{random.randint(0,255):02X}" for _ in range(6)]),
                "signal": -50 - random.randint(0,30),
                "channel": random.choice([1,6,11])
            })

        return samples


ScannerRegistry.register("wifi_scanner", WifiScanner())
