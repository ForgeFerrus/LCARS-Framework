"""One-shot bulk fixer for programs/english_learning/*.py

Run from repo root:
    python tools/fix_english_app.py
"""
# Titanium Bridge Migration: import re
# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: from pathlib import Path

ROOT = Path(__file__).parent.parent

# ══════════════════════════════════════════════════════════════════════════════
# app.py
# ══════════════════════════════════════════════════════════════════════════════
def fix_app():
    p = ROOT / "programs/english_learning/app.py"
    t = p.read_text(encoding="utf-8")

    t = t.replace(
        "from lcars.themes.theme import setup_lcars_font",
        "from lcars.base.defaults import FontSetup, TitanPalette",
    )

    # Remove _PALETTE / _get_theme block
    t = re.sub(
        r"_PALETTE = \[.*?\]\n\ndef _get_theme\(\):\n    return \{.*?\}\n",
        "",
        t,
        flags=re.DOTALL,
    )

    # Fix double theme assignment in __init__
    t = t.replace(
        '        self.theme = _get_theme()\n',
        '        self.theme = {"palette": TitanPalette.Buttons}\n',
    )
    # Remove broken second assignment + duplicate dicts
    t = re.sub(
        r"        self\.theme = get_theme\(self\.era, self\.faction\)\n"
        r"        \n"
        r"        self\.panels = \{\}\n"
        r"        self\.buttons = \{\}\n",
        "",
        t,
    )

    # Rename method calls in __init__
    t = t.replace(
        '        self._build_ui()\n        self._switch("dashboard")',
        '        self.BuildUI()\n        self.SwitchPanel("dashboard")',
    )

    # Rename method definitions
    t = t.replace("    def _build_ui(self):", "    def BuildUI(self):")
    t = t.replace("        self._init_panels()", "        self.InitPanels()")
    t = t.replace("    def _init_panels(self):", "    def InitPanels(self):")
    t = t.replace("connect(self._switch)", "connect(self.SwitchPanel)")
    t = t.replace("    def _switch(self, key):", "    def SwitchPanel(self, key):")
    t = t.replace("setup_lcars_font()", "FontSetup()")

    p.write_text(t, encoding="utf-8")
    print("app.py  ✓")


# ══════════════════════════════════════════════════════════════════════════════
# interface.py
# ══════════════════════════════════════════════════════════════════════════════
def fix_interface():
    p = ROOT / "programs/english_learning/interface.py"
    t = p.read_text(encoding="utf-8")

    # get_font_style → FontStyle (remove faction arg)
    t = re.sub(
        r"get_font_style\((\d+),\s*'(\w+)',\s*self\.faction\)",
        lambda m: f"FontStyle({m.group(1)}, '{m.group(2)}')",
        t,
    )
    t = re.sub(
        r"get_font_style\((\d+),\s*'(\w+)'\)",
        lambda m: f"FontStyle({m.group(1)}, '{m.group(2)}')",
        t,
    )

    # LCARSEra references
    t = re.sub(r",\s*LCARSEra\.\w+", "", t)
    t = t.replace("theme.get('era', LCARSEra.LCARS_25TH)", "None")
    t = t.replace("theme.get('era')", "None")
    t = re.sub(r"self\.era = theme\.get\('[^']+',?\s*(?:LCARSEra\.\w+)?\)", "self.era = None", t)

    # Remove era=/faction=/direction= kwargs
    t = re.sub(r",\s*era=self\.era", "", t)
    t = re.sub(r",\s*era=self\.theme\[.era.\]", "", t)
    t = re.sub(r",\s*faction=self\.faction", "", t)
    t = re.sub(r",\s*direction=\"(?:horizontal|vertical)\"", "", t)

    # Fix LCARSSegment color= → ColorHexStr=
    t = re.sub(r"\bLCARSSegment\(color=", "LCARSSegment(ColorHexStr=", t)

    # Fix LCARSButton: ("text", palette[N], ...) → ("text", "none", palette[N], radius=4)
    # Pattern: LCARSButton("...",  or  LCARSButton(f"...",
    t = re.sub(
        r'LCARSButton\((f?["\'][^"\']*["\'])',
        r'LCARSButton(\1, "none"',
        t,
    )
    # Remove shape='rect'
    t = re.sub(r",\s*shape=['\"]rect['\"]", ", radius=4", t)
    # Remove duplicate radius=4 if already had radius=4 added above
    t = re.sub(r",\s*radius=4(,\s*radius=4)+", ", radius=4", t)

    # Method renames
    t = t.replace("self._style_combo(", "self.StyleCombo(")
    t = t.replace("    def _style_combo(self,", "    def StyleCombo(self,")
    t = t.replace("self._create_stat_block(", "self.CreateStatBlock(")
    t = t.replace("    def _create_stat_block(self,", "    def CreateStatBlock(self,")
    t = t.replace("self._update_progress_indicators(", "self.UpdateProgressIndicators(")
    t = t.replace("self._update_metrics(", "self.UpdateMetrics(")
    t = t.replace("    def _update_progress_indicators(self", "    def UpdateProgressIndicators(self")
    t = t.replace("    def _update_metrics(self", "    def UpdateMetrics(self")

    p.write_text(t, encoding="utf-8")
    print("interface.py  ✓")


# ══════════════════════════════════════════════════════════════════════════════
# widgets_extra.py
# ══════════════════════════════════════════════════════════════════════════════
def fix_widgets_extra():
    p = ROOT / "programs/english_learning/widgets_extra.py"
    t = p.read_text(encoding="utf-8")

    # Replace local get_font_style def with import
    t = re.sub(
        r"def get_font_style\(size=14, weight='normal', faction=None\):\n"
        r"    return f\"font-family: 'LCARS'; font-size: \{size\}pt; font-weight: \{weight\};\"\n",
        "",
        t,
    )

    # Add FontStyle import after LCARSButton import
    if "from lcars.base.defaults import FontStyle" not in t:
        t = t.replace(
            "from lcars.base.interface import LCARSButton",
            "from lcars.base.interface import LCARSButton\nfrom lcars.base.defaults import FontStyle",
        )

    # get_font_style → FontStyle
    t = re.sub(
        r"get_font_style\((\d+),\s*'(\w+)',\s*self\.faction\)",
        lambda m: f"FontStyle({m.group(1)}, '{m.group(2)}')",
        t,
    )
    t = re.sub(
        r"get_font_style\((\d+),\s*'(\w+)'\)",
        lambda m: f"FontStyle({m.group(1)}, '{m.group(2)}')",
        t,
    )

    # Fix LCARSButton calls
    t = re.sub(
        r'LCARSButton\((f?["\'][^"\']*["\'])',
        r'LCARSButton(\1, "none"',
        t,
    )
    t = re.sub(r",\s*shape=['\"]rect['\"]", ", radius=4", t)
    t = re.sub(r",\s*era=self\.theme\[.era.\]", "", t)
    t = re.sub(r",\s*faction=self\.faction", "", t)
    t = re.sub(r",\s*radius=4(,\s*radius=4)+", ", radius=4", t)

    # Method renames
    t = t.replace("self._style_combo(", "self.StyleCombo(")
    t = t.replace("    def _style_combo(self,", "    def StyleCombo(self,")
    t = t.replace("self._check_answer(", "self.CheckAnswer(")
    t = t.replace("    def _check_answer(self,", "    def CheckAnswer(self,")
    t = t.replace("self._load_quiz_question(", "self.LoadQuizQuestion(")
    t = t.replace("    def _load_quiz_question(self", "    def LoadQuizQuestion(self")
    t = t.replace("self._refresh_rule_list(", "self.RefreshRuleList(")
    t = t.replace("    def _refresh_rule_list(self,", "    def RefreshRuleList(self,")
    t = t.replace("self._load_rule(", "self.LoadRule(")
    t = t.replace("    def _load_rule(self,", "    def LoadRule(self,")

    p.write_text(t, encoding="utf-8")
    print("widgets_extra.py  ✓")


# ══════════════════════════════════════════════════════════════════════════════
# tenses.py — verify no leftover get_font_style
# ══════════════════════════════════════════════════════════════════════════════
def fix_tenses():
    p = ROOT / "programs/english_learning/ui/tenses.py"
    t = p.read_text(encoding="utf-8")

    # In case any get_font_style survived
    t = re.sub(
        r"get_font_style\((\d+),\s*'(\w+)',?\s*(?:self\.faction)?\s*\)",
        lambda m: f"FontStyle({m.group(1)}, '{m.group(2)}')",
        t,
    )

    # Fix LCARSSegment color= → ColorHexStr=
    t = re.sub(r"\bLCARSSegment\(color=", "LCARSSegment(ColorHexStr=", t)

    p.write_text(t, encoding="utf-8")
    print("tenses.py  ✓")


# ══════════════════════════════════════════════════════════════════════════════
# All files: fix get_sound_manager → GetSoundManager and .play() → .PlayAudioClip()
# ══════════════════════════════════════════════════════════════════════════════
def fix_sound_manager():
    files = [
        ROOT / "programs/english_learning/app.py",
        ROOT / "programs/english_learning/interface.py",
        ROOT / "programs/english_learning/widgets_extra.py",
        ROOT / "programs/english_learning/ui/tenses.py",
    ]
    for p in files:
        t = p.read_text(encoding="utf-8")
        t = t.replace("from lcars.modules.sound_manager import get_sound_manager",
                      "from lcars.modules.sound_manager import GetSoundManager")
        t = t.replace("get_sound_manager()", "GetSoundManager()")
        t = re.sub(r'GetSoundManager\(\)\.play\(', 'GetSoundManager().PlayAudioClip(', t)
        p.write_text(t, encoding="utf-8")
    print("sound_manager refs  ✓")


if __name__ == "__main__":
    fix_app()
    fix_interface()
    fix_widgets_extra()
    fix_tenses()
    fix_sound_manager()
    print("All done.")
