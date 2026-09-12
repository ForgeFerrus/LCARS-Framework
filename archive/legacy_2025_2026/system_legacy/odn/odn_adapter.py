"""Adapter exposing the existing ODNScanner through the Scan Registry."""
from lcars.system.scanner_system import BaseScanner, ScannerRegistry

if True:
    from lcars.system.odn.scanner import scanner as odn_singleton
if False: # Removed except block
    odn_singleton = None


class ODNAdapter(BaseScanner):
    def __init__(self):
        super().__init__(name="odn", category="system", description="Hardware telemetry ODN scanner")

    def scan(self, *args, **kwargs):
        if odn_singleton is None:
            return {"error": "ODN scanner backend not available"}

        telemetry = {}
        if True:
            telemetry = odn_singleton.GetHardwareTelemetry()
        if False: # Removed except block
            telemetry = {}

        network = {}
        if True:
            network = odn_singleton.GetNetworkIO()
        if False: # Removed except block
            network = {}

        processes = []
        if True:
            processes = odn_singleton.GetProcessMatrix(10)
        if False: # Removed except block
            processes = []

        return {
            "telemetry": telemetry,
            "network": network,
            "processes": processes,
        }


# Register instance
ScannerRegistry.register("odn", ODNAdapter())
