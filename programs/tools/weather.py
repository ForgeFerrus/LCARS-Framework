# ◤ TITANIUM WEATHER MATRIX — LCARS Weather Application
# LCARS Weather Matrix — це високотехнологічний погодний додаток, натхненний естетикою та дизайном інтерфейсів LCARS з всесвіту Star Trek. Цей додаток надає користувачам детальну інформацію про поточні погодні умови, прогноз погоди та метеорологічні дані для різних локацій по всьому світу. Він використовує сучасні API для отримання актуальних даних про погоду та має інтуїтивно зрозумілий інтерфейс, який ідеально підходить для фанатів наукової фантастики та ентузіастів погоди. Weather Matrix пропонує унікальний досвід взаємодії з погодою, поєднуючи функціональність з візуальною привабливістю в стилі LCARS.

import sys
import time
import json
import threading
from pathlib import Path
from typing import Any, Dict, Optional, cast

from urllib.parse import quote
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lcars.base.components import (
    LCARSFrame, LCARSLabel, LCARSButton,
    LCARSDataBlock, LCARSBar, LCARSDivider, LCARSPill,
    LCARSStatBar,
)
from lcars.base.defaults import (
    AlertColor,
    DefaultAccent,
    DefaultBackground,
    DefaultPalette,
    DefaultPrimary,
    DefaultSecondary,
    RandomButtonColor,
)
from lcars.base.interface import LCARSPadd
from lcars.base.types import Directive, LineEdit, ScrollArea, Application, BoxLayout, Primitives, Qt
from programs.utilities.chronometer import ChronometerSubsystem

# 
def _get_layout_class(name):
    return getattr(Primitives, name, None) or getattr(Primitives, name.rstrip("Layout"), None)

#
def _create_layout(name, parent=None):
    Layout = _get_layout_class(name)
    if not Layout or Layout == object:
        class _NoopLayout:
            def __init__(self, _parent=None):
                pass
            def setContentsMargins(self, *args, **kwargs):
                pass
            def setSpacing(self, *args, **kwargs):
                pass
            def addWidget(self, *args, **kwargs):
                pass
            def addLayout(self, *args, **kwargs):
                pass
            def addStretch(self, *args, **kwargs):
                pass
        return _NoopLayout(parent)
    return Layout(parent)

# 
PANEL_BACKGROUND = DefaultBackground
PANEL_EDGE = DefaultSecondary
PANEL_EDGE_SOFT = DefaultPrimary
PANEL_ACCENT = DefaultAccent
TEXT_PRIMARY = DefaultPalette.Panels[2]
TEXT_SECONDARY = DefaultSecondary
BUTTON_PRIMARY = DefaultPrimary
BUTTON_ACTIVE = DefaultSecondary
BUTTON_ACCENT = DefaultAccent
BUTTON_SUCCESS = DefaultPalette.Accent[1]
BUTTON_WARNING = DefaultPalette.YellowAlert[0]
BUTTON_ALERT = AlertColor(1)
BUTTON_GROUPS = {
    "primary": "Buttons",
    "accent": "Accent",
    "success": "Accent",
    "warning": "YellowAlert",
    "alert": "RedAlert",
}
SCROLLBAR_OFF = Qt.ScrollBarPolicy.ScrollBarAlwaysOff
HIDDEN_SCROLL_STYLE = (
    f"background: {PANEL_BACKGROUND}; border: none;"
    "QScrollBar:vertical { width: 0px; background: transparent; }"
    "QScrollBar:horizontal { height: 0px; background: transparent; }"
)

# 
class WeatherEngine:
    def __init__(self):
        self.latitude = 37.7749
        self.longitude = -122.4194
        self.location_name = "SAN FRANCISCO, EARTH"
        self.is_ready = False
        self.last_weather = {}
        self.last_forecast = {}
        self.unit = "metric"
        self.cache_ttl = 600
        self._last_fetch = 0
        self._current_weather_listeners = []
        self._forecast_listeners = []
        self._location_listeners = []
        self._discovery_thread = None

    def start(self):
        if self._discovery_thread is None or not self._discovery_thread.is_alive():
            self._discovery_thread = threading.Thread(target=self._discover_location, daemon=True)
            self._discovery_thread.start()

    def on_current_weather(self, callback):
        self._current_weather_listeners.append(callback)

    def on_forecast_updated(self, callback):
        self._forecast_listeners.append(callback)

    def on_location_resolved(self, callback):
        self._location_listeners.append(callback)

    def _notify_current_weather(self, data):
        for callback in list(self._current_weather_listeners):
            try:
                callback(data)
            except Exception:
                continue

    def _notify_forecast_updated(self, data):
        for callback in list(self._forecast_listeners):
            try:
                callback(data)
            except Exception:
                continue

    def _notify_location_resolved(self, location):
        for callback in list(self._location_listeners):
            try:
                callback(location)
            except Exception:
                continue

    def _http_get_json(self, url: str) -> Optional[dict]:
        try:
            request = Request(url, headers={"User-Agent": "LCARS Weather Matrix/1.0"})
            with urlopen(request, timeout=10) as response:
                code = getattr(response, "status", None) or response.getcode()
                if code != 200:
                    return None
                payload = response.read()
                return json.loads(payload.decode("utf-8"))
        except (HTTPError, URLError, ValueError):
            return None

    def _discover_location(self):
        try:
            data = self._http_get_json("http://ip-api.com/json/")
            if data and data.get("status") == "success":
                self.latitude = data.get("lat", self.latitude)
                self.longitude = data.get("lon", self.longitude)
                city = data.get("city", "UNKNOWN").upper()
                country = data.get("country", "EARTH").upper()
                self.location_name = f"{city}, {country}"
        except Exception:
            pass
        self.is_ready = True
        self._notify_location_resolved(self.location_name)
        self.refresh_weather()
        self.refresh_forecast()

    def refresh_weather(self):
        if not self.is_ready:
            return
        threading.Thread(target=self._fetch_current_weather, daemon=True).start()

    def refresh_forecast(self):
        if not self.is_ready:
            return
        threading.Thread(target=self._fetch_forecast, daemon=True).start()

    def search_location(self, query: str):
        if not query:
            return
        threading.Thread(target=self._resolve_location, args=(query,), daemon=True).start()

    def _resolve_location(self, query: str):
        try:
            encoded_query = quote(query)
            url = f"https://geocoding-api.open-meteo.com/v1/search?name={encoded_query}&count=1"
            data = self._http_get_json(url)
            if data:
                results = data.get("results", [])
                if results:
                    top = results[0]
                    self.latitude = top.get("latitude", self.latitude)
                    self.longitude = top.get("longitude", self.longitude)
                    name = top.get("name", query).upper()
                    country = top.get("country", "UNKNOWN").upper()
                    self.location_name = f"{name}, {country}"
                    self._notify_location_resolved(self.location_name)
                    self.refresh_weather()
                    self.refresh_forecast()
                    return
        except Exception:
            pass
        self._notify_location_resolved("LOCATION NOT FOUND")

    def _fetch_current_weather(self):
        if time.time() - self._last_fetch < self.cache_ttl and self.last_weather:
            self._notify_current_weather(self.last_weather)
            return
        try:
            url = (
                f"https://api.open-meteo.com/v1/forecast?latitude={self.latitude}&longitude={self.longitude}"
                f"&current_weather=true&hourly=relativehumidity_2m,pressure_msl,dewpoint_2m&timezone=auto"
                f"&temperature_unit={self._open_meteo_temperature_unit()}&windspeed_unit={self._open_meteo_windspeed_unit()}"
            )
            payload = self._http_get_json(url)
            if payload:
                data = payload.get("current_weather", {})
                hourly = payload.get("hourly", {})
                humidity = hourly.get("relativehumidity_2m", [None])[0] if hourly else None
                pressure = hourly.get("pressure_msl", [None])[0] if hourly else None
                dewpoint = hourly.get("dewpoint_2m", [None])[0] if hourly else None
                icon, condition = self._translate_code(data.get("weathercode", 0))
                weather = {
                    "Status": "success",
                    "Temp": data.get("temperature", 0.0),
                    "WindSpeed": data.get("windspeed", 0.0),
                    "WindDirection": data.get("winddirection", 0),
                    "Condition": condition,
                    "Icon": icon,
                    "Humidity": humidity,
                    "Pressure": pressure,
                    "DewPoint": dewpoint,
                    "Location": self.location_name,
                }
                self.last_weather = weather
                self._last_fetch = time.time()
                self._notify_current_weather(weather)
                return
            self._notify_current_weather({"Status": "error", "Message": "NETWORK FAILURE"})
        except Exception as exc:
            self._notify_current_weather({"Status": "error", "Message": str(exc)})

    def _fetch_forecast(self):
        try:
            url = (
                f"https://api.open-meteo.com/v1/forecast?latitude={self.latitude}&longitude={self.longitude}"
                f"&daily=temperature_2m_max,temperature_2m_min,weathercode&timezone=auto&temperature_unit={self._open_meteo_temperature_unit()}"
            )
            payload = self._http_get_json(url)
            if payload:
                daily = payload.get("daily", {})
                dates = daily.get("time", [])
                max_temps = daily.get("temperature_2m_max", [])
                min_temps = daily.get("temperature_2m_min", [])
                codes = daily.get("weathercode", [])
                forecast = {"Status": "success", "Daily": []}
                for i in range(min(5, len(dates))):
                    code = codes[i] if i < len(codes) else 0
                    icon, _ = self._translate_code(code)
                    forecast["Daily"].append({
                        "Date": dates[i],
                        "TempMax": max_temps[i] if i < len(max_temps) else 0,
                        "TempMin": min_temps[i] if i < len(min_temps) else 0,
                        "Condition": self._translate_code(code)[0],
                        "Icon": icon,
                        "WeatherCode": code,
                    })
                self.last_forecast = forecast
                self._notify_forecast_updated(forecast)
                return
            self._notify_forecast_updated({"Status": "error", "Message": "NETWORK FAILURE"})
        except Exception as exc:
            self._notify_forecast_updated({"Status": "error", "Message": str(exc)})

    def _translate_code(self, code: int) -> tuple[str, str]:
        mapping = {
            0: ("CLEAR", "☀"), 1: ("MAINLY CLEAR", "🌤"), 2: ("PARTLY CLOUDY", "⛅"),
            3: ("OVERCAST", "☁"), 45: ("FOG", "🌫"), 51: ("LIGHT DRIZZLE", "🌦"),
            55: ("DRIZZLE", "🌧"), 61: ("RAIN", "🌧"), 65: ("HEAVY RAIN", "⛈"),
            71: ("SNOW", "🌨"), 75: ("HEAVY SNOW", "❄"), 95: ("STORM", "🌩"),
        }
        return mapping.get(code, (f"UNKNOWN {code}", "❔"))

    def _open_meteo_temperature_unit(self) -> str:
        return "fahrenheit" if self.unit == "imperial" else "celsius"

    def _open_meteo_windspeed_unit(self) -> str:
        return "mph" if self.unit == "imperial" else "kmh"


class WeatherStation(LCARSPadd):
    def __init__(self):
        super().__init__(Title="◤ TITANIUM WEATHER MATRIX", Color=DefaultPrimary)
        self.setMinimumSize(640, 480)
        self.resize(1040, 760)
        self.setStyleSheet("background: transparent;")
        self.Viewport.setStyleSheet(f"background-color: {PANEL_BACKGROUND}; border-radius: 18px;")
        self._is_fullscreen = False
        self._shutting_down = False
        self.alert_mode = "normal"
        self.dynamic_buttons = []
        
        self.current_view = "overview"
        self.locations = ["SAN FRANCISCO", "WASHINGTON DC", "PRAGUE", "LONDON"]
        self.current_location_idx = 0
        self.hourly_data = []

        self.engine = WeatherEngine()
        self.engine.on_current_weather(self._on_weather_update)
        self.engine.on_forecast_updated(self._on_forecast_update)
        self.engine.on_location_resolved(self._on_location_resolved)

        app_instance = getattr(cast(Any, Application), "instance", lambda: None)()
        about_to_quit = getattr(app_instance, "aboutToQuit", None)
        if about_to_quit is not None and hasattr(about_to_quit, "connect"):
            about_to_quit.connect(self._prepare_shutdown)

        self._build_ui()
        self._sync_alert_state()
        self._setup_chronometer()
        self._setup_palette_cycle()
        self.engine.start()
        self.engine.refresh_weather()
        self.engine.refresh_forecast()

    def _panel_style(self, weight: int = 2) -> str:
        return f"background-color: {PANEL_BACKGROUND}; border: {weight}px solid {PANEL_EDGE}; border-radius: 16px;"

    def _button_color(self, role: str) -> str:
        return RandomButtonColor(self._button_group(role))

    def _button_group(self, role: str) -> str:
        if self.alert_mode == "yellow":
            return "YellowAlert"
        if self.alert_mode == "red":
            return "RedAlert"
        return BUTTON_GROUPS.get(role, "Buttons")

    def _refresh_button_color(self, button: LCARSButton) -> None:
        button.SetColor(self._button_color(getattr(button, "ToneRole", "primary")))

    def _refresh_dynamic_palette(self) -> None:
        for button in list(self.dynamic_buttons):
            self._refresh_button_color(button)

    def _alert_button_role(self) -> str:
        return "alert" if self.alert_mode == "red" else "warning"

    def _alert_button_text(self) -> str:
        labels = {
            "normal": "ALERT: OFF",
            "yellow": "ALERT: YELLOW",
            "red": "ALERT: RED",
        }
        return labels.get(self.alert_mode, "ALERT: OFF")

    def _sync_alert_state(self) -> None:
        if hasattr(self, "alert_button"):
            self.alert_button.SetText(self._alert_button_text())
            self._apply_button_state(self.alert_button, self._alert_button_role(), self.alert_mode != "normal")
        self._refresh_dynamic_palette()
        alert_status = self._alert_button_text()
        if hasattr(self, "status_label"):
            self.status_label.SetText(alert_status)
        if hasattr(self, "footer_label"):
            self.footer_label.SetText(f"PALETTE MODE: {alert_status}")

    def _cycle_alert_mode(self) -> None:
        modes = ["normal", "yellow", "red"]
        next_index = (modes.index(self.alert_mode) + 1) % len(modes)
        self.alert_mode = modes[next_index]
        self._sync_alert_state()

    def _setup_palette_cycle(self) -> None:
        TimerClass = getattr(Primitives, "Timer", None)
        self._palette_timer = None
        if TimerClass and TimerClass != object:
            self._palette_timer = TimerClass(self)
            timeout = getattr(self._palette_timer, "timeout", None)
            if timeout is not None and hasattr(timeout, "connect"):
                timeout.connect(self._advance_palette_cycle)
                if hasattr(self._palette_timer, "start"):
                    self._palette_timer.start(1400)

    def _advance_palette_cycle(self) -> None:
        if self._shutting_down:
            return
        self._refresh_dynamic_palette()

    def _apply_button_state(self, button: LCARSButton, role: str = "primary", active: bool = False) -> None:
        button.Type = LCARSButton.ROUNDED
        # Базовий тон кнопки задається лише коли змінюється її роль.
        # Активність далі веде сама кнопка через latched/hover/pressed алгоритм.
        if button not in self.dynamic_buttons:
            self.dynamic_buttons.append(button)
        if getattr(button, "ToneRole", None) != role:
            button.ToneRole = role
            self._refresh_button_color(button)
        if hasattr(button, "SetLatched"):
            button.SetLatched(active)

    def _prepare_shutdown(self) -> None:
        self._shutting_down = True

    def _setup_chronometer(self) -> None:
        self._update_chronometer_display()
        TimerClass = getattr(Primitives, "Timer", None)
        self._chronometer_timer = None
        if TimerClass and TimerClass != object:
            self._chronometer_timer = TimerClass(self)
            timeout = getattr(self._chronometer_timer, "timeout", None)
            if timeout is not None and hasattr(timeout, "connect"):
                timeout.connect(self._update_chronometer_display)
                if hasattr(self._chronometer_timer, "start"):
                    self._chronometer_timer.start(1000)

    def _update_chronometer_display(self) -> None:
        value = ChronometerSubsystem.get_stardate()
        self.chrono_label.SetText(f"STARDATE: {value}")

    def _build_location_tabs(self, parent_layout) -> None:
        if getattr(self, "location_tabs_frame", None):
            self.location_tabs_frame.setParent(None)

        tabs_frame = LCARSFrame(self)
        tabs_frame.setStyleSheet(self._panel_style())
        tabs_layout = _create_layout("HBoxLayout", tabs_frame)
        self.location_tabs_layout = tabs_layout
        tabs_layout.setContentsMargins(12, 8, 12, 8)
        tabs_layout.setSpacing(10)

        self.location_buttons = []
        for i, loc in enumerate(self.locations):
            btn = LCARSButton(loc[:12], Type=LCARSButton.ROUNDED, Parent=tabs_frame)
            self._apply_button_state(btn, "accent", i == self.current_location_idx)
            btn.Clicked = lambda idx=i: self._switch_location(idx)
            self.location_buttons.append(btn)
            tabs_layout.addWidget(btn)

        tabs_layout.addStretch()
        add_btn = LCARSButton("+", Type=LCARSButton.ROUNDED, Parent=tabs_frame)
        self._apply_button_state(add_btn, "success")
        add_btn.Clicked = self._add_location
        tabs_layout.addWidget(add_btn)

        self.location_tabs_frame = tabs_frame
        if hasattr(parent_layout, "insertWidget"):
            parent_layout.insertWidget(0, tabs_frame)
        else:
            parent_layout.addWidget(tabs_frame)

    def _switch_location(self, idx: int) -> None:
        self.current_location_idx = idx
        for i, btn in enumerate(self.location_buttons):
            self._apply_button_state(btn, "accent", i == idx)
        self.status_label.SetText(f"LOCATION: {self.locations[idx]}")
        self.engine.search_location(self.locations[idx])

    def _add_location(self) -> None:
        query = self.search_input.text().strip()
        if query:
            self.locations.append(query.upper())
            self.current_location_idx = len(self.locations) - 1
            layout = getattr(self.Viewport, "layout", lambda: None)()
            if layout is not None:
                self._build_location_tabs(layout)
            self.engine.search_location(query)

    def _build_ui(self) -> None:
        central = self.Viewport
        existing_layout = getattr(central, "layout", lambda: None)()
        if existing_layout is not None:
            main_layout = existing_layout
        else:
            main_layout = _create_layout("VBoxLayout", central)
            getattr(central, "setLayout", lambda layout: None)(main_layout)
        self._build_location_tabs(main_layout)
        main_layout.setContentsMargins(18, 18, 18, 18)
        main_layout.setSpacing(14)

        scroll_factory = cast(Any, ScrollArea)
        self.body_scroll = scroll_factory(central)
        self.body_scroll.setWidgetResizable(True)
        self.body_scroll.setHorizontalScrollBarPolicy(SCROLLBAR_OFF)
        self.body_scroll.setVerticalScrollBarPolicy(SCROLLBAR_OFF)
        self.body_scroll.setStyleSheet(HIDDEN_SCROLL_STYLE)

        body_host = LCARSFrame(self.body_scroll)
        body_host.setStyleSheet("background: transparent;")
        body_layout = _create_layout("VBoxLayout", body_host)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(14)
        self.body_scroll.setWidget(body_host)
        main_layout.addWidget(self.body_scroll, 1)

        header = LCARSFrame(central)
        header.setStyleSheet(self._panel_style())
        header_layout = _create_layout("HBoxLayout", header)
        self.header_layout = header_layout
        header_layout.setContentsMargins(16, 14, 16, 14)
        header_layout.setSpacing(10)

        title = LCARSLabel("◤ TITANIUM WEATHER MATRIX", Color=TEXT_PRIMARY, FontSize=24, Parent=header)
        header_layout.addWidget(title)

        self.chrono_label = LCARSLabel("STARDATE: --", Color=TEXT_SECONDARY, FontSize=12, Parent=header)
        header_layout.addWidget(self.chrono_label)

        self.status_label = LCARSLabel("SYSTEM STATUS: SYNCHRONIZING WEATHER GRID", Color=TEXT_SECONDARY, FontSize=12, Parent=header)
        header_layout.addWidget(self.status_label)
        header_layout.addStretch()

        refresh_button = LCARSButton("REFRESH", Type=LCARSButton.ROUNDED, Parent=header)
        self._apply_button_state(refresh_button, "primary")
        refresh_button.Clicked = self._manual_refresh
        header_layout.addWidget(refresh_button)

        body_layout.addWidget(header)

        info_bar = LCARSFrame(central)
        info_bar.setStyleSheet(self._panel_style(1))
        info_layout = _create_layout("HBoxLayout", info_bar)
        self.info_layout = info_layout
        info_layout.setContentsMargins(14, 10, 14, 10)
        info_layout.setSpacing(10)

        info_pill = LCARSPill("PORTABLE PADD", Color=BUTTON_ACTIVE, Parent=info_bar)
        info_layout.addWidget(info_pill)

        info_label = LCARSLabel("WEATHER COMMAND CENTER", Color=TEXT_PRIMARY, FontSize=12, Parent=info_bar)
        info_layout.addWidget(info_label)

        self.alert_button = LCARSButton("ALERT: OFF", Type=LCARSButton.ROUNDED, Parent=info_bar)
        self._apply_button_state(self.alert_button, "warning")
        self.alert_button.Clicked = self._cycle_alert_mode
        info_layout.addWidget(self.alert_button)

        self.fullscreen_button = LCARSButton("FULLSCREEN", Type=LCARSButton.ROUNDED, Parent=info_bar)
        self._apply_button_state(self.fullscreen_button, "accent")
        self.fullscreen_button.Clicked = self._toggle_fullscreen
        info_layout.addWidget(self.fullscreen_button)

        info_layout.addStretch()

        exit_button = LCARSButton("EXIT", Type=LCARSButton.ROUNDED, Parent=info_bar)
        self._apply_button_state(exit_button, "alert")
        exit_button.Clicked = self.close
        info_layout.addWidget(exit_button)

        body_layout.addWidget(info_bar)

        control_row = LCARSFrame(central)
        control_row.setStyleSheet(self._panel_style())
        ctrl_layout = _create_layout("HBoxLayout", control_row)
        self.control_layout = ctrl_layout
        ctrl_layout.setContentsMargins(14, 12, 14, 12)
        ctrl_layout.setSpacing(12)

        self.search_input = cast(Any, LineEdit())
        self.search_input.setPlaceholderText("SEARCH LOCATION OR CITY")
        self.search_input.setStyleSheet(f"background: {PANEL_BACKGROUND}; color: {TEXT_PRIMARY}; border: 1px solid {PANEL_EDGE}; border-radius: 8px; padding: 10px;")
        self.search_input.returnPressed.connect(self._search_location)
        ctrl_layout.addWidget(self.search_input, 3)

        search_button = LCARSButton("SEARCH", Type=LCARSButton.ROUNDED, Parent=control_row)
        self._apply_button_state(search_button, "primary")
        search_button.Clicked = self._search_location
        ctrl_layout.addWidget(search_button)

        refresh_button = LCARSButton("REFRESH", Type=LCARSButton.ROUNDED, Parent=control_row)
        self._apply_button_state(refresh_button, "success")
        refresh_button.Clicked = self._manual_refresh
        ctrl_layout.addWidget(refresh_button)

        self.units_button = LCARSButton("METRIC", Type=LCARSButton.ROUNDED, Parent=control_row)
        self._apply_button_state(self.units_button, "warning")
        self.units_button.Clicked = self._toggle_units
        ctrl_layout.addWidget(self.units_button)

        body_layout.addWidget(control_row)
        self._build_content_area(body_layout)
        self._build_footer(body_layout)


    def _build_content_area(self, parent_layout) -> None:
        content_frame = LCARSFrame(self)
        content_frame.setStyleSheet(self._panel_style())
        content_layout = _create_layout("HBoxLayout", content_frame)
        content_layout.setContentsMargins(18, 18, 18, 18)
        content_layout.setSpacing(20)
        self.content_layout = content_layout

        self._build_side_panel(content_layout)

        scroll_factory = cast(Any, ScrollArea)
        self.main_scroll = scroll_factory(content_frame)
        self.main_scroll.setWidgetResizable(True)
        self.main_scroll.setHorizontalScrollBarPolicy(SCROLLBAR_OFF)
        self.main_scroll.setVerticalScrollBarPolicy(SCROLLBAR_OFF)
        self.main_scroll.setStyleSheet(HIDDEN_SCROLL_STYLE)

        main_panel = LCARSFrame(self.main_scroll)
        main_panel.setStyleSheet("background-color: transparent;")
        self.main_panel = main_panel
        main_panel_layout = _create_layout("VBoxLayout", main_panel)
        main_panel_layout.setContentsMargins(0, 0, 0, 0)
        main_panel_layout.setSpacing(18)

        # Головна зона більше не є довгою колонкою з усіх блоків одразу.
        # Тут живуть окремі сторінки, які перемикаються кнопками ліворуч.
        self.view_pages = {}
        self._build_overview_page(main_panel_layout)
        self._build_forecast_page(main_panel_layout)
        self._build_hourly_page(main_panel_layout)
        self._build_metrics_page(main_panel_layout)
        self._build_map_page(main_panel_layout)
        self._refresh_view_mode()

        self.main_scroll.setWidget(main_panel)
        content_layout.addWidget(self.main_scroll, 3)
        parent_layout.addWidget(content_frame, 1)
        self._update_responsive_layout()

    def _build_page_shell(self, parent_layout, view_key: str):
        page = LCARSFrame(self.main_panel)
        page.setStyleSheet("background: transparent;")
        page_layout = _create_layout("VBoxLayout", page)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.setSpacing(16)
        self.view_pages[view_key] = page
        parent_layout.addWidget(page, 1)
        return page_layout

    def _build_overview_page(self, parent_layout) -> None:
        overview_layout = self._build_page_shell(parent_layout, "overview")
        self._build_current_panel(overview_layout)

    def _build_forecast_page(self, parent_layout) -> None:
        forecast_layout = self._build_page_shell(parent_layout, "forecast")
        self._build_forecast_panel(forecast_layout)

    def _build_hourly_page(self, parent_layout) -> None:
        hourly_layout = self._build_page_shell(parent_layout, "hourly")
        self._build_hourly_panel(hourly_layout)

    def _build_metrics_page(self, parent_layout) -> None:
        metrics_layout = self._build_page_shell(parent_layout, "metrics")
        self._build_metrics_grid(metrics_layout)

    def _build_map_page(self, parent_layout) -> None:
        map_layout = self._build_page_shell(parent_layout, "map")
        self._build_map_panel(map_layout)

    def _update_responsive_layout(self) -> None:
        layout = getattr(self, "content_layout", None)
        if layout is None or not hasattr(layout, "setDirection"):
            return
        available_width = max(getattr(self.Viewport, "width", lambda: 0)(), getattr(self, "width", lambda: 0)())
        narrow_layout = available_width < 980

        # На вузькому екрані PADD складає рядки у стеки, щоб нічого не ламалось і не вилазило за межі.
        header_direction = getattr(getattr(self, "header_layout", None), "setDirection", None)
        if callable(header_direction):
            header_direction(BoxLayout.Direction.TopToBottom if available_width < 900 else BoxLayout.Direction.LeftToRight)
        info_direction = getattr(getattr(self, "info_layout", None), "setDirection", None)
        if callable(info_direction):
            info_direction(BoxLayout.Direction.TopToBottom if available_width < 820 else BoxLayout.Direction.LeftToRight)
        control_direction = getattr(getattr(self, "control_layout", None), "setDirection", None)
        if callable(control_direction):
            control_direction(BoxLayout.Direction.TopToBottom if available_width < 900 else BoxLayout.Direction.LeftToRight)
        tabs_direction = getattr(getattr(self, "location_tabs_layout", None), "setDirection", None)
        if callable(tabs_direction):
            tabs_direction(BoxLayout.Direction.TopToBottom if available_width < 760 else BoxLayout.Direction.LeftToRight)

        if narrow_layout:
            layout.setDirection(BoxLayout.Direction.TopToBottom)
            getattr(self.side_panel, "setMaximumHeight", lambda *a: None)(340)
            getattr(self.side_panel, "setMinimumWidth", lambda *a: None)(0)
            getattr(self.side_panel, "setMaximumWidth", lambda *a: None)(16777215)
        else:
            layout.setDirection(BoxLayout.Direction.LeftToRight)
            getattr(self.side_panel, "setMinimumWidth", lambda *a: None)(210)
            getattr(self.side_panel, "setMaximumWidth", lambda *a: None)(280)
            getattr(self.side_panel, "setMaximumHeight", lambda *a: None)(16777215)

    def _build_side_panel(self, parent_layout) -> None:
        side_panel = LCARSFrame(self)
        side_panel.setStyleSheet(self._panel_style())
        self.side_panel = side_panel
        side_panel.setMinimumWidth(210)
        side_layout = _create_layout("VBoxLayout", side_panel)
        side_layout.setContentsMargins(18, 18, 18, 18)
        side_layout.setSpacing(14)

        side_layout.addWidget(LCARSPill("SYSTEM OPS", Color=BUTTON_ACTIVE, Parent=side_panel))
        side_layout.addWidget(LCARSLabel("QUICK ACCESS MODULE", Color=TEXT_PRIMARY, FontSize=11, Parent=side_panel))

        quick_group = LCARSFrame(side_panel)
        quick_group.setStyleSheet("background: transparent;")
        quick_layout = _create_layout("VBoxLayout", quick_group)
        quick_layout.setContentsMargins(0, 0, 0, 0)
        quick_layout.setSpacing(10)

        nav_search = LCARSButton("SEARCH", Type=LCARSButton.ROUNDED, Parent=quick_group)
        self._apply_button_state(nav_search, "primary")
        nav_search.Clicked = self._search_location
        quick_layout.addWidget(nav_search)

        nav_refresh = LCARSButton("SYNC", Type=LCARSButton.ROUNDED, Parent=quick_group)
        self._apply_button_state(nav_refresh, "success")
        nav_refresh.Clicked = self._manual_refresh
        quick_layout.addWidget(nav_refresh)

        nav_units = LCARSButton("UNITS", Type=LCARSButton.ROUNDED, Parent=quick_group)
        self._apply_button_state(nav_units, "warning")
        nav_units.Clicked = self._toggle_units
        quick_layout.addWidget(nav_units)

        nav_map = LCARSButton("MAP", Type=LCARSButton.ROUNDED, Parent=quick_group)
        self._apply_button_state(nav_map, "accent")
        nav_map.Clicked = lambda: self._switch_view("map")
        quick_layout.addWidget(nav_map)

        side_layout.addWidget(quick_group)
        side_layout.addWidget(LCARSDivider("VIEW MODES", Color=PANEL_EDGE, Parent=side_panel))

        self.nav_buttons = {}
        self.nav_button_roles = {}
        nav_items = [
            ("overview", "OVERVIEW", "primary"),
            ("forecast", "5-DAY", "accent"),
            ("hourly", "24-HOUR", "warning"),
            ("metrics", "METRICS", "success"),
            ("map", "MAP", "accent"),
        ]
        for key, label, role in nav_items:
            btn = LCARSButton(
                label,
                Type=LCARSButton.ROUNDED,
                Parent=side_panel,
            )
            self._apply_button_state(btn, role, key == self.current_view)
            btn.Clicked = lambda k=key: self._switch_view(k)
            self.nav_buttons[key] = btn
            self.nav_button_roles[key] = role
            side_layout.addWidget(btn)

        side_layout.addWidget(LCARSDivider("SYSTEM TELEMETRY", Color=PANEL_EDGE, Parent=side_panel))

        telemetry_frame = LCARSFrame(side_panel)
        telemetry_frame.setStyleSheet("background: transparent;")
        telemetry_layout = _create_layout("VBoxLayout", telemetry_frame)
        telemetry_layout.setContentsMargins(0, 0, 0, 0)
        telemetry_layout.setSpacing(10)
        telemetry_layout.addWidget(LCARSLabel("SIGNAL STRENGTH", Color=TEXT_PRIMARY, FontSize=10, Parent=telemetry_frame))
        self.signal_bar = LCARSStatBar(Value=78, Color=BUTTON_ACTIVE, Parent=telemetry_frame)
        telemetry_layout.addWidget(self.signal_bar)
        side_layout.addWidget(telemetry_frame)

        self.grid_block = LCARSDataBlock(Label="GRID HEALTH", Value="98 %", Color=BUTTON_ACTIVE, Parent=side_panel)
        self.link_block = LCARSDataBlock(Label="SAT LINK", Value="READY", Color=BUTTON_ACCENT, Parent=side_panel)
        side_layout.addWidget(self.grid_block)
        side_layout.addWidget(self.link_block)

        side_layout.addStretch()
        side_layout.addWidget(LCARSPill("ANALYTICS", Color=BUTTON_WARNING, Parent=side_panel))
        self.mode_label = LCARSLabel("ACTIVE PANEL: OVERVIEW", Color=TEXT_PRIMARY, FontSize=11, Parent=side_panel)
        side_layout.addWidget(self.mode_label)

        parent_layout.addWidget(side_panel, 1)

    def _build_left_nav(self, parent_layout) -> None:
        nav_panel = LCARSFrame(self)
        nav_panel.setStyleSheet("background-color: #061520; border: 2px solid #2bc9a8; border-radius: 16px;")
        nav_layout = _create_layout("VBoxLayout", nav_panel)
        nav_layout.setContentsMargins(14, 14, 14, 14)
        nav_layout.setSpacing(10)

        nav_layout.addWidget(LCARSLabel("◤ NAVIGATION", Color="#5dffe6", FontSize=14, Parent=nav_panel))
        nav_layout.addWidget(LCARSDivider("VIEW MODES", Color="#3cbfa8", Parent=nav_panel))

        self.nav_buttons = {}
        nav_items = [
            ("forecast", "FORECAST", "#4ae8c9"),
            ("maps", "MAPS", "#5a9aff"),
            ("hourly", "HOURLY", "#ff9f5a"),
            ("monthly", "MONTHLY", "#d49eff"),
            ("historical", "HISTORY", "#ffcc66"),
            ("radar", "RADAR", "#66ffaa"),
        ]

        for key, label, color in nav_items:
            btn = LCARSButton(label, Type=LCARSButton.ROUNDED, Parent=nav_panel)
            self._apply_button_state(btn, "accent", key == self.current_view)
            btn.Clicked = lambda k=key: self._switch_view(k)
            self.nav_buttons[key] = btn
            nav_layout.addWidget(btn)

        nav_layout.addStretch()
        nav_layout.addWidget(LCARSDivider("SETTINGS", Color="#3cbfa8", Parent=nav_panel))

        settings_btn = LCARSButton("OPTIONS", Type=LCARSButton.ROUNDED, Parent=nav_panel)
        self._apply_button_state(settings_btn, "warning")
        settings_btn.Clicked = lambda: self.status_label.SetText("SETTINGS: NOT IMPLEMENTED")
        nav_layout.addWidget(settings_btn)

        parent_layout.insertWidget(0, nav_panel)

    def _switch_view(self, view: str) -> None:
        self.current_view = view
        for key, btn in self.nav_buttons.items():
            self._apply_button_state(btn, self.nav_button_roles.get(key, "accent"), key == view)
        self.status_label.SetText(f"VIEW: {view.upper()}")
        self._refresh_view_mode()

    def _refresh_view_mode(self) -> None:
        if not hasattr(self, "view_pages"):
            return
        if self.current_view not in self.view_pages:
            self.current_view = "overview"
        for key, page in self.view_pages.items():
            page.setVisible(key == self.current_view)

        if self.current_view == "map":
            self.map_label.SetText(f"TACTICAL MAP: {self.engine.location_name}")
            self.map_note.SetText("LIVE OVERLAY READY FOR ROUTE AND RADAR DATA")
        else:
            self.map_label.SetText(f"TACTICAL MAP: {self.engine.location_name}")
            self.map_note.SetText("SELECT MAP PANEL TO VIEW THE EXPANDED OVERLAY")

        panel_titles = {
            "overview": "CURRENT CONDITIONS",
            "forecast": "5-DAY FORECAST",
            "hourly": "24-HOUR TRACK",
            "metrics": "DETAILED METRICS",
            "map": "TACTICAL MAP",
        }
        if hasattr(self, "mode_label"):
            self.mode_label.SetText(f"ACTIVE PANEL: {panel_titles.get(self.current_view, self.current_view.upper())}")

    def _build_current_panel(self, parent_layout) -> None:
        panel = LCARSFrame(self)
        panel.setStyleSheet(self._panel_style())
        panel.setMinimumHeight(220)
        self.current_panel = panel
        panel_layout = _create_layout("VBoxLayout", panel)
        panel_layout.setContentsMargins(18, 18, 18, 18)
        panel_layout.setSpacing(14)

        header = LCARSLabel("◤ CURRENT CONDITIONS", Color=TEXT_PRIMARY, FontSize=18, Parent=panel)
        panel_layout.addWidget(header)

        self.loc_label = LCARSLabel("LOCATION: ---", Color=TEXT_SECONDARY, FontSize=14, Parent=panel)
        panel_layout.addWidget(self.loc_label)

        self.temp_label = LCARSLabel("TEMPERATURE: -- °C", Color=BUTTON_WARNING, FontSize=30, Parent=panel)
        panel_layout.addWidget(self.temp_label)

        top_row = _create_layout("HBoxLayout")
        self.weather_icon = LCARSLabel("☀", Color=BUTTON_WARNING, FontSize=40, Parent=panel)
        self.condition_label = LCARSLabel("CONDITION: ---", Color=TEXT_PRIMARY, FontSize=18, Parent=panel)
        top_row.addWidget(self.weather_icon)
        top_row.addWidget(self.condition_label, 2)
        top_row.addStretch()
        panel_layout.addLayout(top_row)

        row = _create_layout("HBoxLayout")
        self.wind_label = LCARSLabel("WIND: -- km/h", Color=TEXT_SECONDARY, FontSize=14, Parent=panel)
        self.status_short = LCARSLabel("STATUS: ---", Color=TEXT_SECONDARY, FontSize=14, Parent=panel)
        row.addWidget(self.wind_label)
        row.addStretch()
        row.addWidget(self.status_short)
        panel_layout.addLayout(row)

        divider = LCARSDivider("TELEMETRY SUMMARY", Color=PANEL_EDGE, Parent=panel)
        panel_layout.addWidget(divider)

        stats = _create_layout("HBoxLayout")
        self.current_blocks = [
            LCARSDataBlock(Label="HUMIDITY", Value="-- %", Color=BUTTON_ACTIVE, Parent=panel),
            LCARSDataBlock(Label="PRESSURE", Value="-- mb", Color=BUTTON_PRIMARY, Parent=panel),
            LCARSDataBlock(Label="DEWPOINT", Value="-- °C", Color=BUTTON_ACCENT, Parent=panel),
            LCARSDataBlock(Label="WIND DIR", Value="---", Color=BUTTON_WARNING, Parent=panel),
        ]
        for block in self.current_blocks:
            stats.addWidget(block, 1)
        panel_layout.addLayout(stats)

        parent_layout.addWidget(panel, 1)

    def _build_hourly_panel(self, parent_layout) -> None:
        panel = LCARSFrame(self)
        panel.setStyleSheet(self._panel_style())
        panel.setMinimumHeight(300)
        self.hourly_panel = panel
        panel_layout = _create_layout("VBoxLayout", panel)
        panel_layout.setContentsMargins(14, 14, 14, 14)
        panel_layout.setSpacing(10)

        header = LCARSLabel("◤ 24-HOUR FORECAST", Color=TEXT_PRIMARY, FontSize=14, Parent=panel)
        panel_layout.addWidget(header)

        scroll_frame = LCARSFrame(panel)
        scroll_frame.setStyleSheet(f"background-color: {PANEL_BACKGROUND}; border-radius: 10px;")
        scroll_layout = _create_layout("VBoxLayout", scroll_frame)
        scroll_layout.setContentsMargins(10, 10, 10, 10)
        scroll_layout.setSpacing(8)

        self.hourly_cards = []
        hours = ["NOW", "+1H", "+2H", "+3H", "+4H", "+5H", "+6H", "+7H", "+8H", "+9H", "+10H", "+11H"]
        for row_index in range(0, len(hours), 4):
            row_layout = _create_layout("HBoxLayout")
            row_layout.setSpacing(8)
            for hour in hours[row_index:row_index + 4]:
                card = LCARSFrame(scroll_frame)
                card.setStyleSheet(f"background-color: {PANEL_BACKGROUND}; border: 1px solid {PANEL_EDGE}; border-radius: 10px;")
                card_layout = _create_layout("VBoxLayout", card)
                card_layout.setContentsMargins(8, 8, 8, 8)
                card_layout.setSpacing(4)

                time_lbl = LCARSLabel(hour, Color=TEXT_SECONDARY, FontSize=10, Parent=card)
                icon_lbl = LCARSLabel("☀", Color=BUTTON_WARNING, FontSize=20, Parent=card)
                temp_lbl = LCARSLabel("--°", Color=TEXT_PRIMARY, FontSize=12, Parent=card)
                card_layout.addWidget(time_lbl)
                card_layout.addWidget(icon_lbl)
                card_layout.addWidget(temp_lbl)

                self.hourly_cards.append((time_lbl, icon_lbl, temp_lbl))
                row_layout.addWidget(card, 1)
            scroll_layout.addLayout(row_layout)

        panel_layout.addWidget(scroll_frame)
        parent_layout.addWidget(panel)

    def _build_metrics_grid(self, parent_layout) -> None:
        panel = LCARSFrame(self)
        panel.setStyleSheet(self._panel_style())
        panel.setMinimumHeight(220)
        self.metrics_panel = panel
        panel_layout = _create_layout("VBoxLayout", panel)
        panel_layout.setContentsMargins(14, 14, 14, 14)
        panel_layout.setSpacing(10)

        header = LCARSLabel("◤ DETAILED METRICS", Color=TEXT_PRIMARY, FontSize=14, Parent=panel)
        panel_layout.addWidget(header)

        grid = _create_layout("HBoxLayout")
        grid.setSpacing(12)

        self.detailed_blocks = {
            "humidity": LCARSDataBlock(Label="HUMIDITY", Value="-- %", Color=BUTTON_ACTIVE, Parent=panel),
            "pressure": LCARSDataBlock(Label="PRESSURE", Value="-- hPa", Color=BUTTON_PRIMARY, Parent=panel),
            "visibility": LCARSDataBlock(Label="VISIBILITY", Value="-- km", Color=BUTTON_ACCENT, Parent=panel),
            "dewpoint": LCARSDataBlock(Label="DEW POINT", Value="-- °C", Color=BUTTON_WARNING, Parent=panel),
            "windspeed": LCARSDataBlock(Label="WIND SPEED", Value="-- km/h", Color=BUTTON_ACTIVE, Parent=panel),
            "winddir": LCARSDataBlock(Label="WIND DIR", Value="---", Color=BUTTON_PRIMARY, Parent=panel),
            "uvindex": LCARSDataBlock(Label="UV INDEX", Value="--", Color=BUTTON_WARNING, Parent=panel),
            "cloudcover": LCARSDataBlock(Label="CLOUD COVER", Value="-- %", Color=BUTTON_ACCENT, Parent=panel),
        }

        left_col = _create_layout("VBoxLayout")
        left_col.setSpacing(8)
        left_col.addWidget(self.detailed_blocks["humidity"])
        left_col.addWidget(self.detailed_blocks["pressure"])
        left_col.addWidget(self.detailed_blocks["visibility"])
        left_col.addWidget(self.detailed_blocks["dewpoint"])

        right_col = _create_layout("VBoxLayout")
        right_col.setSpacing(8)
        right_col.addWidget(self.detailed_blocks["windspeed"])
        right_col.addWidget(self.detailed_blocks["winddir"])
        right_col.addWidget(self.detailed_blocks["uvindex"])
        right_col.addWidget(self.detailed_blocks["cloudcover"])

        grid.addLayout(left_col, 1)
        grid.addLayout(right_col, 1)
        panel_layout.addLayout(grid)
        parent_layout.addWidget(panel, 1)

    def _build_forecast_panel(self, parent_layout) -> None:
        panel = LCARSFrame(self)
        panel.setStyleSheet(self._panel_style())
        panel.setMinimumHeight(260)
        self.forecast_panel = panel
        panel_layout = _create_layout("VBoxLayout", panel)
        panel_layout.setContentsMargins(18, 18, 18, 18)
        panel_layout.setSpacing(16)

        header = LCARSLabel("◤ 5-DAY WEATHER FORECAST", Color=TEXT_PRIMARY, FontSize=18, Parent=panel)
        panel_layout.addWidget(header)

        self.forecast_cards = []
        for i in range(5):
            card = LCARSFrame(panel)
            card.setStyleSheet(f"background-color: {PANEL_BACKGROUND}; border: 1px solid {PANEL_EDGE}; border-radius: 12px;")
            card_layout = _create_layout("HBoxLayout", card)
            card_layout.setContentsMargins(12, 10, 12, 10)
            card_layout.setSpacing(14)

            date_label = LCARSLabel("---", Color=TEXT_SECONDARY, FontSize=14, Parent=card)
            temp_label = LCARSLabel("-- °C", Color=BUTTON_WARNING, FontSize=14, Parent=card)
            cond_label = LCARSLabel("---", Color=TEXT_PRIMARY, FontSize=14, Parent=card)
            card_layout.addWidget(date_label, 2)
            card_layout.addWidget(temp_label, 1)
            card_layout.addWidget(cond_label, 2)

            self.forecast_cards.append((date_label, temp_label, cond_label))
            panel_layout.addWidget(card)

        parent_layout.addWidget(panel, 1)

    def _build_map_panel(self, parent_layout) -> None:
        panel = LCARSFrame(self)
        panel.setStyleSheet(self._panel_style())
        panel.setMinimumHeight(320)
        self.map_panel = panel
        panel_layout = _create_layout("VBoxLayout", panel)
        panel_layout.setContentsMargins(18, 18, 18, 18)
        panel_layout.setSpacing(16)

        header = LCARSLabel("◤ TACTICAL MAP", Color=TEXT_PRIMARY, FontSize=18, Parent=panel)
        panel_layout.addWidget(header)

        self.map_label = LCARSLabel("TACTICAL MAP: ---", Color=BUTTON_ACTIVE, FontSize=22, Parent=panel)
        panel_layout.addWidget(self.map_label)

        self.map_note = LCARSLabel("SELECT MAP PANEL TO VIEW THE EXPANDED OVERLAY", Color=TEXT_SECONDARY, FontSize=12, Parent=panel)
        panel_layout.addWidget(self.map_note)

        panel_layout.addWidget(LCARSBar(Color=BUTTON_ACCENT, Type=LCARSBar.DOUBLE, Parent=panel))

        status_row = _create_layout("HBoxLayout")
        status_row.setSpacing(12)
        self.map_range_block = LCARSDataBlock(Label="SCAN RANGE", Value="LOCAL", Color=BUTTON_ACCENT, Parent=panel)
        self.map_overlay_block = LCARSDataBlock(Label="OVERLAY", Value="LIVE", Color=BUTTON_WARNING, Parent=panel)
        self.map_lock_block = LCARSDataBlock(Label="TARGET LOCK", Value="READY", Color=BUTTON_ACTIVE, Parent=panel)
        status_row.addWidget(self.map_range_block, 1)
        status_row.addWidget(self.map_overlay_block, 1)
        status_row.addWidget(self.map_lock_block, 1)
        panel_layout.addLayout(status_row)

        canvas = LCARSFrame(panel)
        canvas.setStyleSheet(f"background-color: {PANEL_BACKGROUND}; border: 1px solid {PANEL_EDGE}; border-radius: 14px;")
        canvas_layout = _create_layout("VBoxLayout", canvas)
        canvas_layout.setContentsMargins(18, 18, 18, 18)
        canvas_layout.setSpacing(12)
        canvas_layout.addWidget(LCARSLabel("ROUTE / RADAR / PRECIPITATION LAYER", Color=TEXT_PRIMARY, FontSize=14, Parent=canvas))
        canvas_layout.addWidget(LCARSLabel("Ця панель відкрита окремо, щоб карта не стискала прогноз та телеметрію на інших екранах.", Color=TEXT_SECONDARY, FontSize=11, Parent=canvas))
        panel_layout.addWidget(canvas, 1)

        parent_layout.addWidget(panel, 1)

    def _build_footer(self, parent_layout) -> None:
        footer = LCARSFrame(self)
        footer.setStyleSheet(self._panel_style())
        footer_layout = _create_layout("HBoxLayout", footer)
        footer_layout.setContentsMargins(16, 12, 16, 12)

        self.footer_label = LCARSLabel("LIVE MATRIX: WEATHER STREAM ACTIVE", Color=TEXT_SECONDARY, FontSize=12, Parent=footer)
        footer_layout.addWidget(self.footer_label)
        footer_layout.addStretch()

        self.toggle_button = LCARSButton("SWITCH UNITS", Type=LCARSButton.ROUNDED, Parent=footer)
        self._apply_button_state(self.toggle_button, "warning")
        self.toggle_button.Clicked = self._toggle_units
        footer_layout.addWidget(self.toggle_button)

        parent_layout.addWidget(footer)

    def _search_location(self) -> None:
        query = self.search_input.text().strip()
        if query:
            self.status_label.SetText("SEARCHING LOCATION...")
            self.engine.search_location(query)

    def _manual_refresh(self) -> None:
        self.status_label.SetText("REFRESHING WEATHER DATA...")
        self.engine.refresh_weather()
        self.engine.refresh_forecast()

    def _toggle_units(self) -> None:
        self.engine.unit = "imperial" if self.engine.unit == "metric" else "metric"
        self.units_button.SetText(self.engine.unit.upper())
        self._apply_button_state(self.units_button, "warning" if self.engine.unit == "metric" else "accent")
        self._apply_button_state(self.toggle_button, "warning" if self.engine.unit == "metric" else "accent")
        self.engine.last_weather = {}
        self.engine.last_forecast = {}
        self.engine._last_fetch = 0
        self.footer_label.SetText(f"UNITS: {self.engine.unit.upper()}")
        self.status_label.SetText(f"UNITS: {self.engine.unit.upper()} MODE")
        self.engine.refresh_weather()
        self.engine.refresh_forecast()

    def _toggle_fullscreen(self) -> None:
        self._is_fullscreen = not self._is_fullscreen
        if self._is_fullscreen:
            getattr(self, "showFullScreen", lambda: None)()
            self.fullscreen_button.SetText("WINDOWED")
            self._apply_button_state(self.fullscreen_button, "warning")
            self.status_label.SetText("FULLSCREEN MODE ENABLED")
        else:
            getattr(self, "showNormal", lambda: None)()
            self.fullscreen_button.SetText("FULLSCREEN")
            self._apply_button_state(self.fullscreen_button, "accent")
            self.status_label.SetText("PADD MODE RESTORED")

    def resizeEvent(self, a0) -> None:
        super().resizeEvent(a0)
        self._update_responsive_layout()

    def _on_location_resolved(self, location: str) -> None:
        if self._shutting_down:
            return
        self.loc_label.SetText(f"LOCATION: {location}")
        self.status_label.SetText("LOCATION RESOLVED")

    def _on_weather_update(self, data: dict) -> None:
        if self._shutting_down:
            return
        if data.get("Status") == "success":
            unit_sign = "°F" if self.engine.unit == "imperial" else "°C"
            wind_unit = "mph" if self.engine.unit == "imperial" else "km/h"
            self.temp_label.SetText(f"TEMPERATURE: {data.get('Temp', 0)} {unit_sign}")
            self.condition_label.SetText(f"CONDITION: {data.get('Condition', 'UNKNOWN')}")
            self.weather_icon.SetText(data.get("Icon", "❔"))
            self.wind_label.SetText(f"WIND: {data.get('WindSpeed', 0)} {wind_unit}")
            self.status_short.SetText("STATUS: TELEMETRY RECEIVED")
            self.footer_label.SetText("LIVE MATRIX: WEATHER STREAM STABLE")

            self.current_blocks[0].SetValue(f"{data.get('Humidity', '--')} %")
            self.current_blocks[1].SetValue(f"{data.get('Pressure', '--')} mb")
            self.current_blocks[2].SetValue(f"{data.get('DewPoint', '--')} {unit_sign}")
            self.current_blocks[3].SetValue(f"{data.get('WindDirection', '--')}°")

            if hasattr(self, 'detailed_blocks'):
                self.detailed_blocks["humidity"].SetValue(f"{data.get('Humidity', '--')} %")
                self.detailed_blocks["pressure"].SetValue(f"{data.get('Pressure', '--')} hPa")
                self.detailed_blocks["visibility"].SetValue(f"{data.get('Visibility', '--')} km")
                self.detailed_blocks["dewpoint"].SetValue(f"{data.get('DewPoint', '--')} {unit_sign}")
                self.detailed_blocks["windspeed"].SetValue(f"{data.get('WindSpeed', 0)} {wind_unit}")
                self.detailed_blocks["winddir"].SetValue(data.get('WindDirection', '---'))
                self.detailed_blocks["uvindex"].SetValue(str(data.get('UVIndex', '--')))
                self.detailed_blocks["cloudcover"].SetValue(f"{data.get('CloudCover', '--')} %")

            if hasattr(self, 'hourly_cards') and data.get('Hourly'):
                for i, hour_data in enumerate(data.get('Hourly', [])[:12]):
                    if i < len(self.hourly_cards):
                        time_lbl, icon_lbl, temp_lbl = self.hourly_cards[i]
                        time_lbl.SetText(hour_data.get('Time', f'+{i}H'))
                        icon_lbl.SetText(hour_data.get('Icon', '☀'))
                        temp_lbl.SetText(f"{hour_data.get('Temp', '--')}°")
        else:
            self.status_label.SetText(f"ERROR: {data.get('Message', 'FAILED')}")

    def _on_forecast_update(self, data: dict) -> None:
        if self._shutting_down:
            return
        if data.get("Status") == "success":
            unit_sign = "°F" if self.engine.unit == "imperial" else "°C"

            for i, item in enumerate(data.get("Daily", [])):
                if i < len(self.forecast_cards):
                    day, temp, cond = self.forecast_cards[i]
                    day.SetText(item.get("Date", "---"))
                    temp.SetText(f"{item.get('TempMax', 0)} {unit_sign}")
                    cond.SetText(f"{item.get('Icon', '❔')} {item.get('Condition', '---')}")

            if hasattr(self, 'hourly_cards') and data.get('Hourly'):
                for i, hour_data in enumerate(data.get('Hourly', [])[:12]):
                    if i < len(self.hourly_cards):
                        time_lbl, icon_lbl, temp_lbl = self.hourly_cards[i]
                        time_lbl.SetText(hour_data.get('Time', f'+{i}H'))
                        icon_lbl.SetText(hour_data.get('Icon', '☀'))
                        temp_lbl.SetText(f"{hour_data.get('Temp', '--')}°")

            self.map_label.SetText(f"TACTICAL MAP: {self.engine.location_name}")
            self.status_label.SetText("FORECAST DATA RECEIVED")
        else:
            self.footer_label.SetText(f"FORECAST ERROR: {data.get('Message', 'FAILED')}")


if __name__ == "__main__":
    if "--cli" in sys.argv:
        print("Headless mode not implemented. Please run without --cli.")
        sys.exit(0)

    app_factory = cast(Any, Application)
    app = app_factory(sys.argv)
    window = WeatherStation()
    window.show()
    sys.exit(cast(Any, app).exec())
