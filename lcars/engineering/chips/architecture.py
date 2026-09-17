# ◤ LCARS ENGINEERING :: ISOLINEAR CHIP & STRATUM ARCHITECTURE 🖖
# =============================================================================
# ФАЙЛ: lcars/engineering/chips/architecture.py
# ОПИС: Головна суверенна архітектура ізолінійних чіпів (00..10) та інженерного шару.
#       Керує 11 категоріями оптичних чіпів зорельота, шинами ODN (ODN-00..ODN-10),
#       монтуванням у слоти, оперативним каталогом чіпів та виконанням entrypoints.
# СТАНДАРТ: Titanium LCARS (Zero-Direct-Imports, Zero-Except, Zero-Underscores, Strict PascalCase, Pure Classes).
# =============================================================================
from lcars.base.type import SystemComponent, LCARS
from lcars.base.info import VersionInfo
from lcars.base.interface import 
from lcars.core.signal import ODN

# Категорія ізолінійного чіпа
class ChipCategory(LCARS):
    def __init__(self, Code: str, Name: str, Bus: str, SecurityLevel: int, TargetPath: str, Description: str):
        super().__init__()
        self.Code = Code
        self.Name = Name
        self.Bus = Bus
        self.SecurityLevel = SecurityLevel
        self.TargetPath = TargetPath
        self.Description = Description

# Оптичний слот стійки ODN
class ChipSlot(SystemComponent):
    def __init__(self, CategoryCode: str, SlotNumber: int):
        super().__init__()
        self.CategoryCode = CategoryCode
        self.SlotNumber = SlotNumber
        self.MountedChipId = None
        self.IsOccupied = False
        self.Status = "EMPTY"

    def Mount(self, ChipId: str) -> None:
        self.MountedChipId = ChipId
        self.IsOccupied = True
        self.Status = "ONLINE"

    def Unmount(self) -> None:
        self.MountedChipId = None
        self.IsOccupied = False
        self.Status = "EMPTY"

# Головна ІСО-архітектура оптичних чіпів зорельота
class ISOArchitecture(SystemComponent):
    Instance = None

    Categories = {
        "00": ChipCategory("00", "System Kernel", "ODN-00", 10, "lcars/core/", "Ядро системи, бутстрап та системний контроль"),
        "01": ChipCategory("01", "Base Framework", "ODN-01", 9, "lcars/base/", "Базові типи, протоколи та геометрія LCARS"),
        "02": ChipCategory("02", "Engineering", "ODN-02", 7, "lcars/engineering/", "Фізичні підсистеми інженерного відсіку"),
        "03": ChipCategory("03", "Data Management", "ODN-03", 6, "lcars/modules/", "Бази даних та керування оперативною пам'яттю"),
        "04": ChipCategory("04", "AI ML Systems", "ODN-04", 8, "lcars/modules/", "Синтетичний інтелект та лінгвістичні матриці"),
        "05": ChipCategory("05", "Security Clearance", "ODN-05", 9, "lcars/system/", "Протоколи безпеки, блокування та рівні допуску"),
        "06": ChipCategory("06", "Communication", "ODN-06", 5, "lcars/service/", "Підпросторовий зв'язок та комунікаційні протоколи"),
        "07": ChipCategory("07", "Interface UI", "ODN-07", 4, "lcars/ui/", "Графічні консолі, PADD-панелі та InterfaceEditor"),
        "08": ChipCategory("08", "Storage Systems", "ODN-08", 5, "lcars/data/", "Файлові адаптери та носії сховищ"),
        "09": ChipCategory("09", "Simulation", "ODN-09", 6, "lcars/engineering/laboratory.py", "Фізичні симуляції часток та Geant4"),
        "10": ChipCategory("10", "Sensor Telemetry", "ODN-10", 6, "lcars/engineering/telemetry.py", "Сенсорна та телеметрична сітка корабля"),
    }

    def __init__(self):
        super().__init__()
        self.Catalog = {}
        self.Slots = {}
        self.ActiveBuses = {}
        self.InitializeSlots()
        self.ScanCategories()

    @classmethod
    def GetInstance(cls) -> ISOArchitecture:
        if cls.Instance is None:
            cls.Instance = ISOArchitecture()
        return cls.Instance

    def InitializeSlots(self) -> None:
        for CatCode in self.Categories:
            self.Slots[CatCode] = [ChipSlot(CatCode, SlotIndex) for SlotIndex in range(100)]
            self.ActiveBuses[CatCode] = self.Categories[CatCode].Bus

    def ScanCategories(self) -> dict:
        Yaml = LCARS.Storage.Yaml
        NewCatalog = {}
        for CatCode in self.Categories:
            NewCatalog[CatCode] = {}
            CatDir = LCARS.System.Path(f"lcars/engineering/chips/{CatCode}")
            if not CatDir.exists():
                continue
            for ManifestPath in CatDir.glob("*.yaml"):
                Text = ManifestPath.read_text(encoding="utf-8", errors="replace")
                Parsed = Yaml.safe_load(Text) if Yaml and hasattr(Yaml, "safe_load") else {}
                Meta = Parsed.get("Metadata") or Parsed.get("metadata") or {}
                ChipId = Meta.get("Id") or Meta.get("id") or Parsed.get("Id") or Parsed.get("id") or ManifestPath.stem
                ChipName = Meta.get("Name") or Meta.get("name", "Unknown Chip")
                Entrypoints = Parsed.get("Entrypoints") or Parsed.get("entrypoints") or {}
                Entry = Entrypoints.get("Main") or Entrypoints.get("main", "None")
                Paths = Parsed.get("Paths") or Parsed.get("paths") or {}
                Specs = Parsed.get("Specs") or Parsed.get("specs") or {}
                Database = Paths.get("DatabaseFile") or Paths.get("database_file", "")
                NewCatalog[CatCode][ChipId] = {
                    "Id": ChipId,
                    "Name": ChipName,
                    "Category": CatCode,
                    "FilePath": str(ManifestPath).replace("\\", "/"),
                    "Entrypoint": Entry,
                    "Status": "ONLINE",
                    "Specs": Specs,
                    "Paths": Paths,
                    "Database": Database,
                }
        self.Catalog = NewCatalog
        return self.Catalog

    def GetCategoryChips(self, CategoryCode: str) -> list[dict]:
        CatData = self.Catalog.get(CategoryCode, {})
        return list(CatData.values())

    def ResolveChip(self, ChipId: str) -> dict | None:
        for CatCode, Chips in self.Catalog.items():
            if ChipId in Chips:
                return Chips[ChipId]
        return None

    def MountChip(self, ChipId: str, SlotNumber: int | None = None) -> bool:
        Resolved = self.ResolveChip(ChipId)
        if not Resolved:
            return False
        CatCode = Resolved["Category"]
        CatSlots = self.Slots.get(CatCode, [])
        BusName = Resolved['Specs'].get('Bus') or Resolved['Specs'].get('bus', 'ODN-00')
        if SlotNumber is not None and 0 <= SlotNumber < len(CatSlots):
            TargetSlot = CatSlots[SlotNumber]
            TargetSlot.Mount(ChipId)
            ODN.Transmit(f"ODN.{BusName}.Mounted", ChipId=ChipId)
            return True
        for Slot in CatSlots:
            if not Slot.IsOccupied:
                Slot.Mount(ChipId)
                ODN.Transmit(f"ODN.{BusName}.Mounted", ChipId=ChipId)
                return True
        return False

    def UnmountChip(self, ChipId: str) -> bool:
        for CatCode, CatSlots in self.Slots.items():
            for Slot in CatSlots:
                if Slot.MountedChipId == ChipId:
                    Slot.Unmount()
                    ODN.Transmit("ODN.Chip.Unmounted", ChipId=ChipId)
                    return True
        return False

    def ExecuteEntrypoint(self, ChipId: str) -> any:
        Resolved = self.ResolveChip(ChipId)
        if not Resolved:
            return None
        Entry = Resolved.get("Entrypoint")
        ModulePath, AttrName = Entry.split(":")
        from lcars.service.bridge import Bridge
        ImportFunc = Bridge().Load("System.Module.Import")
        LoadedModule = ImportFunc(ModulePath)
        TargetClassOrFunc = getattr(LoadedModule, AttrName, None)
        return TargetClassOrFunc
# =====================================================================
# CHIP INTERFACE BUILDER — Фабрика зчитування й побудови чіпів ODN
# =====================================================================
class ChipInterfaceBuilder:
    @classmethod
    def LocateChip(cls, ChipId: str) -> Optional[Path]:
        CleanId = str(ChipId).strip().replace(".yaml", "").replace(".yml", "")
        BaseDir = Path(__file__).resolve().parents[2]
        Cat = CleanId.split("-")[0] if "-" in CleanId else "05"
        Candidates = [
            BaseDir / "lcars" / "engineering" / "chips" / Cat / f"{CleanId}.yaml",
            BaseDir / "lcars" / "engineering" / "chips" / Cat / f"{CleanId[:7]}.yaml",
            BaseDir / "lcars" / "engineering" / "chips" / Cat / "05-0000.yaml",
        ]
        for Candidate in Candidates:
            if Candidate.exists():
                return Candidate
        return None

    @classmethod
    def LoadChipData(cls, ChipId: str) -> dict:
        ChipFile = cls.LocateChip(ChipId)
        if not ChipFile:
            return {}
        with open(ChipFile, "r", encoding="utf-8") as FileStream:
            Manifest = yaml.safe_load(FileStream) or {}

        DbConfig = Manifest.get("config", {}).get("database", {})
        DbRelPath = DbConfig.get("path", "")
        if DbRelPath:
            BaseDir = Path(__file__).resolve().parents[2]
            DbPath = BaseDir / DbRelPath
            if DbPath.exists():
                Conn = sqlite3.connect(str(DbPath))
                Cursor = Conn.cursor()
                Table = DbConfig.get("table", "ui_chip_images")
                ScreenName = DbConfig.get("screen", "master_catalog")
                Cursor.execute(
                    f"SELECT elements_json FROM {Table} WHERE chip_id=? OR screen_name=? LIMIT 1",
                    (str(ChipId), str(ScreenName))
                )
                Row = Cursor.fetchone()
                Conn.close()
                if Row and Row[0]:
                    Payload = json.loads(Row[0])
                    if "layout" not in Payload and "sections" in Payload:
                        return {"layout": Payload}
                    return Payload

        LayoutPayload = Manifest.get("layout", {})
        if LayoutPayload:
            return {"layout": LayoutPayload}
        return {}

    @classmethod
    def Build(cls, ChipId: str, ParentHost: Any = None, MasterPadd: Any = None):
        Data = cls.LoadChipData(ChipId)
        if not Data:
            return None
        LayoutConfig = Data.get("layout", {})
        RootPanel = Panel(Parent=ParentHost)
        RootLayout = RootPanel.Vertical(16, 14, 16, 14, 18)
        StatusLabelRef = [None]

        def HandleModeAction(ActionType):
            from lcars.system.alert import GetAlertSystem, AlertLevel
            import lcars.base.default as DefaultMod
            AlertSys = GetAlertSystem()
            if ActionType == "normal":
                DefaultMod.SystemState = "normal"
                if AlertSys:
                    AlertSys.SetLevel(AlertLevel.GREEN)
                if StatusLabelRef[0]:
                    StatusLabelRef[0].SetText("SYSTEM MODE: NORMAL // STANDARD STARFLEET OPERATIONAL PALETTE")
            elif ActionType == "yellow":
                DefaultMod.SystemState = "yellow"
                if AlertSys:
                    AlertSys.SetLevel(AlertLevel.YELLOW)
                if StatusLabelRef[0]:
                    StatusLabelRef[0].SetText("SYSTEM MODE: CONDITION YELLOW // ACTIVE SENSOR CAUTION")
            elif ActionType == "red":
                DefaultMod.SystemState = "red"
                if AlertSys:
                    AlertSys.SetLevel(AlertLevel.RED)
                if StatusLabelRef[0]:
                    StatusLabelRef[0].SetText("SYSTEM MODE: CONDITION RED // ALL STATIONS TO TACTICAL ALERT")
            elif ActionType == "auth":
                if StatusLabelRef[0]:
                    StatusLabelRef[0].SetText("AUTHORIZATION ACCEPTED // SECURITY CLEARANCE LEVEL 4")
                    StatusLabelRef[0].Update()
            elif ActionType == "standby":
                DefaultMod.SystemState = "disabled"
                if StatusLabelRef[0]:
                    StatusLabelRef[0].SetText("SYSTEM MODE: STANDBY // POWER CONSERVE PROTOCOL")
            if MasterPadd and hasattr(MasterPadd, "Widget") and MasterPadd.Widget:
                MasterPadd.Widget.update()

        Sections = LayoutConfig.get("sections", [])
        for SecData in Sections:
            SecPanel = Panel(Parent=RootPanel.Widget)
            SecVL = SecPanel.Vertical(0, 0, 0, 0, SecData.get("spacing", 8))

            if "header" in SecData:
                HdrData = SecData["header"]
                HdrLbl = LCARSLabel(
                    Text=HdrData.get("text", ""),
                    FontSize=HdrData.get("font_size", 18),
                    Parent=SecPanel.Widget,
                )
                SecPanel.Add(SecVL, HdrLbl)

            if "status_label" in SecData:
                StData = SecData["status_label"]
                StRow = Segment(Parent=SecPanel.Widget)
                StRL = StRow.Horizontal(0, 0, 0, 0, 6)
                StLbl = LCARSLabel(
                    Text=StData.get("text", ""),
                    FontSize=StData.get("font_size", 18),
                    Parent=StRow.Widget,
                )
                StatusLabelRef[0] = StLbl
                StRow.Add(StRL, StLbl)
                SecPanel.Add(SecVL, StRow)

            for RowData in SecData.get("rows", []):
                RowType = RowData.get("type", "segment")
                if RowType == "compound_stacks":
                    RowMain = Segment(Parent=SecPanel.Widget)
                    RML = RowMain.Horizontal(0, 0, 0, 0, 12)

                    LeftStack = Segment(Parent=RowMain.Widget)
                    LSL = LeftStack.Vertical(0, 0, 0, 0, 4)
                    for NumVal, NameVal, ChipCode in RowData.get("left_rows", []):
                        RowItem = Segment(Parent=LeftStack.Widget)
                        RL = RowItem.Horizontal(0, 0, 0, 0, 4)
                        Cap = LCARSIndicator(
                            IndicatorType=LCARSIndicator.PillHalf,
                            Direction=180,
                            Width=28,
                            Height=28,
                            Parent=RowItem.Widget
                        )
                        Bar = LCARSBar(Width=6, Height=28, Parent=RowItem.Widget)
                        NumLbl = LCARSLabel(Text=NumVal, FontSize=20, Width=48, Parent=RowItem.Widget)
                        Btn = LCARSButton(
                            Text=NameVal,
                            Number=ChipCode,
                            Form=LCARSButton.SoftHalf,
                            Direction=0,
                            Height=28,
                            Width=180,
                            FontSize=16,
                            Parent=RowItem.Widget
                        )
                        RowItem.Add(RL, Cap)
                        RowItem.Add(RL, Bar)
                        RowItem.Add(RL, NumLbl)
                        RowItem.Add(RL, Btn)
                        LeftStack.Add(LSL, RowItem)
                    RowMain.Add(RML, LeftStack)

                    RightStack = Segment(Parent=RowMain.Widget)
                    RSL = RightStack.Vertical(0, 0, 0, 0, 4)
                    for Subsys, BadgeVal, TelemetryVal, ChipCode in RowData.get("right_rows", []):
                        RowItem = Segment(Parent=RightStack.Widget)
                        RL = RowItem.Horizontal(0, 0, 0, 0, 4)
                        LBtn = LCARSButton(
                            Text=Subsys,
                            Number=ChipCode,
                            Form=LCARSButton.SoftHalf,
                            Direction=180,
                            Height=28,
                            Width=160,
                            FontSize=16,
                            Parent=RowItem.Widget
                        )
                        BadgeLbl = LCARSLabel(Text=BadgeVal, FontSize=20, Width=36, Parent=RowItem.Widget)
                        DataLbl = LCARSLabel(Text=TelemetryVal, FontSize=18, Width=140, Parent=RowItem.Widget)
                        CapR = LCARSIndicator(
                            IndicatorType=LCARSIndicator.PillHalf,
                            Direction=0,
                            Width=24,
                            Height=28,
                            Parent=RowItem.Widget
                        )
                        RowItem.Add(RL, LBtn)
                        RowItem.Add(RL, BadgeLbl)
                        RowItem.Add(RL, DataLbl)
                        RowItem.Add(RL, CapR)
                        RightStack.Add(RSL, RowItem)
                    RowMain.Add(RML, RightStack, 1)
                    SecPanel.Add(SecVL, RowMain)

                elif RowType == "bars_stack":
                    BarRow = Segment(Parent=SecPanel.Widget)
                    BRL = BarRow.Vertical(0, 0, 0, 0, 4)
                    for HVal in RowData.get("heights", [4, 8, 14, 22]):
                        Bar = LCARSBar(Height=HVal, Parent=BarRow.Widget)
                        BarRow.Add(BRL, Bar)
                    SecPanel.Add(SecVL, BarRow)

                else:
                    RowSeg = Segment(Parent=SecPanel.Widget)
                    RL = RowSeg.Horizontal(0, 0, 0, 0, RowData.get("spacing", 6))
                    for Item in RowData.get("items", []):
                        IType = Item.get("type", "button")
                        Flex = Item.get("flex", 0)
                        if IType == "button":
                            ActionKey = Item.get("action", "")
                            Btn = LCARSButton(
                                Text=Item.get("text", ""),
                                Number=Item.get("number", ""),
                                Form=Item.get("form", LCARSButton.Pill),
                                Height=Item.get("height", 38),
                                Width=Item.get("width", 0),
                                FontSize=Item.get("font_size", 16),
                                Parent=RowSeg.Widget,
                            )
                            if ActionKey:
                                def MakeHandler(Act):
                                    return lambda *a: HandleModeAction(Act)
                                Btn.Clicked.Connect(MakeHandler(ActionKey))
                            RowSeg.Add(RL, Btn, Flex)
                        elif IType == "elbow":
                            Elb = LCARSElbow(
                                Direction=Item.get("direction", "top-left"),
                                Text=Item.get("text", ""),
                                Number=Item.get("number", ""),
                                Width=Item.get("width", 480),
                                Height=Item.get("height", 80),
                                Thickness=Item.get("thickness", 24),
                                Radius=Item.get("radius", 36),
                                FontSize=Item.get("font_size", 18),
                                Parent=RowSeg.Widget,
                            )
                            RowSeg.Add(RL, Elb, Flex)
                        elif IType == "indicator":
                            IndMap = {
                                "pill": LCARSIndicator.Pill,
                                "pill_half": LCARSIndicator.PillHalf,
                                "bar": LCARSIndicator.Rect,
                                "rect": LCARSIndicator.Rect,
                            }
                            IndTypeEnum = IndMap.get(Item.get("indicator_type", "pill_half"), LCARSIndicator.PillHalf)
                            Ind = LCARSIndicator(
                                Text=Item.get("text", ""),
                                IndicatorType=IndTypeEnum,
                                Direction=Item.get("direction", 0),
                                Height=Item.get("height", 34),
                                Width=Item.get("width", 140),
                                FontSize=Item.get("font_size", 16),
                                Parent=RowSeg.Widget,
                            )
                            RowSeg.Add(RL, Ind, Flex)
                        elif IType == "datablock":
                            DB = DataBlock(
                                Item.get("title", ""),
                                Item.get("data", {}),
                                RowSeg.Widget,
                            )
                            RowSeg.Add(RL, DB, Flex)
                    SecPanel.Add(SecVL, RowSeg)

            RootPanel.Add(RootLayout, SecPanel)
        return RootPanel

# Канонічні точки доступу до ІСО-архітектури чіпів
ISOArchitectureCore = ISOArchitecture.GetInstance
ISO = ISOArchitecture.GetInstance()
IsolinearChipArchitecture = ISOArchitecture
ChipArchitecture = ISOArchitecture.GetInstance
ARCHITECTURE = ISOArchitecture.GetInstance()
