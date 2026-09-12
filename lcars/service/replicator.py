# ◤ TITANIUM LCARS :: REPLICATOR SERVICE (UI PATTERN REPLICATOR) 🖖
# =============================================================================
# ФАЙЛ: lcars/service/replicator.py
# ОПИС: Сервіс-реплікатор Бортового Комп'ютера (Replicator Service).
# ВІДПОВІДАЛЬНІСТЬ:
# 1. Матеріалізація канонічних станцій (Nova IDE, Desktop, Terminal).
# 2. Динамічне створення інтерфейсних декорацій та панелей для агентів без сторонніх Q-віджетів.
# 3. Використання виключно канонічної палітри LCARS (Palette.Buttons, Palette.Yellow, Palette.Red).
# 4. Взаємодія з базою компонентів (01-0007) та ізолінійних чіпів (08-0003).
# СТАНДАРТ: Titanium LCARS (Zero-Except, Zero-Underscores, Strict PascalCase, Pure Classes).
# =============================================================================

from __future__ import annotations
from typing import Any, Dict, List, Optional
from lcars.base.type import LCARS
from lcars.base.default import Palette
from lcars.base.component import LCARSButton, LCARSLabel, LCARSElbow, LCARSBar, LCARSIndicator, ActiveAudio
from lcars.base.interface import Screen, Panel, Segment, ScanningBar

SqliteMod = LCARS.Import("sqlite3")
PathMod = LCARS.Import("pathlib")
JsonMod = LCARS.Import("json")
SysMod = LCARS.Import("sys")

class ThemePaletteQuery:
    @staticmethod
    def Resolve(DbPath: Any, EraId: str = "PALETTE-24TH-SOVEREIGN") -> Dict[str, str]:
        Canonical = {
            "Primary": Palette.Buttons[0],
            "Secondary": Palette.Buttons[1],
            "Accent": Palette.Buttons[2],
            "Background": Palette.Background,
            "Border": Palette.Buttons[1],
            "Text": "#FFFFFF",
            "Warning": Palette.Yellow[0],
            "Alert": Palette.Red[0],
            "Disabled": Palette.Disabled[0],
            "EditorBg": "#000000",
            "EditorFg": Palette.Buttons[2],
            "TerminalBg": "#000000",
            "TerminalFg": Palette.Yellow[1],
            "CopilotBg": "#000000",
            "CopilotFg": Palette.Buttons[1],
        }
        if not SqliteMod or not DbPath:
            return Canonical

        PathObj = DbPath if hasattr(DbPath, "exists") else (PathMod.Path(str(DbPath)) if PathMod else None)
        if not PathObj or not PathObj.exists():
            return Canonical

        Conn = SqliteMod.connect(str(PathObj))
        Cur = Conn.cursor()
        Cur.execute(
            "SELECT primary_color, secondary_color, accent_color, background_color FROM color_palettes WHERE palette_id = ?",
            (EraId,)
        )
        Row = Cur.fetchone()
        if Row and len(Row) >= 4:
            Canonical["Primary"] = str(Row[0])
            Canonical["Secondary"] = str(Row[1])
            Canonical["Accent"] = str(Row[2])
            Canonical["Background"] = str(Row[3])
            Canonical["Border"] = str(Row[1])

        Cur.execute(
            "SELECT token_name, color_hex FROM theme_tokens WHERE palette_id = ?",
            (EraId,)
        )
        TokenRows = Cur.fetchall()
        for TRow in TokenRows:
            if len(TRow) >= 2:
                Canonical[str(TRow[0])] = str(TRow[1])

        Conn.close()
        return Canonical

class ComponentRegistryQuery:
    @staticmethod
    def GetRegisteredPrimitives(DbPath: Any) -> Dict[str, Dict[str, Any]]:
        Result = {}
        if not SqliteMod or not DbPath:
            return Result
        PathObj = DbPath if hasattr(DbPath, "exists") else (PathMod.Path(str(DbPath)) if PathMod else None)
        if not PathObj or not PathObj.exists():
            return Result
        Conn = SqliteMod.connect(str(PathObj))
        Cur = Conn.cursor()
        Cur.execute("SELECT primitive_id, name, class_name, module_path, default_props FROM ui_primitives")
        Rows = Cur.fetchall()
        for Row in Rows:
            if len(Row) >= 5:
                Result[str(Row[0])] = {
                    "Name": str(Row[1]),
                    "ClassName": str(Row[2]),
                    "ModulePath": str(Row[3]),
                    "DefaultProps": str(Row[4])
                }
        Conn.close()
        return Result

    @staticmethod
    def GetRegisteredComponents(DbPath: Any) -> Dict[str, Dict[str, str]]:
        Result = {}
        if not SqliteMod or not DbPath:
            return Result
        PathObj = DbPath if hasattr(DbPath, "exists") else (PathMod.Path(str(DbPath)) if PathMod else None)
        if not PathObj or not PathObj.exists():
            return Result
        Conn = SqliteMod.connect(str(PathObj))
        Cur = Conn.cursor()
        Cur.execute("SELECT component_id, name, category, module_path, version FROM registered_components")
        Rows = Cur.fetchall()
        for Row in Rows:
            if len(Row) >= 5:
                Result[str(Row[0])] = {
                    "Name": str(Row[1]),
                    "Category": str(Row[2]),
                    "ModulePath": str(Row[3]),
                    "Version": str(Row[4])
                }
        Conn.close()
        return Result

class LCARSDynamicStation(Screen):
    def __init__(self, Spec: Dict[str, Any], PaletteData: Dict[str, str], Parent=None):
        super().__init__(Parent=Parent, Decorated=False, Color=Palette.Background)
        self.Spec = Spec
        self.PaletteData = PaletteData
        self.Title = Spec.get("Title", "DYNAMIC LCARS STATION")
        if hasattr(self.widget, "setWindowTitle"):
            self.widget.setWindowTitle(self.Title)
        self.BuildDynamicStation()

    def windowTitle(self) -> str:
        if hasattr(self.widget, "windowTitle"):
            Title = self.widget.windowTitle()
            if Title:
                return Title
        return self.Title

    def BuildDynamicStation(self):
        ContentObj = self.Items.get("Content", self)
        Content = getattr(ContentObj, "widget", ContentObj)
        ContentLayout = Content.layout() or LCARS.Vertical(Content)
        ContentLayout.setContentsMargins(10, 10, 10, 10)
        ContentLayout.setSpacing(8)

        PrimaryCol = self.PaletteData.get("Primary", Palette.Buttons[0])
        SecondaryCol = self.PaletteData.get("Secondary", Palette.Buttons[1])

        # Верхня панель (LCARS Header)
        HeaderSeg = Segment(Parent=Content)
        HeaderLayout = LCARS.Horizontal(HeaderSeg.widget)
        HeaderLayout.setContentsMargins(0, 0, 0, 0)
        HeaderLayout.setSpacing(8)

        Elbow = LCARSElbow(Direction="top-left", Color=PrimaryCol, Width=160, Height=50, Parent=HeaderSeg.widget)
        HeaderLayout.addWidget(Elbow.widget)

        TitleLabel = LCARSLabel(Text=self.Title, Color=PrimaryCol, Parent=HeaderSeg.widget)
        TitleLabel.SetFontSize(16)
        HeaderLayout.addWidget(TitleLabel.widget, 1)

        BtnClose = LCARSButton(Text="CLOSE", Form=LCARSButton.Pill, Color="#CC3333", Parent=HeaderSeg.widget)
        BtnClose.Clicked.Connect(self.close)
        HeaderLayout.addWidget(BtnClose.widget)

        ContentLayout.addWidget(HeaderSeg.widget)

        Scan = ScanningBar(Color=PrimaryCol, Parent=Content)
        ContentLayout.addWidget(Scan.widget)

        # Тіло станції (динамічні елементи агента у канонічній 2-колонковій LCARS структурі)
        BodySeg = Segment(Parent=Content)
        BodyLayout = LCARS.Horizontal(BodySeg.widget)
        BodyLayout.setContentsMargins(0, 0, 0, 0)
        BodyLayout.setSpacing(14)

        LeftCol = Segment(Parent=BodySeg.widget)
        LeftLayout = LCARS.Vertical(LeftCol.widget)
        LeftLayout.setContentsMargins(0, 0, 0, 0)
        LeftLayout.setSpacing(6)
        LeftCol.widget.setFixedWidth(340)

        RightCol = Segment(Parent=BodySeg.widget)
        RightLayout = LCARS.Vertical(RightCol.widget)
        RightLayout.setContentsMargins(0, 0, 0, 0)
        RightLayout.setSpacing(8)

        Nodes = self.Spec.get("Nodes", [])
        if not Nodes:
            WelcomeLabel = LCARSLabel(Text="DYNAMIC AGENT DECORATION BUFFER // READY", Color=PrimaryCol, Parent=RightCol.widget)
            RightLayout.addWidget(WelcomeLabel.widget)
        else:
            for Node in Nodes:
                NodeType = str(Node.get("Type", "BUTTON")).upper()
                NodeText = str(Node.get("Text", "ACTION"))
                NodeColor = str(Node.get("Color", PrimaryCol))
                if NodeType == "BUTTON":
                    B = LCARSButton(Text=NodeText, Color=NodeColor, Parent=LeftCol.widget)
                    LeftLayout.addWidget(B.widget)
                elif NodeType == "LABEL":
                    L = LCARSLabel(Text=NodeText, Color=NodeColor, Parent=RightCol.widget)
                    L.SetFontSize(14)
                    RightLayout.addWidget(L.widget)
                elif NodeType == "BAR":
                    Bar = LCARSBar(Color=NodeColor, Height=6, Parent=RightCol.widget)
                    RightLayout.addWidget(Bar.widget)

        LeftLayout.addStretch(1)
        RightLayout.addStretch(1)
        BodyLayout.addWidget(LeftCol.widget)
        BodyLayout.addWidget(RightCol.widget, 1)

        ContentLayout.addWidget(BodySeg.widget, 1)

class LCARSReplicator:
    InstanceRef = None

    def __init__(self):
        LCARSReplicator.InstanceRef = self
        PathHelper = PathMod.Path if PathMod else None
        self.RootPath = PathHelper(PathHelper(__file__).resolve().parents[2]) if PathHelper else None
        self.ThemesDbPath = self.RootPath / "lcars" / "data" / "07" / "07-0001-themes.db" if self.RootPath else None
        self.ComponentsDbPath = self.RootPath / "lcars" / "data" / "01" / "01-0007-components.db" if self.RootPath else None
        self.ChipsDbPath = self.RootPath / "lcars" / "data" / "08" / "08-0003-synthesized-chips.db" if self.RootPath else None

        self.ActivePalette = ThemePaletteQuery.Resolve(self.ThemesDbPath, "PALETTE-24TH-SOVEREIGN")
        self.RegisteredPrimitives = ComponentRegistryQuery.GetRegisteredPrimitives(self.ComponentsDbPath)
        self.RegisteredComponents = ComponentRegistryQuery.GetRegisteredComponents(self.ComponentsDbPath)
        self.PatternsCache = {}
        self.ActiveStations = {}
        self.InitChipStore()

    @classmethod
    def GetInstance(cls) -> LCARSReplicator:
        if cls.InstanceRef is None:
            cls.InstanceRef = LCARSReplicator()
        return cls.InstanceRef

    def InitChipStore(self):
        if not SqliteMod or not self.ChipsDbPath:
            return
        DbDir = self.ChipsDbPath.parent
        if not DbDir.exists():
            DbDir.mkdir(parents=True, exist_ok=True)
        Conn = SqliteMod.connect(str(self.ChipsDbPath))
        Cur = Conn.cursor()
        Cur.execute("""
            CREATE TABLE IF NOT EXISTS synthesized_chips (
                chip_id TEXT PRIMARY KEY,
                title TEXT,
                category TEXT,
                stardate TEXT,
                schema_json TEXT
            )
        """)
        Conn.commit()
        Conn.close()

    def StorePatternToChip(self, ChipId: str, Title: str, Category: str, Spec: Dict[str, Any]) -> bool:
        if not SqliteMod or not JsonMod or not self.ChipsDbPath:
            return False
        CleanId = str(ChipId).strip().upper()
        JsonData = JsonMod.dumps(Spec, indent=2)
        Conn = SqliteMod.connect(str(self.ChipsDbPath))
        Cur = Conn.cursor()
        Cur.execute("""
            INSERT OR REPLACE INTO synthesized_chips (chip_id, title, category, stardate, schema_json)
            VALUES (?, ?, ?, datetime('now'), ?)
        """, (CleanId, Title, Category, JsonData))
        Conn.commit()
        Conn.close()
        self.PatternsCache[CleanId.lower()] = Spec
        return True

    def LoadPatternFromChip(self, ChipId: str) -> Optional[Dict[str, Any]]:
        CleanId = str(ChipId).strip().lower()
        if CleanId in self.PatternsCache:
            return self.PatternsCache[CleanId]
        if not SqliteMod or not JsonMod or not self.ChipsDbPath or not self.ChipsDbPath.exists():
            return None
        Conn = SqliteMod.connect(str(self.ChipsDbPath))
        Cur = Conn.cursor()
        Cur.execute("SELECT schema_json FROM synthesized_chips WHERE lower(chip_id) = ?", (CleanId,))
        Row = Cur.fetchone()
        Conn.close()
        if Row and Row[0]:
            Parsed = JsonMod.loads(Row[0])
            self.PatternsCache[CleanId] = Parsed
            return Parsed
        return None

    def Materialize(self, Target: Any = "nova", Parent=None) -> Any:
        Spec = None
        if isinstance(Target, dict):
            Spec = Target
        elif isinstance(Target, str) and ("{" in Target or "[" in Target):
            Raw = Target.strip()
            if "```json" in Raw:
                Raw = Raw.split("```json", 1)[1].split("```", 1)[0].strip()
            elif "```" in Raw:
                Raw = Raw.split("```", 1)[1].split("```", 1)[0].strip()
            Start = Raw.find("{")
            End = Raw.rfind("}")
            if Start != -1 and End > Start:
                from lcars.core.computer import SafeJsonParse
                Parsed = SafeJsonParse(Raw[Start:End+1])
                if isinstance(Parsed, dict) and ("Nodes" in Parsed or "Title" in Parsed):
                    Spec = Parsed

        if Spec is not None:
            Station = LCARSDynamicStation(Spec, self.ActivePalette, Parent=Parent)
            self.ActiveStations[Spec.get("Title", "dynamic")] = Station
            return Station

        TargetKey = str(Target if isinstance(Target, str) else (Target.get("Type") or Target.get("Title") or "nova")).strip().lower()

        # 0. Канонічна станція симулятора частинок Geant4
        if any(k in TargetKey for k in ("geant", "geant4", "physics", "particle", "sim")):
            GeantMod = LCARS.Import("lcars.ui.screen.geant4")
            if GeantMod and hasattr(GeantMod, "LCARSGeant4Station"):
                Station = GeantMod.LCARSGeant4Station(Parent=Parent)
                self.ActiveStations["geant4"] = Station
                return Station

        # 1. Канонічна станція розробки Nova IDE (готова база системи)
        if TargetKey in ("nova", "novaide", "workbench", "ide"):
            NovaMod = LCARS.Import("programs.Nova.ide")
            if NovaMod and hasattr(NovaMod, "NovaPanel"):
                Station = NovaMod.NovaPanel(Parent=Parent)
                self.ActiveStations["nova"] = Station
                if hasattr(Station, "setWindowTitle"):
                    Station.setWindowTitle("NOVA WORKBENCH // IDE")
                return Station

        # 2. Канонічний робочий стіл містка (LCARSDesktop)
        if TargetKey in ("desktop", "bridge"):
            DesktopMod = LCARS.Import("lcars.ui.screen.desktop")
            if DesktopMod and hasattr(DesktopMod, "LCARSDesktop"):
                ComputerMod = LCARS.Import("lcars.core.computer")
                Board = ComputerMod.BoardComputer.GetInstance() if ComputerMod else None
                Station = DesktopMod.LCARSDesktop(BoardComputer=Board)
                self.ActiveStations["desktop"] = Station
                return Station

        # 3. Канонічний термінал PADD
        if TargetKey in ("terminal", "console", "padd"):
            TermMod = LCARS.Import("lcars.ui.terminal")
            if TermMod and hasattr(TermMod, "LCARSTerminal"):
                ComputerMod = LCARS.Import("lcars.core.computer")
                Board = ComputerMod.BoardComputer.GetInstance() if ComputerMod else None
                Station = TermMod.LCARSTerminal(BoardComputer=Board, portable=True)
                self.ActiveStations["terminal"] = Station
                return Station

        # 4. Динамічна матеріалізація схеми, згенерованої штучним інтелектом
        FallbackSpec = {"Title": str(Target).upper(), "Nodes": []}
        Station = LCARSDynamicStation(FallbackSpec, self.ActivePalette, Parent=Parent)
        self.ActiveStations[TargetKey] = Station
        return Station

__all__ = ["LCARSReplicator", "LCARSDynamicStation", "ThemePaletteQuery", "ComponentRegistryQuery"]
