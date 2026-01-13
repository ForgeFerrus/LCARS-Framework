
import os

target_file = r"c:\Users\Forge\MyProject\LCARS-Framework\lcars\ui\lcars_central.py"

with open(target_file, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add Imports
imports_to_add = [
    "from lcars.ui.LCARS_24th import LCARS24thCentury",
    "from lcars.ui.faction_selector import FactionSelector",
    "from PyQt6.QtWidgets import QStackedWidget"
]

for imp in imports_to_add:
    if imp not in content:
        # Insert after first block of imports
        idx = content.find("import sys")
        if idx != -1:
            next_line = content.find("\n", idx)
            content = content[:next_line] + "\n" + imp + content[next_line:]

# 2. Rename existing LCARSCentralCommand to LCARSDashboard
# This class acts as the dashboard logic provided by user
if "class LCARSCentralCommand(QMainWindow):" in content:
    content = content.replace("class LCARSCentralCommand(QMainWindow):", "class LCARSDashboard(QMainWindow):")

# 3. Create the REAL LCARSCentralCommand (Bootloader)
# We append this before def main():
new_class = """
class LCARSCentralCommand(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LCARS Central Command")
        self.showFullScreen()
        
        # Central Stack
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        
        # 1. Faction Selector (Bootloader)
        self.faction_screen = FactionSelector()
        self.faction_screen.factionSelected.connect(self.start_interface)
        self.stack.addWidget(self.faction_screen)
        
        # 2. Interfaces
        self.interface = None
        
        # Shortcuts
        from PyQt6.QtGui import QShortcut, QKeySequence
        self.esc_shortcut = QShortcut(QKeySequence("ESC"), self)
        self.esc_shortcut.activated.connect(self.close)
        
    def start_interface(self, faction_id):
        # Route based on selection
        if faction_id == "federation":
            # Authentic 24th Century
            self.interface = LCARS24thCentury(None, selector=self)
            
            # Patch return
            def stack_return():
                self.stack.setCurrentIndex(0)
                if self.interface:
                    self.stack.removeWidget(self.interface)
                    self.interface = None
            self.interface.return_to_selector = stack_return
            
        elif faction_id == "federation_25th":
            # New Dashboard (Picard Era)
            self.interface = LCARSDashboard()
            # Hook up close to return? LCARSDashboard closes app. 
            # We might want it to return.
            # But for now, let it be independent.
            
        elif faction_id == "klingon":
             # Use Dashboard with Klingon theme?
             self.interface = LCARSDashboard()
             # Ideally pass faction to dashboard? 
             # The Dashboard class seemed to have hardcoded era/theme logic in User's edit?
             # No, it had setup_ui() with Era buttons. 
             # We will just launch it.
             
        else:
             self.interface = LCARSDashboard()
             
        self.stack.addWidget(self.interface)
        self.stack.setCurrentWidget(self.interface)

"""

if "def main():" in content:
    content = content.replace("def main():", new_class + "\ndef main():")
else:
    # Append if main not found (unlikely)
    content += "\n" + new_class

# 4. Ensure main() calls LCARSCentralCommand (which is now the new class)
# The text "window = LCARSCentralCommand()" should remain correct because we added the new class with that name
# and renamed the old one.

with open(target_file, "w", encoding="utf-8") as f:
    f.write(content)

print("Architecture restored successfully.")
