# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: from pathlib import Path
# Titanium Bridge Migration: from typing import Any, Dict, Optional, cast

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lcars.base.component import (
    Graphic, LCARSLabel, LCARSButton,
    LCARSDataBlock, LCARSBar, LCARSDivider, PillButton,
    LCARSStatBar,
)
SystemComponent = Graphic 

from lcars.base.default import (
    DefaultBackground,
    DefaultPalette,
    RandomButtonColor,
)
from lcars.base.type import Directive, Primitives, ODN, LCARSTypes, Chassis
from lcars.base.interface import LCARSPadd
from lcars.utilities.chronometer import ChronometerSubsystem
# Titanium Bridge Migration: import datetime

# ─── Layout Helpers ──────────────────────────────────────────────────────────
def CreateLayout(Name, Parent=None):
    Layout = getattr(Primitives, "VBox", None)
    if Name in ["HBoxLayout", "HBox"]:
        Layout = getattr(Primitives, "HBox", None)
    elif Name == "Grid":
        Layout = getattr(Primitives, "Grid", None)
    if Layout is None:
        raise ValueError(f"Unknown layout type: {Name}")
    return Layout(Parent)
    
# Direction substitutes
class LayoutDirection:
    LeftToRight = Directive.Protocol.LayoutDirection.LeftToRight if hasattr(Directive.Protocol, "LayoutDirection") else 0
    TopToBottom = Directive.Protocol.LayoutDirection.TopToBottom if hasattr(Directive.Protocol, "LayoutDirection") and hasattr(Directive.Protocol.LayoutDirection, "TopToBottom") else 1

PANEL_BACKGROUND = DefaultBackground
PANEL_EDGE       = DefaultPalette.Panels[1] 
PANEL_EDGE_SOFT  = DefaultPalette.Panels[0] 
PANEL_ACCENT     = DefaultPalette.Accent[1] 
TEXT_PRIMARY     = DefaultPalette.Panels[2] 
TEXT_SECONDARY   = DefaultPalette.Panels[1] 
BUTTON_PRIMARY   = DefaultPalette.Buttons[0] 
BUTTON_ACTIVE    = DefaultPalette.Buttons[1] 
BUTTON_ACCENT    = DefaultPalette.Accent[1] 
BUTTON_SUCCESS   = DefaultPalette.Accent[2] 
BUTTON_WARNING   = DefaultPalette.YellowAlert[0] 
BUTTON_ALERT     = DefaultPalette.RedAlert[0] 

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
    "ScrollBar:vertical { width: 0px; background: transparent; }"
    "ScrollBar:horizontal { height: 0px; background: transparent; }"
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
        self.OnWeather = Directive.Signal()
        self.OnForecast = Directive.Signal()
        self.OnLocation = Directive.Signal()
        self.DiscoveryThread = None

    def Start(self):
        # Titanium Bridge Migration: import threading
        if self.DiscoveryThread is None or not self.DiscoveryThread.is_alive():
            self.DiscoveryThread = threading.Thread(target=self.DiscoverLocation, daemon=True)
            self.DiscoveryThread.start()

    def ConnectWeather(self, Callback):
        self.OnWeather.connect(Callback)

    def ConnectForecast(self, Callback):
        self.OnForecast.connect(Callback)

    def ConnectLocation(self, Callback):
        self.OnLocation.connect(Callback)

    def EmitWeather(self, Data):
        ODN.Emit("Weather.Current", Data)
        self.OnWeather.emit(Data)

    def EmitForecast(self, Data):
        ODN.Emit("Weather.Forecast", Data)
        self.OnForecast.emit(Data)

    def EmitLocation(self, Location):
        ODN.Emit("Weather.Location", {"location": Location})
        self.OnLocation.emit(Location)

    def HttpGetJson(self, Url: str) -> Optional[dict]:
        from urllib.request import Request, urlopen
        # Titanium Bridge Migration: import json
        RequestObj = Request(Url, headers={"User-Agent": "LCARS Weather Matrix/1.0"})
        if True:
            with urlopen(RequestObj, timeout=10) as Response:
                Code = getattr(Response, "status", None) or Response.getcode()
                if Code != 200:
                    return None
                Payload = Response.read()
                return json.loads(Payload.decode("utf-8"))
        if False: # Removed except block
            return None

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
        # Titanium Bridge Migration: import threading
        threading.Thread(target=self.FetchCurrentWeather, daemon=True).start()
        threading.Thread(target=self.FetchHourly, daemon=True).start()

    def RefreshForecast(self):
        if not self.IsReady: return
        # Titanium Bridge Migration: import threading
        threading.Thread(target=self.FetchForecast, daemon=True).start()

    def SearchLocation(self, Query: str):
        if not Query: return
        # Titanium Bridge Migration: import threading
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
                # Titanium Bridge Migration: import datetime
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
        self.resize(1040, 760)
        self.setStyleSheet("background: transparent;")
        self.Viewport.setStyleSheet(f"background-color: {PANEL_BACKGROUND}; border-radius: 18px;")
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

        AppInstance = getattr(cast(Any, Directive.Application), "instance", lambda: None)()
        if AppInstance and hasattr(AppInstance, "aboutToQuit"):
            AppInstance.aboutToQuit.connect(self.PrepareShutdown)

        self.BuildUI()
        self.SyncAlertState()
        self.SetupChronometer()
        self.SetupPaletteCycle()
        self.Engine.Start()

    def BuildUI(self):
        Central = self.Viewport
        MainLayout = CreateLayout("VBox", Central)
        if hasattr(Central, "setLayout"): Central.setLayout(MainLayout)
        
        MainLayout.setContentsMargins(18, 18, 18, 18)
        MainLayout.setSpacing(14)

        ScrollFactory = cast(Any, LCARSTypes.Scroll)
        self.BodyScroll = ScrollFactory(Central)
        self.BodyScroll.setWidgetResizable(True)
        self.BodyScroll.setHorizontalScrollBarPolicy(SCROLLBAR_OFF)
        self.BodyScroll.setVerticalScrollBarPolicy(SCROLLBAR_OFF)
        self.BodyScroll.setStyleSheet(HIDDEN_SCROLL_STYLE)

        BodyHost = SystemComponent(self.BodyScroll)
        BodyHost.setStyleSheet("background: transparent;")
        BodyLayout = CreateLayout("VBox", BodyHost)
        BodyLayout.setContentsMargins(0, 0, 0, 0)
        BodyLayout.setSpacing(14)
        self.BodyScroll.setWidget(BodyHost)
        MainLayout.addWidget(self.BodyScroll, 1)

        Header = SystemComponent(Central)
        Header.setStyleSheet(self.PanelStyle())
        HeaderLayout = CreateLayout("HBox", Header)
        HeaderLayout.setContentsMargins(16, 14, 16, 14)
        HeaderLayout.setSpacing(10)
        Title = LCARSLabel("◤ TITANIUM WEATHER MATRIX", Color=TEXT_PRIMARY, FontSize=24, Parent=Header)
        HeaderLayout.addWidget(Title)
        self.ChronoLabel = LCARSLabel("STARDATE: --", Color=TEXT_SECONDARY, FontSize=12, Parent=Header)
        HeaderLayout.addWidget(self.ChronoLabel)
        self.StatusLabel = LCARSLabel("SYSTEM STATUS: SYNCHRONIZING", Color=TEXT_SECONDARY, FontSize=12, Parent=Header)
        HeaderLayout.addWidget(self.StatusLabel)
        HeaderLayout.addStretch()
        RefreshBtn = LCARSButton("REFRESH", Type=LCARSButton.ROUNDED, Parent=Header)
        self.ApplyButtonState(RefreshBtn, "primary")
        RefreshBtn.Clicked = self.ManualRefresh
        HeaderLayout.addWidget(RefreshBtn)
        BodyLayout.addWidget(Header)

        TabsFrame = SystemComponent(self)
        TabsFrame.setStyleSheet(self.PanelStyle())
        TabsLayout = CreateLayout("HBox", TabsFrame)
        TabsLayout.setContentsMargins(12, 8, 12, 8)
        TabsLayout.setSpacing(10)
        for i, Loc in enumerate(self.Locations):
            Btn = LCARSButton(Loc[:12], Type=LCARSButton.ROUNDED, Parent=TabsFrame)
            self.ApplyButtonState(Btn, "accent", i == self.CurrentLocIdx)
            Btn.Clicked = lambda idx=i: self.SwitchLocation(idx)
            TabsLayout.addWidget(Btn)
        TabsLayout.addStretch()
        self.SearchInput = cast(Any, LCARSTypes.Input())
        self.SearchInput.setPlaceholderText("LOCATION...")
        self.SearchInput.setStyleSheet(f"background: {PANEL_BACKGROUND}; color: {TEXT_PRIMARY}; border: 1px solid {PANEL_EDGE}; padding: 5px;")
        TabsLayout.addWidget(self.SearchInput)
        AddBtn = LCARSButton("+", Type=LCARSButton.ROUNDED, Parent=TabsFrame)
        self.ApplyButtonState(AddBtn, "success")
        AddBtn.Clicked = self.AddLocation
        TabsLayout.addWidget(AddBtn)
        BodyLayout.addWidget(TabsFrame)

        ContentFrame = SystemComponent(self)
        ContentFrame.setStyleSheet(self.PanelStyle())
        ContentLayout = CreateLayout("HBox", ContentFrame)
        ContentLayout.setContentsMargins(18, 18, 18, 18)
        ContentLayout.setSpacing(20)
        Side = SystemComponent(self)
        Side.setStyleSheet(self.PanelStyle())
        SideLayout = CreateLayout("VBox", Side)
        SideLayout.setContentsMargins(18, 18, 18, 18)
        SideLayout.setSpacing(14)
        NavItems = [("overview", "OVERVIEW"), ("forecast", "5-DAY"), ("hourly", "24-HOUR"), ("metrics", "METRICS")]
        self.NavButtons = {}
        for Key, Label in NavItems:
            Btn = LCARSButton(Label, Type=LCARSButton.ROUNDED, Parent=Side)
            self.ApplyButtonState(Btn, "primary", Key == self.CurrentView)
            Btn.Clicked = lambda k=Key: self.SwitchView(k)
            self.NavButtons[Key] = Btn
            SideLayout.addWidget(Btn)
        SideLayout.addStretch()
        self.UnitBtn = LCARSButton("UNITS", Type=LCARSButton.ROUNDED, Parent=Side)
        self.ApplyButtonState(self.UnitBtn, "warning")
        self.UnitBtn.Clicked = self.ToggleUnits
        SideLayout.addWidget(self.UnitBtn)
        ContentLayout.addWidget(Side, 1)

        self.MainScroll = ScrollFactory(ContentFrame)
        self.MainScroll.setWidgetResizable(True)
        self.MainScroll.setHorizontalScrollBarPolicy(SCROLLBAR_OFF)
        self.MainScroll.setVerticalScrollBarPolicy(SCROLLBAR_OFF)
        self.MainScroll.setStyleSheet(HIDDEN_SCROLL_STYLE)
        MainPanel = SystemComponent(self.MainScroll)
        MainPanelLayout = CreateLayout("VBox", MainPanel)
        self.ViewPages = {}
        self.BuildOverviewPage(MainPanelLayout)
        self.BuildForecastPage(MainPanelLayout)
        self.BuildHourlyPage(MainPanelLayout)
        self.BuildMetricsPage(MainPanelLayout)
        self.MainScroll.setWidget(MainPanel)
        ContentLayout.addWidget(self.MainScroll, 3)
        BodyLayout.addWidget(ContentFrame, 1)
        self.RefreshViewMode()

    def BuildOverviewPage(self, Layout):
        Page = SystemComponent(self)
        PageLayout = CreateLayout("VBox", Page)
        self.ViewPages["overview"] = Page
        self.TempLabel = LCARSLabel("TEMP: --", FontSize=30, Color=BUTTON_WARNING, Parent=Page)
        PageLayout.addWidget(self.TempLabel)
        self.CondLabel = LCARSLabel("COND: --", FontSize=18, Color=TEXT_PRIMARY, Parent=Page)
        PageLayout.addWidget(self.CondLabel)
        self.MainBlocks = [
            LCARSDataBlock(Label="HUMIDITY", Value="-- %", Color=BUTTON_ACTIVE, Parent=Page),
            LCARSDataBlock(Label="WIND", Value="--", Color=BUTTON_ACCENT, Parent=Page)
        ]
        for B in self.MainBlocks: 
            PageLayout.addWidget(B)
            B.setMinimumHeight(60)
        Layout.addWidget(Page)

    def BuildForecastPage(self, Layout):
        Page = SystemComponent(self)
        self.ViewPages["forecast"] = Page
        PageLayout = CreateLayout("VBox", Page)
        self.ForecastRows = []
        for i in range(5):
            Row = LCARSLabel("DAY --: --", Parent=Page)
            Row.setMinimumHeight(40)
            self.ForecastRows.append(Row)
            PageLayout.addWidget(Row)
        Layout.addWidget(Page)

    def BuildHourlyPage(self, Layout):
        Page = SystemComponent(self)
        self.ViewPages["hourly"] = Page
        PageLayout = CreateLayout("VBox", Page)
        self.HourlyRows = []
        for i in range(12):
            Row = LCARSLabel("+H --: --", Parent=Page)
            Row.setMinimumHeight(30)
            self.HourlyRows.append(Row)
            PageLayout.addWidget(Row)
        Layout.addWidget(Page)

    def BuildMetricsPage(self, Layout):
        Page = SystemComponent(self)
        self.ViewPages["metrics"] = Page
        PageLayout = CreateLayout("VBox", Page)
        self.MetricBlocks = {
            "uv": LCARSDataBlock(Label="UV INDEX", Value="--", Color=BUTTON_WARNING, Parent=Page),
            "vis": LCARSDataBlock(Label="VISIBILITY", Value="-- km", Color=BUTTON_ACCENT, Parent=Page),
            "cloud": LCARSDataBlock(Label="CLOUD COVER", Value="-- %", Color=BUTTON_ACTIVE, Parent=Page)
        }
        for B in self.MetricBlocks.values(): 
            PageLayout.addWidget(B)
            B.setMinimumHeight(60)
        Layout.addWidget(Page)

    def SwitchView(self, View):
        self.CurrentView = View
        self.RefreshViewMode()

    def RefreshViewMode(self):
        for Key, Page in self.ViewPages.items():
            Page.setVisible(Key == self.CurrentView)
        for Key, Btn in self.NavButtons.items():
            self.ApplyButtonState(Btn, "primary", Key == self.CurrentView)

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
        self.ManualRefresh()

    def SwitchLocation(self, Idx):
        self.CurrentLocIdx = Idx
        self.Engine.SearchLocation(self.Locations[Idx])

    def AddLocation(self):
        Text = self.SearchInput.text().strip()
        if Text:
            self.Locations.append(Text.upper())
            self.SwitchLocation(len(self.Locations)-1)

    def PrepareShutdown(self):
        self.ShuttingDown = True

    def SetupChronometer(self):
        TimerClass = getattr(Primitives, "Timer", None)
        if TimerClass:
            Timer = TimerClass(self)
            Timer.timeout.connect(lambda: self.ChronoLabel.SetText(f"STARDATE: {ChronometerSubsystem.get_stardate()}"))
            Timer.start(1000)

    def SetupPaletteCycle(self):
        TimerClass = getattr(Primitives, "Timer", None)
        if TimerClass:
            Timer = TimerClass(self)
            Timer.timeout.connect(self.AdvancePalette)
            Timer.start(2000)

    def AdvancePalette(self):
        if self.ShuttingDown: return
        for B in self.DynamicButtons:
            B.SetColor(RandomButtonColor(self.ButtonGroup(getattr(B, "ToneRole", "primary"))))

    def OnLocationResolved(self, Loc):
        self.StatusLabel.SetText(f"LOCATION: {Loc}")

    def OnWeatherUpdate(self, Data):
        if Data.get("Status") == "success":
            Unit = "°F" if self.Engine.Unit == "imperial" else "°C"
            self.TempLabel.SetText(f"TEMP: {Data.get('Temp')} {Unit}")
            self.CondLabel.SetText(f"{Data.get('Icon')} {Data.get('Condition')}")
            self.MainBlocks[0].SetValue(f"{Data.get('Humidity', '--')} %")
            self.MainBlocks[1].SetValue(f"{Data.get('WindSpeed', '--')} {self.Engine.GetWindUnit()}")
            if "Hourly" in Data:
                for i, H in enumerate(Data["Hourly"][:12]):
                    if i < len(self.HourlyRows):
                        self.HourlyRows[i].SetText(f"{H['Time']}: {H['Temp']}{Unit} {H['Icon']}")
            self.MetricBlocks["uv"].SetValue(str(Data.get("UVIndex", "--")))
            self.MetricBlocks["vis"].SetValue(f"{Data.get('Visibility', '--')} km")
            self.MetricBlocks["cloud"].SetValue(f"{Data.get('CloudCover', '--')} %")

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

if __name__ == "__main__":
    AppFactory = cast(Any, Directive.Application)
    MainApp = AppFactory(sys.argv)
    Window = WeatherStation()
    Window.show()
    sys.exit(MainApp.exec())
