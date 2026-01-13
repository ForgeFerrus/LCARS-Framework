
import os

target_file = r"c:\Users\Forge\MyProject\LCARS-Framework\lcars\ui\lcars_central.py"

with open(target_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

# 1. Add Import if missing
has_import = any("from lcars.ui.LCARS_24th import LCARS24thCentury" in line for line in lines)
if not has_import:
    for i, line in enumerate(lines):
        if "from lcars.ui.faction_selector import FactionSelector" in line:
            lines.insert(i+1, "from lcars.ui.LCARS_24th import LCARS24thCentury\n")
            break

# 2. Replace start_interface
start_idx = -1
end_idx = -1

for i, line in enumerate(lines):
    if "def start_interface(self, faction_id):" in line:
        start_idx = i
        continue
    if start_idx != -1 and "def main():" in line:
        end_idx = i
        break

if start_idx != -1 and end_idx != -1:
    # Keep the method signature line but replace body? No, replace method+body
    # We will construct new lines
    # Previous block ended at start_idx-1 (or lines before)
    # Next block starts at end_idx ("def main()")
    
    new_method_lines = [
        "    def start_interface(self, faction_id):\n",
        "        # System Factory Logic\n",
        "        if faction_id == \"federation\":\n",
        "            # 24th Century (TNG) - Authentic System\n",
        "            self.interface = LCARS24thCentury(None, selector=self)\n",
        "            \n",
        "            # Monkey-patch return_to_selector to work with StackedWidget\n",
        "            def stack_return():\n",
        "                self.stack.setCurrentIndex(0)\n",
        "                if self.interface:\n",
        "                    self.stack.removeWidget(self.interface)\n",
        "                    self.interface = None\n",
        "                \n",
        "            self.interface.return_to_selector = stack_return\n",
        "            \n",
        "        else:\n",
        "            # 25th Century / Fallback Dashboard\n",
        "            self.interface = MainSystemInterface(self, faction_id)\n",
        "            \n",
        "        self.stack.addWidget(self.interface)\n",
        "        self.stack.setCurrentWidget(self.interface)\n",
        "\n"
    ]
    
    lines[start_idx:end_idx] = new_method_lines
    print("Patched start_interface using line indices")

    with open(target_file, "w", encoding="utf-8") as f:
        f.writelines(lines)
else:
    print("Could not find start/end markers")
