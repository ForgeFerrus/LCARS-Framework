#!/usr/bin/env python3
"""Test script to verify launcher is actually visible and working."""

import sys
from PyQt6.QtWidgets import QApplication
from lcars.ui.launcher import LCARSLauncher

if __name__ == "__main__":
    print("[TEST] Creating QApplication")
    app = QApplication(sys.argv)
    QApplication.setStyle('Fusion')
    
    print("[TEST] Creating LCARSLauncher")
    launcher = LCARSLauncher(require_auth=True)
    
    print(f"[TEST] Launcher geometry: {launcher.geometry()}")
    print(f"[TEST] Launcher size: {launcher.size()}")
    print(f"[TEST] Launcher isVisible: {launcher.isVisible()}")
    
    print("[TEST] Showing launcher window")
    launcher.show()
    
    print(f"[TEST] After show() - isVisible: {launcher.isVisible()}")
    print(f"[TEST] Launcher geometry: {launcher.geometry()}")
    
    launcher.raise_()
    launcher.activateWindow()
    
    print("[TEST] Launcher raised and activated")
    print("[TEST] Starting event loop...")
    
    sys.exit(app.exec())
