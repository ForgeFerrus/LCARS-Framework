import sys
import threading
import time
from pathlib import Path
from typing import Any, Dict, Optional, cast

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lcars.base.component import Graphic, LCARSLabel, LCARSButton, DataBlock
SystemComponent = Graphic

from lcars.base.default import (
    DefaultBackground,
    Palette,
    RandomButtonColor,
)
from lcars.base.type import Directive, Primitives, LCARSTypes, LCARS
from lcars.base.interface import LCARSPadd
from lcars.tools.chronometer import ChronometerSubsystem
import datetime


def W(Obj):
    WidgetAttr = getattr(Obj, "widget", None)
    if callable(WidgetAttr):
        return WidgetAttr()
    if WidgetAttr is not None:  
        return WidgetAttr
    return Obj

# ─── Layout Helpers ──────────────────────────────────────────────────────────
def CreateLayout(Name, Parent=None):
    Layout = None
    if Name in ["HBoxLayout", "HBox"]:
        Layout = LCARS.Horizontal
    elif Name in ["VBoxLayout", "VBox"]:
        Layout = LCARS.Vertical
    elif Name == "Grid":
        Layout = LCARS.Grid
    if Layout is None:
        raise ValueError(f"Unknown layout type: {Name}")
    return Layout(W(Parent))
    
# Direction substitutes
class LayoutDirection:
    LeftToRight = Directive.Protocol.LayoutDirection.LeftToRight if hasattr(Directive.Protocol, "LayoutDirection") else 0
    TopToBottom = Directive.Protocol.LayoutDirection.TopToBottom if hasattr(Directive.Protocol, "LayoutDirection") and hasattr(Directive.Protocol.LayoutDirection, "TopToBottom") else 1

PANEL_BACKGROUND = DefaultBackground
PANEL_EDGE       = Palette.Panels[1] 
PANEL_EDGE_SOFT  = Palette.Panels[0] 
PANEL_ACCENT     = Palette.Accent[1] 
TEXT_PRIMARY     = Palette.Panels[2] 
TEXT_SECONDARY   = Palette.Panels[1] 
BUTTON_PRIMARY   = Palette.Buttons[0] 
BUTTON_ACTIVE    = Palette.Buttons[1] 
BUTTON_ACCENT    = Palette.Accent[1] 
BUTTON_SUCCESS   = Palette.Accent[2] 
BUTTON_WARNING   = Palette.YellowAlert[0] 
BUTTON_ALERT     = Palette.RedAlert[0] 

BUTTON_GROUPS = {
    "primary": "Buttons",
    "accent": "Accent",
    "success": "Accent",
    "warning": "YellowAlert",
    "alert": "RedAlert",
}

# Protocols
SCROLLBAR_OFF = Directive.Protocol.ScrollBarPolicy.ScrollBarAlwaysOff
if isinstance(SCROLLBAR_OFF, int):
    pass

HIDDEN_SCROLL_STYLE = (
    f"background: {PANEL_BACKGROUND}; border: none;"
    "QScrollBar:vertical { width: 0px; background: transparent; }"
    "QScrollBar:horizontal { height: 0px; background: transparent; }"
)

class WeatherEngine:
    def __init__(self):
        self.Latitude = 37.7749
        self.Longitude = -122.4194
        self.LocationName = "SAN FRANCISCO, EARTH"
        self.IsReady = False
        self.LastWeather = {}
        self.LastForecast = {}
        self.Unit = "metric"
        self.CacheTTL = 600
        self.LastFetch = 0
        self.OnWeather = []
        self.OnForecast = []
        self.OnLocation = []
        self.DiscoveryThread = None

    def Start(self):
        import threading
        if self.DiscoveryThread is None or not self.DiscoveryThread.is_alive():
            self.DiscoveryThread = threading.Thread(target=self.DiscoverLocation, daemon=True)
            self.DiscoveryThread.start()

    def ConnectWeather(self, Callback):
        if Callback not in self.OnWeather:
            self.OnWeather.append(Callback)

    def ConnectForecast(self, Callback):
        if Callback not in self.OnForecast:
            self.OnForecast.append(Callback)

    def ConnectLocation(self, Callback):
        if Callback not in self.OnLocation:
            self.OnLocation.append(Callback)

    def EmitWeather(self, Data):
        for Callback in self.OnWeather:
            Callback(Data)

    def EmitForecast(self, Data):
        for Callback in self.OnForecast:
            Callback(Data)

    def EmitLocation(self, Location):
        for Callback in self.OnLocation:
            Callback(Location)

    def HttpGetJson(self, Url: str) -> Optional[dict]:
        from urllib.request import Request, urlopen
        import json
        RequestObj = Request(Url, headers={"User-Agent": "LCARS Weather Matrix/1.0"})
        with urlopen(RequestObj, timeout=10) as Response:
            Code = getattr(Response, "status", None) or Response.getcode()
            if Code != 200:
                return None
            Payload = Response.read()
            return json.loads(Payload.decode("utf-8"))

    def DiscoverLocation(self):
        Data = self.HttpGetJson("http://ip-api.com/json/")
        if Data and Data.get("status") == "success":
            self.Latitude = Data.get("lat", self.Latitude)
            self.Longitude = Data.get("lon", self.Longitude)
            City = Data.get("city", "UNKNOWN").upper()
            Country = Data.get("country", "EARTH").upper()
            self.LocationName = f"{City}, {Country}"
        self.IsReady = True
        self.EmitLocation(self.LocationName)
        self.RefreshWeather()
        self.RefreshForecast()

    def RefreshWeather(self):
        if not self.IsReady: return
        import threading
        threading.Thread(target=self.FetchCurrentWeather, daemon=True).start()
        threading.Thread(target=self.FetchHourly, daemon=True).start()

    def RefreshForecast(self):
        if not self.IsReady: return
        import threading
        threading.Thread(target=self.FetchForecast, daemon=True).start()

    def SearchLocation(self, Query: str):
        if not Query: return
        import threading
        threading.Thread(target=self.ResolveLocation, args=(Query,), daemon=True).start()

    def ResolveLocation(self, Query: str):
        from urllib.parse import quote
        EncodedQuery = quote(Query)
        Url = f"https://geocoding-api.open-meteo.com/v1/search?name={EncodedQuery}&count=1"
        Data = self.HttpGetJson(Url)
        if Data:
            Results = Data.get("results", [])
            if Results:
                Top = Results[0]
                self.Latitude = Top.get("latitude", self.Latitude)
                self.Longitude = Top.get("longitude", self.Longitude)
                Name = Top.get("name", Query).upper()
                Country = Top.get("country", "UNKNOWN").upper()
                self.LocationName = f"{Name}, {Country}"
                self.EmitLocation(self.LocationName)
                self.RefreshWeather()
                self.RefreshForecast()
                return
        self.EmitLocation("LOCATION NOT FOUND")

    def FetchCurrentWeather(self):
        import time
        if time.time() - self.LastFetch < self.CacheTTL and self.LastWeather:
            self.EmitWeather(self.LastWeather)
            return
        Url = (
            f"https://api.open-meteo.com/v1/forecast?latitude={self.Latitude}&longitude={self.Longitude}"
            f"&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m,wind_direction_10m"
            f"&hourly=relative_humidity_2m,pressure_msl,dew_point_2m,visibility,uv_index,cloud_cover"
            f"&timezone=auto&temperature_unit={self.GetTempUnit()}&wind_speed_unit={self.GetWindUnit()}"
        )
        Payload = self.HttpGetJson(Url)
        if Payload:
            Current = Payload.get("current", {})
            Hourly = Payload.get("hourly", {})
            Idx = 0
            if "time" in Hourly and len(Hourly["time"]) > 0:
                import datetime
                NowIso = datetime.datetime.now().isoformat()[:13]
                for i, T in enumerate(Hourly["time"]):
                    if NowIso in T: Idx = i; break
            
            Icon, Cond = self.TranslateCode(Current.get("weather_code", 0))
            Weather = {
                "Status": "success",
                "Temp": Current.get("temperature_2m", 0.0),
                "WindSpeed": Current.get("wind_speed_10m", 0.0),
                "WindDirection": Current.get("wind_direction_10m", 0),
                "Condition": Cond,
                "Icon": Icon,
                "Humidity": Current.get("relative_humidity_2m", None),
                "Pressure": Hourly.get("pressure_msl", [None])[Idx] if Hourly else None,
                "DewPoint": Hourly.get("dew_point_2m", [None])[Idx] if Hourly else None,
                "Visibility": Hourly.get("visibility", [None])[Idx] if Hourly else None,
                "UVIndex": Hourly.get("uv_index", [None])[Idx] if Hourly else None,
                "CloudCover": Hourly.get("cloud_cover", [None])[Idx] if Hourly else None,
                "Location": self.LocationName,
                "IsAdverse": self.IsAdverseCondition(Current.get("weather_code", 0))
            }
            self.LastWeather = Weather
            self.LastFetch = time.time()
            self.EmitWeather(Weather)
            return
        self.EmitWeather({"Status": "error", "Message": "NETWORK FAILURE"})

    def FetchHourly(self):
        Url = (
            f"https://api.open-meteo.com/v1/forecast?latitude={self.Latitude}&longitude={self.Longitude}"
            f"&hourly=temperature_2m,weather_code&timezone=auto&forecast_hours=24"
            f"&temperature_unit={self.GetTempUnit()}"
        )
        Payload = self.HttpGetJson(Url)
        if Payload:
            Hourly = Payload.get("hourly", {})
            Times = Hourly.get("time", [])
            Temps = Hourly.get("temperature_2m", [])
            Codes = Hourly.get("weather_code", [])
            Data = []
            for i in range(min(24, len(Times))):
                Icon, _ = self.TranslateCode(Codes[i] if i < len(Codes) else 0)
                Data.append({
                    "Time": f"+{i}H" if i > 0 else "NOW",
                    "Temp": Temps[i] if i < len(Temps) else 0,
                    "Icon": Icon,
                })
            if self.LastWeather:
                self.LastWeather["Hourly"] = Data
                self.EmitWeather(self.LastWeather)

    def IsAdverseCondition(self, Code: int) -> bool:
        return Code in [65, 75, 82, 86, 95, 96, 99]

    def FetchForecast(self):
        Url = (
            f"https://api.open-meteo.com/v1/forecast?latitude={self.Latitude}&longitude={self.Longitude}"
            f"&daily=temperature_2m_max,temperature_2m_min,weather_code&timezone=auto&temperature_unit={self.GetTempUnit()}"
        )
        Payload = self.HttpGetJson(Url)
        if Payload:
            Daily = Payload.get("daily", {})
            Dates = Daily.get("time", [])
            MaxT = Daily.get("temperature_2m_max", [])
            MinT = Daily.get("temperature_2m_min", [])
            Codes = Daily.get("weather_code", [])
            Forecast = {"Status": "success", "Daily": []}
            for i in range(min(5, len(Dates))):
                Icon, Cond = self.TranslateCode(Codes[i] if i < len(Codes) else 0)
                Forecast["Daily"].append({
                    "Date": Dates[i],
                    "TempMax": MaxT[i] if i < len(MaxT) else 0,
                    "TempMin": MinT[i] if i < len(MinT) else 0,
                    "Condition": Cond,
                    "Icon": Icon,
                })
            self.LastForecast = Forecast
            self.EmitForecast(Forecast)
            return
        self.EmitForecast({"Status": "error", "Message": "NETWORK FAILURE"})

    def TranslateCode(self, Code: int) -> tuple[str, str]:
        Mapping = {
            0: ("CLEAR", "☀"), 1: ("MAINLY CLEAR", "🌤"), 2: ("PARTLY CLOUDY", "⛅"),
            3: ("OVERCAST", "☁"), 45: ("FOG", "🌫"), 48: ("RIME FOG", "🌫"),
            51: ("LIGHT DRIZZLE", "🌦"), 53: ("DRIZZLE", "🌦"), 55: ("HEAVY DRIZZLE", "🌧"),
            61: ("LIGHT RAIN", "🌧"), 63: ("RAIN", "🌧"), 65: ("HEAVY RAIN", "⛈"),
            71: ("LIGHT SNOW", "🌨"), 73: ("SNOW", "🌨"), 75: ("HEAVY SNOW", "❄"),
            77: ("SNOW GRAINS", "❄"), 80: ("SHOWERS", "🌦"), 81: ("HEAVY SHOWERS", "🌧"),
            82: ("STORM SHOWERS", "⛈"), 85: ("SNOW SHOWERS", "🌨"), 86: ("HEAVY SNOW SHOWERS", "❄"),
            95: ("THUNDERSTORM", "🌩"), 96: ("STORM WITH HAIL", "🌩"), 99: ("HEAVY STORM", "🌩"),
        }
        return Mapping.get(Code, (f"UNKNOWN {Code}", "❔"))

    def GetTempUnit(self) -> str:
        return "fahrenheit" if self.Unit == "imperial" else "celsius"

    def GetWindUnit(self) -> str:
        return "mph" if self.Unit == "imperial" else "kmh"

class WeatherStation(LCARSPadd):
    def __init__(self):
        super().__init__(Title="◤ TITANIUM WEATHER MATRIX", Color=BUTTON_PRIMARY)
        self.setStyleSheet("background: transparent;")
        self.Viewport = self.widget
        self.Viewport.setStyleSheet("background-color: #000000; border: none;")
        self.IsFullscreen = False
        self.ShuttingDown = False
        self.AlertMode = "normal"
        self.DynamicButtons = []
        
        self.CurrentView = "overview"
        self.Locations = ["SAN FRANCISCO", "WASHINGTON DC", "PRAGUE", "LONDON"]
        self.CurrentLocIdx = 0

        self.Engine = WeatherEngine()
        self.Engine.ConnectWeather(self.OnWeatherUpdate)
        self.Engine.ConnectForecast(self.OnForecastUpdate)
        self.Engine.ConnectLocation(self.OnLocationResolved)

        AppInstance = getattr(sys.modules.get("__main__"), "AppInstance", None)
        if AppInstance and hasattr(AppInstance, "aboutToQuit"):
            AppInstance.aboutToQuit.connect(self.PrepareShutdown)

        self.BuildUI()
        self.SyncAlertState()
        self.SetupChronometer()
        self.SetupPaletteCycle()
        self.Engine.Start()
        if hasattr(self.widget, "showFullScreen"):
            self.widget.showFullScreen()

    def BuildUI(self):
        Central = self.Viewport
        MainLayout = Central.layout() if hasattr(Central, "layout") else None
        if MainLayout is None:
            MainLayout = CreateLayout("VBox", Central)
            if hasattr(Central, "setLayout"):
                Central.setLayout(MainLayout)
        
        MainLayout.setContentsMargins(18, 18, 18, 18)
        MainLayout.setSpacing(14)

        Header = SystemComponent(Central)
        Header.setStyleSheet(self.PanelStyle())
        HeaderLayout = CreateLayout("HBox", Header)
        HeaderLayout.setContentsMargins(16, 14, 16, 14)
        HeaderLayout.setSpacing(10)
        Title = LCARSLabel("◤ TITANIUM WEATHER MATRIX", Color=TEXT_PRIMARY, FontSize=24, Parent=Header)
        HeaderLayout.addWidget(W(Title))
        self.ChronoLabel = LCARSLabel("STARDATE: --", Color=TEXT_SECONDARY, FontSize=12, Parent=Header)
        HeaderLayout.addWidget(W(self.ChronoLabel))
        self.StatusLabel = LCARSLabel("SYSTEM STATUS: SYNCHRONIZING", Color=TEXT_SECONDARY, FontSize=12, Parent=Header)
        HeaderLayout.addWidget(W(self.StatusLabel))
        HeaderLayout.addStretch()
        RefreshBtn = LCARSButton("REFRESH", Type=LCARSButton.PILL, Parent=Header)
        self.ApplyButtonState(RefreshBtn, "primary")
        RefreshBtn.clicked.connect(self.ManualRefresh)
        HeaderLayout.addWidget(W(RefreshBtn))
        MainLayout.addWidget(W(Header))

        InfoBar = SystemComponent(Central)
        InfoBar.setStyleSheet(self.PanelStyle(1))
        InfoLayout = CreateLayout("HBox", InfoBar)
        InfoLayout.setContentsMargins(14, 10, 14, 10)
        InfoLayout.setSpacing(10)
        InfoLayout.addWidget(W(LCARSLabel("PORTABLE PADD", Color=BUTTON_ACTIVE, FontSize=12, Parent=InfoBar)))
        InfoLayout.addWidget(W(LCARSLabel("WEATHER COMMAND CENTER", Color=TEXT_PRIMARY, FontSize=12, Parent=InfoBar)))
        self.AlertBtn = LCARSButton("ALERT: OFF", Type=LCARSButton.PILL, Parent=InfoBar)
        self.ApplyButtonState(self.AlertBtn, "warning")
        self.AlertBtn.clicked.connect(self.CycleAlertMode)
        InfoLayout.addWidget(W(self.AlertBtn))
        self.FullscreenBtn = LCARSButton("FULLSCREEN", Type=LCARSButton.PILL, Parent=InfoBar)
        self.ApplyButtonState(self.FullscreenBtn, "accent")
        self.FullscreenBtn.clicked.connect(self.ToggleFullscreen)
        InfoLayout.addWidget(W(self.FullscreenBtn))
        InfoLayout.addStretch()
        ExitBtn = LCARSButton("EXIT", Type=LCARSButton.PILL, Parent=InfoBar)
        self.ApplyButtonState(ExitBtn, "alert")
        ExitBtn.clicked.connect(self.close)
        InfoLayout.addWidget(W(ExitBtn))
        MainLayout.addWidget(W(InfoBar))

        ControlRow = SystemComponent(Central)
        ControlRow.setStyleSheet(self.PanelStyle())
        ControlLayout = CreateLayout("HBox", ControlRow)
        ControlLayout.setContentsMargins(14, 12, 14, 12)
        ControlLayout.setSpacing(12)
        self.SearchInput = cast(Any, LCARS.Input())
        self.SearchInput.setPlaceholderText("SEARCH LOCATION OR CITY")
        self.SearchInput.setStyleSheet(f"background: {PANEL_BACKGROUND}; color: {TEXT_PRIMARY}; border: 1px solid {PANEL_EDGE}; border-radius: 8px; padding: 10px;")
        if hasattr(self.SearchInput, "returnPressed"):
            self.SearchInput.returnPressed.connect(self.SearchLocation)
        ControlLayout.addWidget(W(self.SearchInput), 3)
        SearchBtn = LCARSButton("SEARCH", Type=LCARSButton.PILL, Parent=ControlRow)
        self.ApplyButtonState(SearchBtn, "primary")
        SearchBtn.clicked.connect(self.SearchLocation)
        ControlLayout.addWidget(W(SearchBtn))
        SyncBtn = LCARSButton("SYNC", Type=LCARSButton.PILL, Parent=ControlRow)
        self.ApplyButtonState(SyncBtn, "success")
        SyncBtn.clicked.connect(self.ManualRefresh)
        ControlLayout.addWidget(W(SyncBtn))
        self.UnitBtn = LCARSButton("METRIC", Type=LCARSButton.PILL, Parent=ControlRow)
        self.ApplyButtonState(self.UnitBtn, "warning")
        self.UnitBtn.clicked.connect(self.ToggleUnits)
        ControlLayout.addWidget(W(self.UnitBtn))
        MainLayout.addWidget(W(ControlRow))

        TabsFrame = SystemComponent(self)
        TabsFrame.setStyleSheet(self.PanelStyle())
        TabsLayout = CreateLayout("HBox", TabsFrame)
        TabsLayout.setContentsMargins(12, 8, 12, 8)
        TabsLayout.setSpacing(10)
        for i, Loc in enumerate(self.Locations):
            Btn = LCARSButton(Loc[:12], Type=LCARSButton.PILL, Parent=TabsFrame)
            self.ApplyButtonState(Btn, "accent", i == self.CurrentLocIdx)
            Btn.clicked.connect(lambda _=None, idx=i: self.SwitchLocation(idx))
            TabsLayout.addWidget(W(Btn))
        TabsLayout.addStretch()
        self.SearchInput = cast(Any, LCARS.Input())
        self.SearchInput.setPlaceholderText("LOCATION...")
        self.SearchInput.setStyleSheet(f"background: {PANEL_BACKGROUND}; color: {TEXT_PRIMARY}; border: 1px solid {PANEL_EDGE}; padding: 5px;")
        TabsLayout.addWidget(W(self.SearchInput))
        AddBtn = LCARSButton("+", Type=LCARSButton.PILL, Parent=TabsFrame)
        self.ApplyButtonState(AddBtn, "success")
        AddBtn.clicked.connect(self.AddLocation)
        TabsLayout.addWidget(W(AddBtn))
        MainLayout.addWidget(W(TabsFrame))

        ContentFrame = SystemComponent(self)
        ContentFrame.setStyleSheet(self.PanelStyle())
        ContentLayout = CreateLayout("HBox", ContentFrame)
        ContentLayout.setContentsMargins(18, 18, 18, 18)
        ContentLayout.setSpacing(20)

        self.BuildSidePanel(ContentLayout)

        CenterColumn = SystemComponent(ContentFrame)
        CenterColumn.setStyleSheet("background: transparent;")
        CenterLayout = CreateLayout("VBox", CenterColumn)
        CenterLayout.setContentsMargins(0, 0, 0, 0)
        CenterLayout.setSpacing(14)

        TopSplit = SystemComponent(CenterColumn)
        TopSplit.setStyleSheet("background: transparent;")
        TopSplitLayout = CreateLayout("HBox", TopSplit)
        TopSplitLayout.setContentsMargins(0, 0, 0, 0)
        TopSplitLayout.setSpacing(14)

        LeftColumn = SystemComponent(TopSplit)
        LeftColumn.setStyleSheet("background: transparent;")
        LeftLayout = CreateLayout("VBox", LeftColumn)
        LeftLayout.setContentsMargins(0, 0, 0, 0)
        LeftLayout.setSpacing(14)

        RightColumn = SystemComponent(TopSplit)
        RightColumn.setStyleSheet("background: transparent;")
        RightLayout = CreateLayout("VBox", RightColumn)
        RightLayout.setContentsMargins(0, 0, 0, 0)
        RightLayout.setSpacing(14)

        self.ViewPages = {}
        self.BuildOverviewPage(LeftLayout)
        self.BuildForecastPage(LeftLayout)
        self.BuildHourlyPage(RightLayout)
        self.BuildMetricsPage(RightLayout)
        LeftLayout.addStretch()
        RightLayout.addStretch()
        TopSplitLayout.addWidget(W(LeftColumn), 1)
        TopSplitLayout.addWidget(W(RightColumn), 1)
        CenterLayout.addWidget(W(TopSplit))
        self.BuildMapPage(CenterLayout)
        self.BuildFooter(CenterLayout)
        ContentLayout.addWidget(W(CenterColumn), 1)
        MainLayout.addWidget(W(ContentFrame), 1)
        self.RefreshViewMode()

    def BuildOverviewPage(self, Layout):
        Page = SystemComponent(self)
        Page.setStyleSheet(self.PanelStyle())
        PageLayout = CreateLayout("VBox", Page)
        PageLayout.setContentsMargins(16, 16, 16, 16)
        PageLayout.setSpacing(12)
        self.ViewPages["overview"] = Page
        SectionTitle = LCARSLabel("CURRENT CONDITIONS", FontSize=20, Color=BUTTON_PRIMARY, Parent=Page)
        PageLayout.addWidget(W(SectionTitle))
        self.TempLabel = LCARSLabel("TEMP: --", FontSize=30, Color=BUTTON_WARNING, Parent=Page)
        PageLayout.addWidget(W(self.TempLabel))
        self.CondLabel = LCARSLabel("COND: --", FontSize=18, Color=TEXT_PRIMARY, Parent=Page)
        PageLayout.addWidget(W(self.CondLabel))
        self.MainBlocks = [
            DataBlock("HUMIDITY", "-- %", BUTTON_ACTIVE, Parent=Page),
            DataBlock("WIND", "--", BUTTON_ACCENT, Parent=Page)
        ]
        self.DetailBlocks = [
            DataBlock("PRESSURE", "--", BUTTON_SUCCESS, Parent=Page),
            DataBlock("DEW POINT", "--", BUTTON_WARNING, Parent=Page),
            DataBlock("VISIBILITY", "-- km", BUTTON_ACTIVE, Parent=Page),
        ]
        for B in self.MainBlocks: 
            PageLayout.addWidget(W(B))
            B.setMinimumHeight(60)
        for B in self.DetailBlocks:
            PageLayout.addWidget(W(B))
            B.setMinimumHeight(60)
        Layout.addWidget(W(Page))

    def BuildForecastPage(self, Layout):
        Page = SystemComponent(self)
        Page.setStyleSheet(self.PanelStyle())
        self.ViewPages["forecast"] = Page
        PageLayout = CreateLayout("VBox", Page)
        PageLayout.setContentsMargins(16, 16, 16, 16)
        PageLayout.setSpacing(10)
        PageLayout.addWidget(W(LCARSLabel("5-DAY FORECAST", FontSize=20, Color=BUTTON_PRIMARY, Parent=Page)))
        self.ForecastRows = []
        for i in range(5):
            Row = LCARSLabel("DAY --: --", Parent=Page)
            Row.setMinimumHeight(40)
            self.ForecastRows.append(Row)
            PageLayout.addWidget(W(Row))
        Layout.addWidget(W(Page))

    def BuildHourlyPage(self, Layout):
        Page = SystemComponent(self)
        Page.setStyleSheet(self.PanelStyle())
        self.ViewPages["hourly"] = Page
        PageLayout = CreateLayout("VBox", Page)
        PageLayout.setContentsMargins(16, 16, 16, 16)
        PageLayout.setSpacing(8)
        PageLayout.addWidget(W(LCARSLabel("24-HOUR OUTLOOK", FontSize=20, Color=BUTTON_PRIMARY, Parent=Page)))
        self.HourlyRows = []
        for i in range(12):
            Row = LCARSLabel("+H --: --", Parent=Page)
            Row.setMinimumHeight(30)
            self.HourlyRows.append(Row)
            PageLayout.addWidget(W(Row))
        Layout.addWidget(W(Page))

    def BuildMetricsPage(self, Layout):
        Page = SystemComponent(self)
        Page.setStyleSheet(self.PanelStyle())
        self.ViewPages["metrics"] = Page
        PageLayout = CreateLayout("VBox", Page)
        PageLayout.setContentsMargins(16, 16, 16, 16)
        PageLayout.setSpacing(12)
        PageLayout.addWidget(W(LCARSLabel("DETAILED METRICS", FontSize=20, Color=BUTTON_PRIMARY, Parent=Page)))
        self.MetricBlocks = {
            "uv": DataBlock("UV INDEX", "--", BUTTON_WARNING, Parent=Page),
            "vis": DataBlock("VISIBILITY", "-- km", BUTTON_ACCENT, Parent=Page),
            "cloud": DataBlock("CLOUD COVER", "-- %", BUTTON_ACTIVE, Parent=Page)
        }
        self.ExtendedMetricBlocks = {
            "pressure": DataBlock("PRESSURE", "--", BUTTON_SUCCESS, Parent=Page),
            "dew": DataBlock("DEW POINT", "--", BUTTON_WARNING, Parent=Page),
        }
        for B in self.MetricBlocks.values(): 
            PageLayout.addWidget(W(B))
            B.setMinimumHeight(60)
        for B in self.ExtendedMetricBlocks.values():
            PageLayout.addWidget(W(B))
            B.setMinimumHeight(60)
        Layout.addWidget(W(Page))

    def BuildMapPage(self, Layout):
        Page = SystemComponent(self)
        Page.setStyleSheet(self.PanelStyle())
        self.ViewPages["map"] = Page
        PageLayout = CreateLayout("VBox", Page)
        PageLayout.setContentsMargins(16, 16, 16, 16)
        PageLayout.setSpacing(12)
        PageLayout.addWidget(W(LCARSLabel("TACTICAL MAP", FontSize=20, Color=BUTTON_PRIMARY, Parent=Page)))
        self.MapLabel = LCARSLabel("TACTICAL MAP: ---", FontSize=22, Color=BUTTON_ACTIVE, Parent=Page)
        PageLayout.addWidget(W(self.MapLabel))
        self.MapNote = LCARSLabel("SELECT MAP PANEL TO VIEW THE EXPANDED OVERLAY", FontSize=12, Color=TEXT_SECONDARY, Parent=Page)
        PageLayout.addWidget(W(self.MapNote))
        self.MapRangeBlock = DataBlock("SCAN RANGE", "LOCAL", BUTTON_ACCENT, Parent=Page)
        self.MapOverlayBlock = DataBlock("OVERLAY", "LIVE", BUTTON_WARNING, Parent=Page)
        self.MapLockBlock = DataBlock("TARGET LOCK", "READY", BUTTON_ACTIVE, Parent=Page)
        PageLayout.addWidget(W(self.MapRangeBlock))
        PageLayout.addWidget(W(self.MapOverlayBlock))
        PageLayout.addWidget(W(self.MapLockBlock))
        MapCanvas = SystemComponent(Page)
        MapCanvas.setStyleSheet(f"background-color: {PANEL_BACKGROUND}; border: 1px solid {PANEL_EDGE}; border-radius: 14px;")
        MapCanvasLayout = CreateLayout("VBox", MapCanvas)
        MapCanvasLayout.setContentsMargins(18, 18, 18, 18)
        MapCanvasLayout.setSpacing(12)
        MapCanvasLayout.addWidget(W(LCARSLabel("ROUTE / RADAR / PRECIPITATION LAYER", Color=TEXT_PRIMARY, FontSize=14, Parent=MapCanvas)))
        MapCanvasLayout.addWidget(W(LCARSLabel("THIS PANEL IS OPEN SEPARATELY SO THE MAP DOES NOT CRUSH THE FORECAST AND TELEMETRY.", Color=TEXT_SECONDARY, FontSize=11, Parent=MapCanvas)))
        PageLayout.addWidget(W(MapCanvas), 1)
        Layout.addWidget(W(Page))

    def BuildFooter(self, Layout):
        Footer = SystemComponent(self)
        Footer.setStyleSheet(self.PanelStyle())
        FooterLayout = CreateLayout("HBox", Footer)
        FooterLayout.setContentsMargins(16, 12, 16, 12)
        FooterLayout.setSpacing(10)
        self.FooterLabel = LCARSLabel("LIVE MATRIX: WEATHER STREAM ACTIVE", Color=TEXT_SECONDARY, FontSize=12, Parent=Footer)
        FooterLayout.addWidget(W(self.FooterLabel))
        FooterLayout.addStretch()
        self.ToggleUnitsBtn = LCARSButton("SWITCH UNITS", Type=LCARSButton.PILL, Parent=Footer)
        self.ApplyButtonState(self.ToggleUnitsBtn, "warning")
        self.ToggleUnitsBtn.clicked.connect(self.ToggleUnits)
        FooterLayout.addWidget(W(self.ToggleUnitsBtn))
        Layout.addWidget(W(Footer))

    def BuildSidePanel(self, ParentLayout):
        SidePanel = SystemComponent(self)
        SidePanel.setStyleSheet(self.PanelStyle())
        self.SidePanel = SidePanel
        SideLayout = CreateLayout("VBox", SidePanel)
        SideLayout.setContentsMargins(18, 18, 18, 18)
        SideLayout.setSpacing(12)
        SideLayout.addWidget(W(LCARSLabel("SYSTEM OPS", Color=BUTTON_ACTIVE, FontSize=12, Parent=SidePanel)))
        SideLayout.addWidget(W(LCARSLabel("QUICK ACCESS MODULE", Color=TEXT_PRIMARY, FontSize=11, Parent=SidePanel)))
        QuickRow = SystemComponent(SidePanel)
        QuickRow.setStyleSheet("background: transparent;")
        QuickLayout = CreateLayout("VBox", QuickRow)
        QuickLayout.setContentsMargins(0, 0, 0, 0)
        QuickLayout.setSpacing(10)
        QuickButtons = [
            ("SEARCH", "primary", self.SearchLocation),
            ("SYNC", "success", self.ManualRefresh),
            ("UNITS", "warning", self.ToggleUnits),
            ("MAP", "accent", lambda: self.SwitchView("map")),
        ]
        for Text, Role, Handler in QuickButtons:
            Btn = LCARSButton(Text, Type=LCARSButton.PILL, Parent=QuickRow)
            self.ApplyButtonState(Btn, Role)
            Btn.clicked.connect(Handler)
            QuickLayout.addWidget(W(Btn))
        SideLayout.addWidget(W(QuickRow))
        SideLayout.addWidget(W(LCARSLabel("VIEW MODES", Color=TEXT_SECONDARY, FontSize=11, Parent=SidePanel)))
        self.NavButtons = {}
        NavItems = [
            ("overview", "OVERVIEW", "primary"),
            ("forecast", "5-DAY", "accent"),
            ("hourly", "24-HOUR", "warning"),
            ("metrics", "METRICS", "success"),
            ("map", "MAP", "accent"),
        ]
        for Key, Label, Role in NavItems:
            Btn = LCARSButton(Label, Type=LCARSButton.PILL, Parent=SidePanel)
            self.ApplyButtonState(Btn, Role, Key == self.CurrentView)
            Btn.clicked.connect(lambda _=None, k=Key: self.SwitchView(k))
            self.NavButtons[Key] = Btn
            SideLayout.addWidget(W(Btn))
        SideLayout.addWidget(W(LCARSLabel("SYSTEM TELEMETRY", Color=TEXT_SECONDARY, FontSize=11, Parent=SidePanel)))
        self.SignalBlock = DataBlock("SIGNAL STRENGTH", "78 %", BUTTON_ACTIVE, Parent=SidePanel)
        self.GridBlock = DataBlock("GRID HEALTH", "98 %", BUTTON_ACTIVE, Parent=SidePanel)
        self.LinkBlock = DataBlock("SAT LINK", "READY", BUTTON_ACCENT, Parent=SidePanel)
        SideLayout.addWidget(W(self.SignalBlock))
        SideLayout.addWidget(W(self.GridBlock))
        SideLayout.addWidget(W(self.LinkBlock))
        SideLayout.addStretch()
        ParentLayout.addWidget(W(SidePanel))

    def SwitchView(self, View):
        self.CurrentView = View
        self.RefreshViewMode()

    def RefreshViewMode(self):
        for Key, Page in self.ViewPages.items():
            Page.setVisible(True)
        for Key, Btn in self.NavButtons.items():
            self.ApplyButtonState(Btn, "primary", Key == self.CurrentView)
        if hasattr(self, "MapLabel"):
            self.MapLabel.SetText(f"TACTICAL MAP: {self.Engine.LocationName}")
        if hasattr(self, "MapNote"):
            if self.CurrentView == "map":
                self.MapNote.SetText("LIVE OVERLAY READY FOR ROUTE AND RADAR DATA")
            else:
                self.MapNote.SetText("SELECT MAP PANEL TO VIEW THE EXPANDED OVERLAY")

    def PanelStyle(self, Weight=2):
        return f"background-color: {PANEL_BACKGROUND}; border: {Weight}px solid {PANEL_EDGE}; border-radius: 16px;"

    def ApplyButtonState(self, Btn, Role="primary", Active=False):
        if Btn not in self.DynamicButtons: self.DynamicButtons.append(Btn)
        Btn.ToneRole = Role
        Btn.SetColor(RandomButtonColor(self.ButtonGroup(Role)))
        if hasattr(Btn, "SetLatched"): Btn.SetLatched(Active)

    def ButtonGroup(self, Role):
        if self.AlertMode == "yellow": return "YellowAlert"
        if self.AlertMode == "red": return "RedAlert"
        return BUTTON_GROUPS.get(Role, "Buttons")

    def ManualRefresh(self):
        self.StatusLabel.SetText("REFRESHING...")
        self.Engine.RefreshWeather()
        self.Engine.RefreshForecast()

    def ToggleUnits(self):
        self.Engine.Unit = "imperial" if self.Engine.Unit == "metric" else "metric"
        if hasattr(self, "UnitBtn"):
            self.UnitBtn.SetText("IMPERIAL" if self.Engine.Unit == "imperial" else "METRIC")
        if hasattr(self, "ToggleUnitsBtn"):
            self.ToggleUnitsBtn.SetText("IMPERIAL" if self.Engine.Unit == "imperial" else "METRIC")
        self.ManualRefresh()

    def SwitchLocation(self, Idx):
        self.CurrentLocIdx = Idx
        self.Engine.SearchLocation(self.Locations[Idx])

    def AddLocation(self):
        Text = self.SearchInput.text().strip()
        if Text:
            self.Locations.append(Text.upper())
            self.SwitchLocation(len(self.Locations)-1)

    def SearchLocation(self):
        Text = self.SearchInput.text().strip()
        if Text:
            self.StatusLabel.SetText("SEARCHING LOCATION...")
            self.Engine.SearchLocation(Text)

    def ToggleFullscreen(self):
        super().ToggleFullscreen()
        if getattr(self, "PaddFullscreen", False):
            self.FullscreenBtn.SetText("WINDOWED")
            self.StatusLabel.SetText("PADD FULLSCREEN ENABLED")
        else:
            self.FullscreenBtn.SetText("FULLSCREEN")
            self.StatusLabel.SetText("PADD MODE RESTORED")

    def CycleAlertMode(self):
        Modes = ["normal", "yellow", "red"]
        Index = Modes.index(self.AlertMode) if self.AlertMode in Modes else 0
        self.AlertMode = Modes[(Index + 1) % len(Modes)]
        Labels = {"normal": "ALERT: OFF", "yellow": "ALERT: YELLOW", "red": "ALERT: RED"}
        if hasattr(self, "AlertBtn"):
            self.AlertBtn.SetText(Labels[self.AlertMode])
            self.ApplyButtonState(self.AlertBtn, "warning" if self.AlertMode != "red" else "alert", self.AlertMode != "normal")
        self.RefreshDynamicPalette()
        if hasattr(self, "FooterLabel"):
            self.FooterLabel.SetText(f"PALETTE MODE: {Labels[self.AlertMode]}")

    def PrepareShutdown(self):
        self.ShuttingDown = True

    def SetupChronometer(self):
        self.ChronoThread = threading.Thread(target=self.RunChronometer, daemon=True)
        self.ChronoThread.start()
        self.ChronoLabel.SetText(f"STARDATE: {ChronometerSubsystem.get_stardate()}")

    def SetupPaletteCycle(self):
        self.PaletteThread = threading.Thread(target=self.RunPaletteCycle, daemon=True)
        self.PaletteThread.start()

    def RunChronometer(self):
        while not self.ShuttingDown:
            self.ChronoLabel.SetText(f"STARDATE: {ChronometerSubsystem.get_stardate()}")
            time.sleep(1)

    def RunPaletteCycle(self):
        while not self.ShuttingDown:
            self.AdvancePalette()
            time.sleep(2)

    def AdvancePalette(self):
        if self.ShuttingDown: return
        for B in self.DynamicButtons:
            B.SetColor(RandomButtonColor(self.ButtonGroup(getattr(B, "ToneRole", "primary"))))

    def OnLocationResolved(self, Loc):
        self.StatusLabel.SetText(f"LOCATION: {Loc}")
        if hasattr(self, "MapLabel"):
            self.MapLabel.SetText(f"TACTICAL MAP: {Loc}")
        if hasattr(self, "FooterLabel"):
            self.FooterLabel.SetText(f"LIVE MATRIX: {Loc}")

    def OnWeatherUpdate(self, Data):
        if Data.get("Status") == "success":
            Unit = "°F" if self.Engine.Unit == "imperial" else "°C"
            self.TempLabel.SetText(f"TEMP: {Data.get('Temp')} {Unit}")
            self.CondLabel.SetText(f"{Data.get('Icon')} {Data.get('Condition')}")
            self.MainBlocks[0].SetText(f"{Data.get('Humidity', '--')} %")
            self.MainBlocks[1].SetText(f"{Data.get('WindSpeed', '--')} {self.Engine.GetWindUnit()}")
            if hasattr(self, "DetailBlocks"):
                self.DetailBlocks[0].SetText(str(Data.get("Pressure", "--")))
                self.DetailBlocks[1].SetText(str(Data.get("DewPoint", "--")))
                self.DetailBlocks[2].SetText(f"{Data.get('Visibility', '--')} km")
            if "Hourly" in Data:
                for i, H in enumerate(Data["Hourly"][:12]):
                    if i < len(self.HourlyRows):
                        self.HourlyRows[i].SetText(f"{H['Time']}: {H['Temp']}{Unit} {H['Icon']}")
            self.MetricBlocks["uv"].SetText(str(Data.get("UVIndex", "--")))
            self.MetricBlocks["vis"].SetText(f"{Data.get('Visibility', '--')} km")
            self.MetricBlocks["cloud"].SetText(f"{Data.get('CloudCover', '--')} %")
            if hasattr(self, "ExtendedMetricBlocks"):
                self.ExtendedMetricBlocks["pressure"].SetText(str(Data.get("Pressure", "--")))
                self.ExtendedMetricBlocks["dew"].SetText(str(Data.get("DewPoint", "--")))

    def OnForecastUpdate(self, Data):
        if Data.get("Status") == "success":
            Unit = "°F" if self.Engine.Unit == "imperial" else "°C"
            for i, D in enumerate(Data["Daily"]):
                if i < len(self.ForecastRows):
                    self.ForecastRows[i].SetText(f"{D['Date']}: {D['TempMax']}{Unit} {D['Icon']}")

    def SyncAlertState(self):
        # Placeholder as original logic was lost during PascalCase conversion
        pass

    def RefreshDynamicPalette(self):
        for B in self.DynamicButtons:
            B.SetColor(RandomButtonColor(self.ButtonGroup(getattr(B, "ToneRole", "primary"))))

# Робимо дисплей безрамковим і прозорим, використовуючи внутрішній протокол LCARS
