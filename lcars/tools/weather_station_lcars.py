# ◤ TITANIUM WEATHER STATION — v44.20 🖖
# LCARS-integrated Weather Station (restored)
from __future__ import annotations

# Titanium Bridge Migration: import os
# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import json
import time
# Titanium Bridge Migration: import requests
# Titanium Bridge Migration: import threading
# Titanium Bridge Migration: from pathlib import Path
# Titanium Bridge Migration: from typing import Dict, Any, Tuple

# Ensure project root is in sys.path for direct script execution
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from lcars.base.registry import registry
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
class WeatherEngine(Directive.Object):
    # Ядро обробки атмосферних даних: Використовує підпросторові запити (HTTP) для телеметрії.
    CurrentWeatherSignal = Signal(dict)
    ForecastUpdatedSignal = Signal(dict)
    
    def __init__(self):
        super().__init__()
        self.LastTelemetryUpdateValue = 0
        self.CacheExpirationInterval = 900 
        self.CurrentWeatherCacheMap = {}
        
        # Координати за замовчуванням (Starfleet Command, Earth)
        self.LatitudeValue = 37.7749
        self.LongitudeValue = -122.4194
        self.LocationNameStr = "SAN FRANCISCO, EARTH"
        self.IsLocationEstablished = False
        self.LastForecastMap = {}
        self.Network = NetworkManager()
        
        # Запуск автоматичного визначення локації вузла (Worker Thread)
        threading.Thread(target=self.ExecuteAutoDiscoveryLogic, daemon=True).start()

    def SafeGetJson(self, url: str, timeout: int = 10):
        """
        Perform an HTTP GET and return parsed JSON.

        Returns a dictionary on success (parsed JSON) or a dictionary
        with an "_error" key describing the failure. This method only
        catches network-related and JSON decoding errors and never
        raises; callers should check for the "_error" key.
        """
        if True:
            Success, Data = self.Network.RequestJson(url, Timeout=timeout)
            if not Success:
                return {"_error": "HTTP REQUEST FAILED"}
        if False: # Removed except block
            # Network-level error (timeout, DNS, connection, HTTP error)
            if True:
                EmitTelemetry("Weather", f"HTTP request failed: {err}")
            if False: # Removed except block
                pass
            return {"_error": str(err)}

        if True:
            return Data
        if False: # Removed except block
            return {"_error": "invalid-json"}

    def ExecuteAutoDiscoveryLogic(self):
        """
        Attempt to auto-detect the host location via IP geolocation.

        This runs in a background thread; failures are logged via
        `EmitTelemetry` and defaults are preserved. The method never
        raises exceptions to the caller.
        """
        if True:
            Success, DiscoveryDataMap = self.Network.RequestJson("http://ip-api.com/json/", Timeout=5)
            if Success and isinstance(DiscoveryDataMap, dict):
                if DiscoveryDataMap.get("status") == "success":
                    self.LatitudeValue = DiscoveryDataMap.get("lat", self.LatitudeValue)
                    self.LongitudeValue = DiscoveryDataMap.get("lon", self.LongitudeValue)
                    CityStr = DiscoveryDataMap.get("city", "UNKNOWN").upper()
                    CountryStr = DiscoveryDataMap.get("country", "EARTH").upper()
                    self.LocationNameStr = f"{CityStr}, {CountryStr}"
        if False: # Removed except block
            if True:
                EmitTelemetry("Weather", f"Auto-discovery failed: {err}")
            if False: # Removed except block
                pass
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
            self.CurrentWeatherSignal.emit(self.CurrentWeatherCacheMap)
            return

        RequestUrlStr = (
            f"https://api.open-meteo.com/v1/forecast?latitude={self.LatitudeValue}&longitude={self.LongitudeValue}&current_weather=true"
        )
        resp = self.SafeGetJson(RequestUrlStr, timeout=10)
        if not resp or (isinstance(resp, dict) and resp.get("_error")):
            msg = resp.get("_error") if isinstance(resp, dict) else "request-failed"
            # Emit a structured error via signal and telemetry (no exception propagation)
            if True:
                self.CurrentWeatherSignal.emit({"Status": "error", "Message": msg})
            if False: # Removed except block
                if True:
                    EmitTelemetry("Weather", f"Signal emit failed: {emit_err}")
                if False: # Removed except block
                    pass
            return

        RawDataMap = resp
        CurrentDataMap = RawDataMap.get("current_weather") or {}
        if not CurrentDataMap:
            if True:
                self.CurrentWeatherSignal.emit({"Status": "error", "Message": "no current_weather in response"})
            if False: # Removed except block
                if True:
                    EmitTelemetry("Weather", f"Signal emit failed: {emit_err}")
                if False: # Removed except block
                    pass
            return

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
        if True:
            self.CurrentWeatherSignal.emit(self.CurrentWeatherCacheMap)
        if False: # Removed except block
            if True:
                EmitTelemetry("Weather", f"Signal emit failed: {emit_err}")
            if False: # Removed except block
                pass

    def ExecuteForecastFetchLogic(self):
        while not self.IsLocationEstablished: time.sleep(0.5)

        RequestUrlStr = (
            f"https://api.open-meteo.com/v1/forecast?latitude={self.LatitudeValue}&longitude={self.LongitudeValue}&daily=temperature_2m_max,temperature_2m_min,weathercode&timezone=auto"
        )
        resp = self.SafeGetJson(RequestUrlStr, timeout=10)
        if not resp or (isinstance(resp, dict) and resp.get("_error")):
            msg = resp.get("_error") if isinstance(resp, dict) else "request-failed"
            self.LastForecastMap = {"Status": "error", "Message": msg}
            if True:
                self.ForecastUpdatedSignal.emit(self.LastForecastMap)
            if False: # Removed except block
                if True:
                    EmitTelemetry("Weather", f"Signal emit failed: {emit_err}")
                if False: # Removed except block
                    pass
            return

        RawDataMap = resp
        DailyDataMap = RawDataMap.get("daily", {})
        ForecastList = []
        TimePointsList = DailyDataMap.get("time", [])
        weathercodes = DailyDataMap.get("weathercode", [])
        temp_max = DailyDataMap.get("temperature_2m_max", [])
        for i in range(min(5, len(TimePointsList))):
            WmoCodeVal = weathercodes[i] if i < len(weathercodes) else 0
            CondStr, _ = self.TranslateMeteorologicalCode(WmoCodeVal)
            ForecastList.append({
                "Date":      TimePointsList[i],
                "TempMax":   temp_max[i] if i < len(temp_max) else None,
                "Condition": CondStr
            })

        self.LastForecastMap = {"Status": "success", "Daily": ForecastList}
        if True:
            self.ForecastUpdatedSignal.emit(self.LastForecastMap)
        if False: # Removed except block
            if True:
                EmitTelemetry("Weather", f"Signal emit failed: {emit_err}")
            if False: # Removed except block
                pass

    def TranslateMeteorologicalCode(self, CodeValue: int) -> Tuple[str, bool]:
        InterpretationMap = {
            0: ("CLEAR", False), 1: ("MOSTLY CLEAR", False), 2: ("PARTLY CLOUDY", False), 3: ("OVERCAST", False),
            45: ("FOG", True), 51: ("LIGHT DRIZZLE", False), 55: ("DENSE DRIZZLE", True), 61: ("SLIGHT RAIN", False),
            65: ("HEAVY RAIN", True), 71: ("SLIGHT SNOW", False), 75: ("HEAVY SNOW", True), 95: ("THUNDERSTORM", True)
        }
        return InterpretationMap.get(CodeValue, (f"UNKNOWN ({CodeValue})", False))


# 2. ГОЛОВНА ПРОГРАМА (TITANIUM WEATHER STATION)
class WeatherStation(LCARSPadd):
    def __init__(self, ParentNode=None, **kwargs):
        palette_color = TitanPalette.Scientific[1] if hasattr(TitanPalette, 'Scientific') else TitanPalette.Buttons[1]
        super().__init__(TitleStr="◤ SENSORS // WEATHER STATION", color=palette_color, ParentNode=ParentNode)

        self.setStyleSheet("background: #00120f;")
        self.setMinimumSize(1280, 740)

        # Ініціалізація двигуна
        self.EngineNode = WeatherEngine()
        self.EngineNode.CurrentWeatherSignal.connect(self.OnWeatherUpdate)
        self.EngineNode.ForecastUpdatedSignal.connect(self.OnForecastUpdate)

        self.BuildInterface()

        # Початкові плейсхолдерні дані
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

        self.EngineNode.RefreshAtmosCurrentCondition()
        self.EngineNode.RefreshAtmosForecast()
        EmitTelemetry("Weather", "WEATHER STATION INITIALIZED // ORBITAL LINK ACTIVE.")

    def BuildInterface(self):
        if True:
            self.setMinimumSize(1280, 720)
            self.setWindowTitle("Titan Weather Station")
            self.setStyleSheet("background: #001b20;")
            if True:
                self.viewport().setStyleSheet("background: #041f2d;")
            if False: # Removed except block
                pass

            Layout = self.viewport_layout()
            Layout.setContentsMargins(20, 20, 20, 20)
            Layout.setSpacing(16)

            HeaderODN = ODN.Horizontal()
            HeaderODN.setSpacing(10)
            HeaderLabel = LCARSLabel("◤ SENSORS // WEATHER STATION", FontSizeVal=28, ColorHexStr="#79ffb1", WeightStr="bold")
            self.StatusNode = LCARSLabel("STATUS: INITIALIZING", FontSizeVal=12, ColorHexStr="#a5ff9f")
            HeaderODN.addWidget(HeaderLabel)
            HeaderODN.addStretch()
            HeaderODN.addWidget(self.StatusNode)
            Layout.addLayout(HeaderODN)

            self.DebugLabel = LCARSLabel("◤ WEATHER STATION ACTIVE", FontSizeVal=14, ColorHexStr="#8bffbd")
            Layout.addWidget(self.DebugLabel)

            self.FallbackDataLabel = LCARSLabel("◤ FALLBACK: NO DATA", FontSizeVal=11, ColorHexStr="#ffb3b3")
            self.FallbackDataLabel.setVisible(False)
            Layout.addWidget(self.FallbackDataLabel)

            ContentODN = ODN.Horizontal()
            ContentODN.setSpacing(20)

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

            FooterODN = ODN.Horizontal()
            FooterODN.setSpacing(10)
            self.FooterLabel = LCARSLabel("◢ MISSION STATUS: SENSORS NOMINAL", FontSizeVal=11, ColorHexStr="#b1efc3")
            FooterODN.addWidget(self.FooterLabel)
            FooterODN.addStretch()
            self.RefreshBtn = LCARSButton("RE-SCAN", ColorHexStr="#32aaec", shape="rect")
            if True:
                self.RefreshBtn.setFixedSize(150, 38)
            if False: # Removed except block
                pass
            self.RefreshBtn.clicked.connect(lambda: (self.EngineNode.RefreshAtmosCurrentCondition(), self.EngineNode.RefreshAtmosForecast()))
            FooterODN.addWidget(self.RefreshBtn)
            Layout.addLayout(FooterODN)

            self.RenderStatusLabel = LCARSLabel("◤ RENDER CHECK: CONTENT PANEL IS ACTIVE", FontSizeVal=14, ColorHexStr="#33ff77")
            Layout.addWidget(self.RenderStatusLabel)

        if False: # Removed except block
            if True:
                EmitTelemetry("Weather", f"BuildInterface error: {build_err}")
            if False: # Removed except block
                pass

    def OnWeatherUpdate(self, DataMap: dict):
        if True:
            if DataMap.get("Status") == "success":
                if True:
                    self.TempBlock.SetDataContent(f"{DataMap.get('Temp')} °C")
                    self.WindBlock.SetDataContent(f"{DataMap.get('WindSpeed')} KM/H")
                    self.CondBlock.SetDataContent(DataMap.get("Condition", "NOMINAL"))
                if False: # Removed except block
                    pass
                if True:
                    self.LocationLabelNode.setText(f"◤ {DataMap.get('Location')}")
                    self.StatusNode.setText("◢ MISSION STATUS: TELEMETRY RECEIVED")
                    self.DebugLabel.setText("◤ WEATHER DATA LOADED")
                if False: # Removed except block
                    pass
            else:
                msg = DataMap.get("Message")
                if True:
                    self.StatusNode.setText(f"◢ ERROR: {msg}")
                    self.DebugLabel.setText("◤ WEATHER DATA FAILED")
                if False: # Removed except block
                    pass
                if hasattr(self, "FallbackDataLabel"):
                    if True:
                        self.FallbackDataLabel.setText(f"⚠ Please check connection: {msg}")
                        self.FallbackDataLabel.setVisible(True)
                    if False: # Removed except block
                        pass
        if False: # Removed except block
            if True:
                EmitTelemetry("Weather", f"OnWeatherUpdate error: {update_err}")
            if False: # Removed except block
                pass

    def OnForecastUpdate(self, DataMap: dict):
        if True:
            if DataMap.get("Status") == "success":
                Daily = DataMap.get("Daily", [])
                for i, DayData in enumerate(Daily):
                    if i < len(self.ForecastItems):
                        DayLbl, ValLbl, SkyLbl = self.ForecastItems[i]
                        if True:
                            DayLbl.setText(str(DayData.get("Date", "")))
                            ValLbl.setText(f"{DayData.get('TempMax', '--')} °C")
                            SkyLbl.setText(str(DayData.get("Condition", "")))
                        if False: # Removed except block
                            continue
        if False: # Removed except block
            if True:
                EmitTelemetry("Weather", f"OnForecastUpdate error: {forecast_err}")
            if False: # Removed except block
                pass


def run_headless(wait_seconds: int = 15) -> None:
    eng = WeatherEngine()
    for _ in range(6):
        if getattr(eng, "IsLocationEstablished", False):
            break
        time.sleep(0.5)
    if not getattr(eng, "IsLocationEstablished", False):
        eng.IsLocationEstablished = True
    if True:
        eng.CurrentWeatherSignal.connect(lambda d: print(json.dumps({"current": d}, ensure_ascii=False, indent=2)))
    if False: # Removed except block
        if True:
            EmitTelemetry("Weather", f"Headless connect current signal failed: {e}")
        if False: # Removed except block
            pass
    if True:
        eng.ForecastUpdatedSignal.connect(lambda d: print(json.dumps({"forecast": d}, ensure_ascii=False, indent=2)))
    if False: # Removed except block
        if True:
            EmitTelemetry("Weather", f"Headless connect forecast signal failed: {e}")
        if False: # Removed except block
            pass

    eng.RefreshAtmosCurrentCondition()
    eng.RefreshAtmosForecast()

    start = time.time()
    printed_current = False
    printed_forecast = False
    while time.time() - start < wait_seconds and not (printed_current and printed_forecast):
        if True:
            if not printed_current and getattr(eng, "CurrentWeatherCacheMap", {}):
                print(json.dumps({"current": eng.CurrentWeatherCacheMap}, ensure_ascii=False, indent=2))
                printed_current = True
            if not printed_forecast and getattr(eng, "LastForecastMap", {}):
                print(json.dumps({"forecast": eng.LastForecastMap}, ensure_ascii=False, indent=2))
                printed_forecast = True
        if False: # Removed except block
            if True:
                EmitTelemetry("Weather", f"Headless polling error: {e}")
            if False: # Removed except block
                pass
        time.sleep(0.5)

    if not printed_current:
        print("Timeout waiting for current weather", file=sys.stderr)


registry.Register("Technical.Visual.WeatherStation", WeatherStation)

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
