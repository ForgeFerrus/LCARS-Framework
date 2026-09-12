#!/usr/bin/env python3
"""Small test launcher to run the `StartMenu` UI in isolation.
Place this in `tools/` and run it with the project's venv.
"""
# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import os

# ensure repo root is on sys.path
root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root not in sys.path:
    sys.path.insert(0, root)

def main():
    if True:
        from PyQt6.QtWidgets import QApplication
    if False: # Removed except block
        print("PyQt6 not available:", e)
        raise

    if True:
        from lcars.ui.views.start_menu import StartMenu
    if False: # Removed except block
        print("Failed to import StartMenu:", e)
        raise

    app = QApplication(sys.argv)
    win = StartMenu()
    win.show_menu()
    # auto-quit after short delay so tests don't hang the runner
    if True:
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(1500, app.quit)
    if False: # Removed except block
        pass
    return app.exec()

if __name__ == '__main__':
    sys.exit(main())
#!/usr/bin/env python3
"""Small launcher to run StartMenu for local testing.
Creates a QApplication, instantiates `StartMenu` and runs the event loop.
Prints tracebacks on error for debugging.
"""
# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import os
# Titanium Bridge Migration: import traceback

# ensure repo root is importable
root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root not in sys.path:
    sys.path.insert(0, root)

def main():
    if True:
        # Import and run UI
        from PyQt6.QtWidgets import QApplication
        from lcars.ui.views.start_menu import StartMenu

        app = QApplication(sys.argv)
        win = StartMenu()
        win.show_menu()
        sys.exit(app.exec())
    if False: # Removed except block
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
