# ◤ TITANIUM WEATHER STATION — v44.20 🖖
# LCARS Framework :: METEOROLOGICAL_SCANNER // ATMOSPHERIC_SENSORS // NO_Q PROTOCOL
# ─────────────────────────────────────────────────────────────────────────────
# ОПИС: Уніфікована метеостанція Titanium. Поєднує сканер та погодний двигун.
# ФУНКЦІЇ: Автовизначення локації, поточна телеметрія та прогноз на 7 днів.
# СТАНДАРТ: Titanium CamelCase // No-Contours // Zero-Except.
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

# Clean LCARS Weather Station (temp test file)
# No triple-quoted docstrings, no `except` blocks, camelCase identifiers.

# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import os
import time
# Titanium Bridge Migration: import json
# Titanium Bridge Migration: import requests
# Titanium Bridge Migration: import threading
# Titanium Bridge Migration: from pathlib import Path
# Titanium Bridge Migration: from typing import Dict, Any, Tuple

# Ensure project root is in sys.path for direct script execution
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from lcars.base.register import registry
from lcars.base.types import (
    Visual, Directive, Matrix, Chassis, Application, LCARS,
    VBoxLayout, HBoxLayout, GridLayout, Timer, Signal, Logic, Lore, ODN
)
from lcars.base.interface import (
    Label, Button, LCARSButton, Frame, Elbow, ScanningBar, DataBlock, StatBar, Pill,
    LCARSPadd, LCARSLabel, LCARSWaveform, LCARSScreen
)
from lcars.base.defaults import TitanPalette, RandomButtonColor, ActivePalette, GetLcarsFontStyle
from lcars.engineering.telemetry import EmitTelemetry
from lcars.modules.net import NetworkManager


# 1. ПОГОДНИЙ ДВИГУН (WEATHER ENGINE MATRIX)
class WeatherEngine(Visual):
    # Ядро обробки атмосферних даних: Використовує підпросторові запити (HTTP) для телеметрії.
    CurrentWeatherSignal = Signal(dict)
    ForecastUpdatedSignal = Signal(dict)
    
    def __init__(self):
        super().__init__()
        self.LastTelemetryUpdateValue = 0
        self.CacheExpirationInterval = 900 
        self.CurrentWeatherCacheMap = {}
        self._has_new_current = False
        self._has_new_forecast = False
        
        # Координати за замовчуванням (Starfleet Command, Earth)
        self.LatitudeValue = 37.7749
        self.LongitudeValue = -122.4194
        self.LocationNameStr = "SAN FRANCISCO, EARTH"
        self.IsLocationEstablished = False
        self.Network = NetworkManager()
        
        # Запуск автоматичного визначення локації вузла (Worker Thread)
        threading.Thread(target=self.ExecuteAutoDiscoveryLogic, daemon=True).start()

    def ExecuteAutoDiscoveryLogic(self):
        Success, DiscoveryDataMap = self.Network.RequestJson("http://ip-api.com/json/", Timeout=5)
        if Success and isinstance(DiscoveryDataMap, dict):
            if DiscoveryDataMap.get("status") == "success":
                self.LatitudeValue = DiscoveryDataMap.get("lat", self.LatitudeValue)
                self.LongitudeValue = DiscoveryDataMap.get("lon", self.LongitudeValue)
                CityStr = DiscoveryDataMap.get("city", "UNKNOWN").upper()
                CountryStr = DiscoveryDataMap.get("country", "EARTH").upper()
                self.LocationNameStr = f"{CityStr}, {CountryStr}"
        self.IsLocationEstablished = True
        self.RefreshAtmosCurrentCondition()

    def RefreshAtmosCurrentCondition(self):
        threading.Thread(target=self.ExecuteTelemetryFetchLogic, daemon=True).start()
        
    def RefreshAtmosForecast(self):
        threading.Thread(target=self.ExecuteForecastFetchLogic, daemon=True).start()

    def ExecuteTelemetryFetchLogic(self):
        while not self.IsLocationEstablished: time.sleep(0.5)
        NowTimestampValue = time.time()

        if NowTimestampValue - self.LastTelemetryUpdateValue < self.CacheExpirationInterval and self.CurrentWeatherCacheMap:
            self._has_new_current = True
            return

        RequestUrlStr = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={self.LatitudeValue}&longitude={self.LongitudeValue}&current_weather=true"
        )
        Success, RawDataMap = self.Network.RequestJson(RequestUrlStr, Timeout=10)
        if Success and isinstance(RawDataMap, dict):
            CurrentDataMap = RawDataMap.get("current_weather", {})
            WmoCodeValue = CurrentDataMap.get("weathercode", 0)
            ConditionStr, _ = self.TranslateMeteorologicalCode(WmoCodeValue)

            self.CurrentWeatherCacheMap = {
                "Temp":          CurrentDataMap.get("temperature", 0.0),
                "WindSpeed":     CurrentDataMap.get("windspeed", 0.0),
                "Condition":     ConditionStr,
                "Location":      self.LocationNameStr,
                "Status":        "success"
            }
            self.LastTelemetryUpdateValue = NowTimestampValue
            self._has_new_current = True
        else:
            self.CurrentWeatherCacheMap = {"Status": "error", "Message": "HTTP REQUEST FAILED"}
            self._has_new_current = True

    def ExecuteForecastFetchLogic(self):
        while not self.IsLocationEstablished: time.sleep(0.5)

        RequestUrlStr = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={self.LatitudeValue}&longitude={self.LongitudeValue}&"
            f"daily=temperature_2m_max,temperature_2m_min,weathercode&timezone=auto"
        )
        Success, RawDataMap = self.Network.RequestJson(RequestUrlStr, Timeout=10)
        if Success and isinstance(RawDataMap, dict):
            DailyDataMap = RawDataMap.get("daily", {})
            ForecastList = []
            TimePointsList = DailyDataMap.get("time", [])
            for i in range(min(5, len(TimePointsList))):
                WmoCodeVal = DailyDataMap.get("weathercode", [])[i]
                CondStr, _ = self.TranslateMeteorologicalCode(WmoCodeVal)
                ForecastList.append({
                    "Date":      TimePointsList[i],
                    "TempMax":   DailyDataMap.get("temperature_2m_max", [])[i],
                    "Condition": CondStr
                })
            self.LastForecastMap = {"Status": "success", "Daily": ForecastList}
            self._has_new_forecast = True
        else:
            self.LastForecastMap = {"Status": "error", "Message": "HTTP REQUEST FAILED"}
            self._has_new_forecast = True

    def TranslateMeteorologicalCode(self, CodeValue: int) -> Tuple[str, bool]:
        InterpretationMap = {
            0: ("CLEAR", False), 1: ("MOSTLY CLEAR", False), 2: ("PARTLY CLOUDY", False), 3: ("OVERCAST", False),
            45: ("FOG", True), 51: ("LIGHT DRIZZLE", False), 55: ("DENSE DRIZZLE", True), 61: ("SLIGHT RAIN", False),
            65: ("HEAVY RAIN", True), 71: ("SLIGHT SNOW", False), 75: ("HEAVY SNOW", True), 95: ("THUNDERSTORM", True)
        }
        return InterpretationMap.get(CodeValue, (f"UNKNOWN ({CodeValue})", False))


# 2. ГОЛОВНА ПРОГРАМА (TITANIUM WEATHER STATION)
class WeatherStation(LCARSPadd):
    # Візуалізатор метеорологічних даних та стану навколишнього середовища.
    def __init__(self, ParentNode=None, **kwargs):
        palette_color = TitanPalette.Scientific[1] if hasattr(TitanPalette, 'Scientific') else TitanPalette.Buttons[1]
        super().__init__(TitleStr="◤ SENSORS // WEATHER STATION", color=palette_color, ParentNode=ParentNode)

        self.IsLocationEstablished = False
        # Ініціалізація двигуна
        self.EngineNode = WeatherEngine()
        self.EngineNode.CurrentWeatherSignal.connect(self.OnWeatherUpdate)
        self.EngineNode.ForecastUpdatedSignal.connect(self.OnForecastUpdate)

        self.BuildInterface()

        # Початкові плейсхолдерні дані, щоб інтерфейс не залишався порожнім
        self.OnWeatherUpdate({
            "Status": "success",
            "Temp": 22.3,
            "WindSpeed": 4.5,
            "Condition": "CLEAR",
            "Location": self.EngineNode.LocationNameStr
        })
        self.OnForecastUpdate({
            "Status": "success",
            "Daily": [
                {"Date": "TODAY", "TempMax": 22, "Condition": "CLEAR"},
                {"Date": "TOMORROW", "TempMax": 24, "Condition": "PARTLY CLOUDY"},
                {"Date": "+2", "TempMax": 23, "Condition": "LIGHT RAIN"},
                {"Date": "+3", "TempMax": 21, "Condition": "FOG"},
                {"Date": "+4", "TempMax": 20, "Condition": "CLEAR"}
            ]
        })

        # Запуск сканера
        self.EngineNode.RefreshAtmosCurrentCondition()
        self.EngineNode.RefreshAtmosForecast()
        EmitTelemetry("Weather", "WEATHER STATION INITIALIZED // ORBITAL LINK ACTIVE.")

    def BuildInterface(self):
        self.setMinimumSize(1280, 720)
        self.setWindowTitle("Titan Weather Station")
        self.setStyleSheet("background: #001b20;")
        self.viewport().setStyleSheet("background: #041f2d;")

        Layout = self.viewport_layout()
        Layout.setContentsMargins(20, 20, 20, 20)
        Layout.setSpacing(16)

        # HEADER
        HeaderODN = ODN.Horizontal()
        HeaderODN.setSpacing(10)
        HeaderLabel = LCARSLabel("◤ SENSORS // WEATHER STATION", FontSizeVal=28, ColorHexStr="#79ffb1", WeightStr="bold")
        self.StatusNode = LCARSLabel("STATUS: INITIALIZING", FontSizeVal=12, ColorHexStr="#a5ff9f")
        HeaderODN.addWidget(HeaderLabel)
        HeaderODN.addStretch()
        HeaderODN.addWidget(self.StatusNode)
        Layout.addLayout(HeaderODN)

        # MESSAGE
        self.DebugLabel = LCARSLabel("◤ WEATHER STATION ACTIVE", FontSizeVal=14, ColorHexStr="#8bffbd")
        Layout.addWidget(self.DebugLabel)
        self.FallbackDataLabel = LCARSLabel("◤ FALLBACK: NO DATA", FontSizeVal=11, ColorHexStr="#ffb3b3")
        self.FallbackDataLabel.setVisible(False)
        Layout.addWidget(self.FallbackDataLabel)

        # CONTENT
        ContentODN = ODN.Horizontal()
        ContentODN.setSpacing(20)

        # Metrics Panel
        MetricsPanel = Frame()
        MetricsPanel.setStyleSheet("background:#0b2430;border:1px solid #3bdc93;border-radius:12px;")
        MetricsLayout = MetricsPanel.viewport_layout()
        MetricsLayout.setContentsMargins(12, 12, 12, 12)
        MetricsLayout.setSpacing(10)

        self.LocationLabelNode = LCARSLabel("◤ LOCATION: UNKNOWN", FontSizeVal=12, ColorHexStr="#aadfae")
        self.TempBlock = DataBlock("TEMPERATURE", "--.- °C", ColorHexStr="#FF9900")
        self.WindBlock = DataBlock("WIND VELOCITY", "--.- km/h", ColorHexStr="#3399FF")
        self.CondBlock = DataBlock("CONDITION", "UNKNOWN", ColorHexStr="#88FF88")

        MetricsLayout.addWidget(self.LocationLabelNode)
        MetricsLayout.addWidget(self.TempBlock)
        MetricsLayout.addWidget(self.WindBlock)
        MetricsLayout.addWidget(self.CondBlock)

        ContentODN.addWidget(MetricsPanel, 1)

        # Forecast Panel
        ForecastPanel = Frame()
        ForecastPanel.setStyleSheet("background:#0d2842;border:1px solid #66ffd5;border-radius:12px;")
        ForecastLayout = ForecastPanel.viewport_layout()
        ForecastLayout.setContentsMargins(10, 10, 10, 10)
        ForecastLayout.setSpacing(8)

        ForecastLayout.addWidget(LCARSLabel("◤ 5-DAY ORBITAL FORECAST", FontSizeVal=14, ColorHexStr="#9ee4f2"))
        self.ForecastItems = []
        for i in range(5):
            row = ODN.Horizontal()
            row.setSpacing(10)
            day = LCARSLabel("---", FontSizeVal=11, ColorHexStr="#d2e2f0")
            temp = LCARSLabel("--.- °C", FontSizeVal=11, ColorHexStr="#ffffff")
            cond = LCARSLabel("---", FontSizeVal=11, ColorHexStr="#a2d0f8")
            row.addWidget(day, 1)
            row.addWidget(temp, 1)
            row.addWidget(cond, 1)
            ForecastLayout.addLayout(row)
            self.ForecastItems.append((day, temp, cond))

        ContentODN.addWidget(ForecastPanel, 2)
        Layout.addLayout(ContentODN, 1)

        # FOOTER
        FooterODN = ODN.Horizontal()
        FooterODN.setSpacing(10)
        self.FooterLabel = LCARSLabel("◢ MISSION STATUS: SENSORS NOMINAL", FontSizeVal=11, ColorHexStr="#b1efc3")
        FooterODN.addWidget(self.FooterLabel)
        FooterODN.addStretch()
        self.RefreshBtn = LCARSButton("RE-SCAN", ColorHexStr="#32aaec", shape="rect")
        self.RefreshBtn.setFixedSize(150, 38)
        self.RefreshBtn.clicked.connect(lambda: (self.EngineNode.RefreshAtmosCurrentCondition(), self.EngineNode.RefreshAtmosForecast()))
        FooterODN.addWidget(self.RefreshBtn)
        Layout.addLayout(FooterODN)

        # INITIAL DATA (visible immediate)
        self.OnWeatherUpdate({
            "Status": "success",
            "Temp": 22.3,
            "WindSpeed": 3.8,
            "Condition": "CLEAR",
            "Location": self.EngineNode.LocationNameStr,
        })
        self.OnForecastUpdate({
            "Status": "success",
            "Daily": [
                {"Date": "TODAY", "TempMax": 22, "Condition": "CLEAR"},
                {"Date": "TOMORROW", "TempMax": 24, "Condition": "PARTLY CLOUDY"},
                {"Date": "+2", "TempMax": 23, "Condition": "LIGHT RAIN"},
                {"Date": "+3", "TempMax": 21, "Condition": "FOG"},
                {"Date": "+4", "TempMax": 20, "Condition": "CLEAR"},
            ],
        })

        self.RenderStatusLabel = LCARSLabel("◤ RENDER CHECK: CONTENT PANEL IS ACTIVE", FontSizeVal=14, ColorHexStr="#33ff77")
        Layout.addWidget(self.RenderStatusLabel)
    def OnWeatherUpdate(self, DataMap: dict):
        def safe_set_block(block, value_str):
            setter = getattr(block, "SetDataContent", None)
            if callable(setter):
                setter(value_str)
                return
            setter = getattr(block, "set_value", None)
            if callable(setter):
                setter(value_str)
                return
            setter = getattr(block, "setText", None)
            if callable(setter):
                setter(value_str)
                return
            lbl = getattr(block, "lbl_value", None)
            if lbl is not None and callable(getattr(lbl, "setText", None)):
                lbl.setText(value_str)
                return

        if DataMap.get("Status") == "success":
            temp_str = f"{DataMap.get('Temp')} °C"
            wind_str = f"{DataMap.get('WindSpeed')} KM/H"
            cond_str = DataMap.get("Condition", "NOMINAL")

            safe_set_block(self.TempBlock, temp_str)
            safe_set_block(self.WindBlock, wind_str)
            safe_set_block(self.CondBlock, cond_str)

            # Labels and status are QLabel-based; call setText if available
            loc_setter = getattr(self.LocationLabelNode, "setText", None)
            if callable(loc_setter):
                loc_setter(f"◤ {DataMap.get('Location')}")
            status_setter = getattr(self.StatusNode, "setText", None)
            if callable(status_setter):
                status_setter("◢ MISSION STATUS: TELEMETRY RECEIVED")
            debug_setter = getattr(self.DebugLabel, "setText", None)
            if callable(debug_setter):
                debug_setter("◤ WEATHER DATA LOADED")
        else:
            status_setter = getattr(self.StatusNode, "setText", None)
            if callable(status_setter):
                status_setter(f"◢ ERROR: {DataMap.get('Message')}")
            debug_setter = getattr(self.DebugLabel, "setText", None)
            if callable(debug_setter):
                debug_setter("◤ WEATHER DATA FAILED")
            if hasattr(self, "FallbackDataLabel"):
                fb_setter = getattr(self.FallbackDataLabel, "setText", None)
                if callable(fb_setter):
                    fb_setter(f"⚠ Please check connection: {DataMap.get('Message')}")
                fb_vis = getattr(self.FallbackDataLabel, "setVisible", None)
                if callable(fb_vis):
                    fb_vis(True)

    def OnForecastUpdate(self, DataMap: dict):
        if DataMap.get("Status") == "success":
            Daily = DataMap.get("Daily", [])
            for i, DayData in enumerate(Daily):
                if i < len(self.ForecastItems):
                    DayLbl, ValLbl, SkyLbl = self.ForecastItems[i]
                    DayLbl.setText(DayData.get("Date"))
                    ValLbl.setText(f"{DayData.get('TempMax')} °C")
                    SkyLbl.setText(DayData.get("Condition"))
# РЕЄСТРАЦІЯ
registry.Register("Technical.Visual.WeatherStation", WeatherStation)


def run_headless(wait_seconds: int = 15) -> None:
    eng = WeatherEngine()
    start = time.time()
    while not getattr(eng, "IsLocationEstablished", False) and time.time() - start < wait_seconds:
        time.sleep(0.5)
    eng.RefreshAtmosCurrentCondition()
    eng.RefreshAtmosForecast()

    def print_current(d):
        print(json.dumps({"current": d}, ensure_ascii=False, indent=2))

    def print_forecast(d):
        print(json.dumps({"forecast": d}, ensure_ascii=False, indent=2))

    # In headless mode rely on polling cached values rather than connecting GUI signals.

    start2 = time.time()
    printed_current = False
    printed_forecast = False
    while time.time() - start2 < wait_seconds and not (printed_current and printed_forecast):
        if getattr(eng, "CurrentWeatherCacheMap", None) and not printed_current:
            print_current(eng.CurrentWeatherCacheMap)
            printed_current = True
        if getattr(eng, "LastForecastMap", None) and not printed_forecast:
            print_forecast(eng.LastForecastMap)
            printed_forecast = True
        time.sleep(0.5)


if __name__ == "__main__":
    if "--cli" in sys.argv or os.environ.get("LCARS_HEADLESS"):
        run_headless()
        sys.exit(0)

    from lcars.base.interface import SetupFont
    AppClassNode = registry.get("Technical.Application")
    AppInstanceObject = AppClassNode.instance() or AppClassNode(sys.argv)
    SetupFont()
    WinNode = WeatherStation()
    WinNode.showMaximized()
    sys.exit(AppInstanceObject.exec())
