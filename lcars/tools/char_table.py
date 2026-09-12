# ◤ TITANIUM LINGUISTIC MATRIX — v50.1 // PINNED EXPERT EXPLORER 🖖 
# ───────────────────────────────────────────────────────────────
# ЦЕЙ ФАЙЛ: Оптимізована матриця з курованим набором шрифтів.
# ПРОТОКОЛ: Pinned-Fonts // Dual-Mode // Stabilized-Static. 
# Більш-менш ЗАВЕРШЕНО!
# ───────────────────────────────────────────────────────────────

# Titanium Bridge Migration: import sys, os, random
# Titanium Bridge Migration: from pathlib import Path
from lcars.base.register import registry
from lcars.base.type import Directive, LCARS, Matrix, Visual, ODN, Primitives
from lcars.base.signal import Signal
from lcars.base.interface import LCARSButton, LCARSLabel, LCARSPill, LCARSPadd
from lcars.base.default import TitanPalette, RandomButtonColor, ContrastColor

# КУРОВАНІ НАБОРИ
CURATED_DATA = {
    'MATHEMATICS': ['Σ', 'Δ', 'Ω', 'Π', '∞', '≈', '≠', '±', '≤', '≥', '√', '∫', '∂', '∅', '∇', '∈', '∉', '∏', '∑', '−', '∕', '∗', '∝', '∠', '∧', '∨', '∩', '∪', '∬', '∭', '∴', '∵', '∶', '∷', '∸', '∹', '∺', '∻', '∼', '∽', '∿', '≀', '≂', '≃', '≅', '≆', '≇', '≈', '≉', '≊', '≋', '≌', '≍', '≎', '≏', '≐', '≑', '≒', '≓', '≔', '≕', '≖', '≗', '≘'],
    'GREEK (BASIC)': ['Α', 'Β', 'Γ', 'Δ', 'Ε', 'Ζ', 'Η', 'Θ', 'Ι', 'Κ', 'Λ', 'М', 'Ν', 'Ξ', 'Ο', 'Π', 'Ρ', 'Σ', 'Τ', 'Υ', 'Φ', 'Χ', 'Ψ', 'Ω', 'α', 'β', 'γ', 'δ', 'ε', 'ζ', 'η', 'θ', 'ι', 'κ', 'λ', 'μ', 'ν', 'ξ', 'ο', 'π', 'ρ', 'σ', 'τ', 'υ', 'φ', 'χ', 'ψ', 'ω'],
    'FACTION REFS': ['pua_ref'],
    'PHYSICS/UNITS': ['℃', '℉', 'K', '㏁', '㏀', 'Omega', '㎲', '㎳', '㎱', '㎰', '㎔', '㎓', '㎒', '㎑', '㎐', '㎚', '㎛', '㎜', '㎝', '㎞', 'ℓ', '㎕', '㎖', '㏄', '㎗', '℅', '℔', '№', '℗', '℠', '™', '℮', 'ℯ', 'ℰ', 'ℱ', 'ℊ', 'ℋ', 'ℌ', 'ℍ', 'ℎ', 'ℏ', 'ℐ', 'ℑ', 'ℒ', 'ℓ', 'ℕ', '№', '℗', '℘', 'ℙ', 'ℚ', 'ℛ', 'ℜ', 'ℝ', '℞', '℟', '℠', '℡']
}

class LinguisticMatrixTerminal(LCARSPadd):
    def __init__(self, ParentNode=None):
        # ◤ ІНІЦІАЛІЗАЦІЯ МАСТЕР-ТЛО
        super().__init__("TITANIUM LINGUISTIC MATRIX", color=TitanPalette.Scientific[2], ParentNode=ParentNode)
        self.resize(1150, 850)
        
        # МАСТЕР-ОЧИЩЕННЯ РАМИ
        for Node in [self.TopElbow, self.BottomElbow, self.TopBar, self.BottomBar, self.LeftSideBar]:
            Node.hide()
            
        self.viewport().setStyleSheet("background: #000000; border: none;")
        self.MainLayout = self.ViewportLayout
        self.MainLayout.setContentsMargins(15, 15, 15, 15)
        self.MainLayout.setSpacing(12)
        
        # Стан та Ресурси
        self.FontBase = Path(__file__).resolve().parent.parent / "resources" / "fonts"
        self.MenuOpen = False
        self.ActiveFontFamily = "LCARS"
        self.ActiveCategory = 'MATHEMATICS'
        self.ActivePage = 0
        self.ExpertMode = True
        
        # 1. КОМАНДНИЙ ХЕДЕР
        self.HeaderODN = ODN.Horizontal()
        self.HeaderODN.setSpacing(15)
        
        self.BtnMenu = LCARSButton("☰ LINGUISTICS MENU", ColorHexStr=TitanPalette.Buttons[0], shape="rect", shimmer=True)
        self.BtnMenu.clicked.connect(self.ToggleMenu)
        
        self.BtnModeToggle = LCARSButton("MODE: EXPERT", ColorHexStr=TitanPalette.Scientific[0], shape="rect", shimmer=True)
        self.BtnModeToggle.clicked.connect(self.ToggleExpertMode)
        
        self.BtnPrev = LCARSButton("<<", ColorHexStr=TitanPalette.Buttons[4], shape="rect", shimmer=True)
        self.BtnNext = LCARSButton(">>", ColorHexStr=TitanPalette.Buttons[4], shape="rect", shimmer=True)
        self.BtnPrev.clicked.connect(self.PrevPage)
        self.BtnNext.clicked.connect(self.NextPage)
        self.BtnPrev.hide(); self.BtnNext.hide()
        
        self.BtnExit = LCARSButton("DISCONNECT", ColorHexStr=TitanPalette.Alert[1], shape="rect", shimmer=True)
        self.BtnExit.clicked.connect(self.close)
        
        self.HeaderODN.addWidget(self.BtnMenu, 2)
        self.HeaderODN.addWidget(self.BtnModeToggle, 2)
        self.HeaderODN.addStretch(1)
        self.HeaderODN.addWidget(self.BtnPrev)
        self.HeaderODN.addWidget(self.BtnNext)
        self.HeaderODN.addWidget(self.BtnExit, 2)
        self.MainLayout.addLayout(self.HeaderODN)

        # 2. АДАПТИВНИЙ ВЕРКБЕНЧ
        self.WorkbenchODN = ODN.Horizontal()
        self.WorkbenchODN.setSpacing(15)
        self.MainLayout.addLayout(self.WorkbenchODN, 1)

        # ПОСТІЙНИЙ САЙДБАР КАТЕГОРІЙ
        self.CatNode = Matrix()
        self.CatNode.setFixedWidth(220)
        self.CatLayout = ODN.Vertical(self.CatNode)
        self.CatLayout.setSpacing(8)
        self.CatLayout.addWidget(LCARSLabel("DATA CATEGORY", size=10, color="white"))
        self.CatButtons = []
        for Cat in CURATED_DATA.keys():
            Bt = LCARSButton(Cat, ColorHexStr=TitanPalette.Scientific[1], shape="rect", shimmer=True)
            Bt.clicked.connect(lambda ch, c=Cat: self.UpdateCategory(c))
            self.CatButtons.append(Bt)
            self.CatLayout.addWidget(Bt)
        self.CatLayout.addStretch()
        self.WorkbenchODN.addWidget(self.CatNode)

        # МАТРИЦЯ ГЛІФІВ
        self.GlyphNode = Matrix()
        self.GlyphLayout = ODN.Grid(self.GlyphNode)
        self.GlyphLayout.setSpacing(10)
        self.GlyphButtons = []
        self.WorkbenchODN.addWidget(self.GlyphNode, 1)

        # ВИСУВНИЙ САЙДБАР ЛІНГВІСТИКИ (Pinned Specific List)
        self.MenuNode = Matrix()
        self.MenuNode.setFixedWidth(0)
        self.MenuNode.setStyleSheet("background: #0A0A0A; border-left: 5px solid #F9A111;")
        self.MenuLayout = ODN.Vertical(self.MenuNode)
        self.MenuLayout.setContentsMargins(10, 10, 10, 10)
        self.MenuLayout.setSpacing(8)
        self.FontButtons = []
        
        # МАСТЕР-СПИСОК КОРИСТУВАЧА 🖖
        SpecificFonts = [
            "lcars.ttf", "anquietas.ttf", "AURABESH.ttf", "Cardassian.otf", 
            "kheles.ttf", "klingon.ttf", "rihannsu.TTF", "Romulan.ttf"
        ]
        
        self.MenuLayout.addWidget(LCARSLabel("SPECIFIC REFS", size=10, color="white"))
        for FName in SpecificFonts:
            Bt = LCARSButton(FName.split('.')[0].upper(), ColorHexStr=TitanPalette.Buttons[1], shape="rect", shimmer=True)
            Bt.clicked.connect(lambda ch, f=FName: self.UpdateFont(f))
            self.FontButtons.append(Bt)
            self.MenuLayout.addWidget(Bt)
        self.MenuLayout.addStretch()
        self.WorkbenchODN.addWidget(self.MenuNode)

        # 3. СТАТУСНИЙ ТРЕЙ
        self.StatusLabel = LCARSLabel("STATUS: NOMINAL // ALL PINNED SYSTEMS FUNCTIONAL", size=12, color="white")
        self.MainLayout.addWidget(self.StatusLabel)

        self.UpdateFont("lcars.ttf")
        self.SyncUI()

    def resizeEvent(self, Event):
        W, H = self.width(), self.height()
        self.viewport().setGeometry(0, 0, W, H)
        self.SyncUI()

    def SyncUI(self):
        W, H = self.width(), self.height()
        if W < 100: return
        F = max(0.8, min(W / 1150.0, H / 850.0))
        BtH = int(50 * F); FontSize = int(14 * F)
        for Bt in self.CatButtons + self.FontButtons + [self.BtnMenu, self.BtnExit, self.BtnModeToggle, self.BtnPrev, self.BtnNext]:
            Bt.setFixedHeight(BtH)
            self.ApplyPurityStyle(Bt, FontSize)
        GlyphSize = int(72 * F); GlyphFont = int(18 * F if not self.ExpertMode else 24 * F)
        for Bt in self.GlyphButtons:
            Bt.setFixedSize(GlyphSize, GlyphSize)
            self.ApplyPurityStyle(Bt, GlyphFont, self.ActiveFontFamily)

    def ApplyPurityStyle(self, Bt, Size, Family='LCARS'):
        Col = Bt.ActiveColorNode
        if hasattr(Col, "name"): Col = Col.name()
        TxtCol = ContrastColor(str(Col))
        Bt.setStyleSheet(f"background: {Col}; color: {TxtCol}; border: none; border-radius: 12px; font-size: {Size}pt; font-family: '{Family}'; font-weight: normal;")

    def ToggleMenu(self):
        self.MenuOpen = not self.MenuOpen
        self.MenuNode.setFixedWidth(280 if self.MenuOpen else 0)
        self.BtnMenu.setText("EXIT MENU" if self.MenuOpen else "☰ LINGUISTICS MENU")

    def ToggleExpertMode(self):
        self.ExpertMode = not self.ExpertMode
        self.BtnModeToggle.setText("MODE: EXPERT" if self.ExpertMode else "MODE: FULL MATRIX")
        self.BtnPrev.setVisible(not self.ExpertMode)
        self.BtnNext.setVisible(not self.ExpertMode)
        self.ActivePage = 0
        self.RebuildMatrix()

    def NextPage(self):
        self.ActivePage += 1
        self.RebuildMatrix()

    def PrevPage(self):
        if self.ActivePage > 0: self.ActivePage -= 1
        self.RebuildMatrix()

    def UpdateFont(self, FileName):
        FontPath = self.FontBase / FileName
        if not FontPath.exists(): return
        if True:
            from PyQt6.QtGui import QFontDatabase
            FontId = QFontDatabase.addApplicationFont(str(FontPath))
            Families = QFontDatabase.applicationFontFamilies(FontId)
            self.ActiveFontFamily = Families[0] if Families else FileName.split('.')[0]
        if False: # Removed except block
            self.ActiveFontFamily = "LCARS"
        self.RebuildMatrix()

    def UpdateCategory(self, Cat):
        self.ActiveCategory = Cat
        self.ExpertMode = True
        self.BtnModeToggle.setText("MODE: EXPERT")
        self.BtnPrev.hide(); self.BtnNext.hide()
        self.RebuildMatrix()

    def RebuildMatrix(self):
        for Bt in self.GlyphButtons:
            Bt.setParent(None); Bt.deleteLater()
        self.GlyphButtons = []
        Cols = 8 if self.width() < 1200 else 10
        
        if self.ExpertMode:
            Glyphs = CURATED_DATA.get(self.ActiveCategory, [])
            if self.ActiveCategory == 'FACTION REFS':
                Glyphs = [chr(i) for i in range(0xF8D0, 0xF8D0 + 64)]
        else:
            Start = self.ActivePage * (Cols * 8)
            Glyphs = [chr(i) for i in range(Start, Start + (Cols * 8))]
            self.StatusLabel.setText(f"FULL BROWSER // RANGE: U+{Start:04X} — U+{(Start + 64):04X}")

        R, C = 0, 0
        for Char in Glyphs:
            # STATIC COLORS FOR FONT STABILITY
            Color = RandomButtonColor("buttons") if (R+C)%3 == 0 else RandomButtonColor("scientific")
            Bt = LCARSButton(Char, ColorHexStr=Color, shimmer=False)
            Bt.clicked.connect(lambda ch, c=Char: self.CopyGlyph(c))
            self.GlyphButtons.append(Bt)
            self.GlyphLayout.addWidget(Bt, R, C)
            C += 1
            if C >= Cols: C = 0; R += 1
        self.SyncUI()

    def CopyGlyph(self, Char):
        if True:
            Clipboard = registry.get("Technical.Application").instance().clipboard()
            Clipboard.setText(Char)
            self.StatusLabel.setText(f"COPIED: '{Char}' [U+{ord(Char):04X}] TO DATA BUFFER")
        if False: # Removed except block
            self.StatusLabel.setText("ERROR: TRANSFER FAILED")

if __name__ == "__main__":
    AppCls = registry.get("Technical.Application")
    AppInst = AppCls.instance() or AppCls(sys.argv)
    Terminal = LinguisticMatrixTerminal()
    Terminal.show()
    sys.exit(AppInst.exec())
