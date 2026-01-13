"""
ПРИКЛАД ПЛАГІНА: Detector Control Plugin
=========================================

Цей файл демонструє, як розробити плагін для LCARS Enterprise.

Структура плагіна:
  plugins/
    detector_control/
      detector_control_plugin.py  (цей файл)
      plugin.yaml                 (метаданні)
      __init__.py
"""

import logging
import sys
from pathlib import Path
from typing import Dict, Optional

# Додамо path для імпорту lcars
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lcars.core.plugin_system import LCARSPlugin
from lcars.core.event_bus import EventBus, Event, EventType
from lcars.core.config_manager import ConfigManager

logger = logging.getLogger(__name__)


class DetectorControlPlugin(LCARSPlugin):
    """
    Плагін для керування детектором.
    
    Демонструє:
    • Завантаження конфігурації
    • Прослуховування подій системи
    • Генерування власних подій
    • Експорт API функцій
    • Взаємодія з іншими компонентами
    """
    
    def __init__(self, event_bus: EventBus = None, config_manager: ConfigManager = None):
        """
        Ініціалізувати плагін.
        
        Args:
            event_bus: Глобальна шина подій (буде іnjected системою)
            config_manager: Менеджер конфiгурацiї (буде іnjected системою)
        """
        metadata = LCARSPlugin.Metadata(
            name="Detector Control",
            version="1.0.0",
            author="Enterprise Team",
            description="Управління детектором: конфiгурацiя, моніторинг, керування",
            dependencies=[]
        )
        super().__init__(metadata)
        
        # Сервіси, які будуть іnjected
        self.event_bus = event_bus or EventBus()
        self.config_manager = config_manager or ConfigManager()
        
        # Стан детектора
        self.state = {
            "power": "off",
            "energy": 0.0,
            "particles": 0,
            "shield_thickness": 1.0,
            "temperature": 20.0,
            "hv": 0  # High voltage
        }
        
        self.listener_ids = []  # Для відписання
    
    # ═════════════════════════════════════════════════════════════════════
    # ХУКИ ПЛАГІНА
    # ═════════════════════════════════════════════════════════════════════
    
    def on_load(self) -> bool:
        """
        Викликається при завантаженні плагіна.
        
        Тут варто:
        • Перевірити залежності
        • Завантажити конфіг
        • Піднаписатися на события
        • Експортувати API
        """
        logger.info(f"Loading plugin: {self.metadata.name}")
        
        try:
            # 1. Піднаписуємось на события
            self._setup_event_listeners()
            
            # 2. Завантажуємо конфiгурацiю
            self._load_configuration()
            
            # 3. Експортуємо API
            self._export_api()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load plugin: {e}")
            return False
    
    def on_unload(self) -> bool:
        """
        Викликається при вивантаженні плагіна.
        
        Тут варто очистити ресурси:
        • Відписатися від подій
        • Закрити файли
        • Зупинити сервіси
        """
        logger.info(f"Unloading plugin: {self.metadata.name}")
        
        # Відписуємось від усіх подій
        for listener_id in self.listener_ids:
            # Цей не реалізовано у базовій версії, але можна додати
            pass
        
        self.listener_ids.clear()
        return True
    
    def on_startup(self):
        """Викликається при старті приложення"""
        logger.info(f"Startup: {self.metadata.name}")
        
        # Генеруємо подію завантаження плагіна
        event = Event(
            EventType.PLUGIN_LOADED,
            source=self.metadata.name,
            data={
                "plugin": self.metadata.name,
                "version": self.metadata.version,
                "status": "ready"
            }
        )
        self.event_bus.emit(event)
    
    def on_shutdown(self):
        """Викликається при завершенні приложення"""
        logger.info(f"Shutdown: {self.metadata.name}")
        
        # Вимикаємо детектор
        self.set_power(False)
    
    # ═════════════════════════════════════════════════════════════════════
    # ЕКСПОРТОВАНИЙ API
    # ═════════════════════════════════════════════════════════════════════
    
    def configure_detector(self, **params) -> bool:
        """
        Налаштувати детектор.
        
        Args:
            energy (float): Енергія у MeV
            particles (int): Кількість частинок
            shield_thickness (float): Товщина щита
            hv (int): Висока напруга
        
        Returns:
            True якщо успішно
        
        Example:
            >>> detector.configure_detector(energy=1.5, particles=10000)
        """
        logger.info(f"Configuring detector with params: {params}")
        
        try:
            # Обновляємо стан
            if "energy" in params:
                self.state["energy"] = float(params["energy"])
            if "particles" in params:
                self.state["particles"] = int(params["particles"])
            if "shield_thickness" in params:
                self.state["shield_thickness"] = float(params["shield_thickness"])
            if "hv" in params:
                self.state["hv"] = int(params["hv"])
            
            # Синхронізуємо з конфiгом
            self.config_manager.set("detector", "energy", self.state["energy"])
            self.config_manager.set("detector", "particles", self.state["particles"])
            
            # Генеруємо подію
            event = Event(
                EventType.DETECTOR_UPDATED,
                source=self.metadata.name,
                data={"state": self.state.copy(), "params": params}
            )
            self.event_bus.emit(event)
            
            logger.info(f"Detector configured successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to configure detector: {e}")
            return False
    
    def get_state(self) -> Dict:
        """
        Отримати поточний стан детектора.
        
        Returns:
            Dict з усіма параметрами
        
        Example:
            >>> state = detector.get_state()
            >>> print(f"Temperature: {state['temperature']}")
        """
        return self.state.copy()
    
    def set_power(self, enabled: bool) -> bool:
        """
        Вмикнути/вимикнути детектор.
        
        Args:
            enabled (bool): True = вмикнути, False = вимикнути
        
        Returns:
            True якщо успішно
        """
        logger.info(f"Setting detector power: {enabled}")
        
        try:
            self.state["power"] = "on" if enabled else "off"
            
            event = Event(
                EventType.DETECTOR_UPDATED,
                source=self.metadata.name,
                data={"action": "power_changed", "power": self.state["power"]}
            )
            self.event_bus.emit(event)
            
            return True
        except Exception as e:
            logger.error(f"Failed to set power: {e}")
            return False
    
    def calibrate(self) -> bool:
        """
        Калібрувати детектор.
        
        Returns:
            True якщо успішно
        """
        logger.info("Starting detector calibration...")
        
        try:
            # Лічильник для демонстрації
            self.state["temperature"] = 20.0
            
            event = Event(
                EventType.DETECTOR_UPDATED,
                source=self.metadata.name,
                data={"action": "calibration_complete"}
            )
            self.event_bus.emit(event)
            
            logger.info("Calibration complete")
            return True
        except Exception as e:
            logger.error(f"Calibration failed: {e}")
            return False
    
    def get_detector_info(self) -> Dict:
        """Отримати інформацію про детектор"""
        return {
            "name": self.metadata.name,
            "version": self.metadata.version,
            "state": self.state.copy()
        }
    
    # ═════════════════════════════════════════════════════════════════════
    # ПРИВАТНІ МЕТОДИ
    # ═════════════════════════════════════════════════════════════════════
    
    def _setup_event_listeners(self):
        """Піднаписатися на события системи"""
        
        # Прослухуємо старт симуляцій
        listener_id = self.event_bus.subscribe(
            EventType.SIMULATION_STARTED,
            self._on_simulation_started,
            priority=10
        )
        self.listener_ids.append(listener_id)
        
        # Прослухуємо завершення симуляцій
        listener_id = self.event_bus.subscribe(
            EventType.SIMULATION_COMPLETED,
            self._on_simulation_completed,
            priority=5
        )
        self.listener_ids.append(listener_id)
        
        # Прослухуємо помилки
        listener_id = self.event_bus.subscribe(
            EventType.SIMULATION_ERROR,
            self._on_simulation_error,
            priority=15
        )
        self.listener_ids.append(listener_id)
    
    def _load_configuration(self):
        """Завантажити конфiгурацiю для детектора"""
        
        # Спостерігаємо за змінами енергії
        self.config_manager.watch(
            "detector",
            "energy",
            self._on_energy_changed
        )
    
    def _export_api(self):
        """Експортувати API функції для інших плагінів"""
        
        # Експортуємо основні функції
        self.export("configure", self.configure_detector)
        self.export("get_state", self.get_state)
        self.export("set_power", self.set_power)
        self.export("calibrate", self.calibrate)
        self.export("info", self.get_detector_info)
        
        logger.info("API exported")
    
    def _on_simulation_started(self, event: Event):
        """Callback: Симуляція розпочалась"""
        logger.info(f"Simulation started: {event.data}")
        
        # Опціонально: можемо налаштувати детектор на основі параметрів симуляції
        if "energy" in event.data:
            self.configure_detector(energy=event.data["energy"])
    
    def _on_simulation_completed(self, event: Event):
        """Callback: Симуляція завершилась"""
        logger.info(f"Simulation completed: {event.data}")
    
    def _on_simulation_error(self, event: Event):
        """Callback: Помилка під час симуляції"""
        logger.warning(f"Simulation error: {event.data}")
        
        # Вимикаємо детектор у разі помилки
        self.set_power(False)
    
    def _on_energy_changed(self, config_name, key, old_value, new_value):
        """Callback: Енергія змінилась у конфiгу"""
        logger.info(f"Energy changed in config: {old_value} → {new_value}")
        
        # Оновляємо внутрішній стан
        self.state["energy"] = new_value
        
        # Генеруємо подію
        event = Event(
            EventType.DETECTOR_UPDATED,
            source=self.metadata.name,
            data={"action": "energy_changed", "old": old_value, "new": new_value}
        )
        self.event_bus.emit(event)


# ═════════════════════════════════════════════════════════════════════════════
# ТЕСТ
# ═════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(levelname)-8s %(message)s'
    )
    
    print("=" * 80)
    print("Detector Control Plugin - Demo")
    print("=" * 80 + "\n")
    
    # Створимо плагін
    plugin = DetectorControlPlugin()
    
    # Завантажимо
    print("1. Loading plugin...")
    if plugin.on_load():
        print("   ✅ Plugin loaded\n")
    
    # Запустимо
    print("2. Starting up...")
    plugin.on_startup()
    print("   ✅ Plugin started\n")
    
    # Налаштуємо
    print("3. Configuring detector...")
    plugin.configure_detector(
        energy=1.5,
        particles=10000,
        shield_thickness=2.0,
        hv=500
    )
    print("   ✅ Configured\n")
    
    # Отримаємо стан
    print("4. Getting detector state...")
    state = plugin.get_state()
    print(f"   State: {state}\n")
    
    # Калібруємо
    print("5. Calibrating...")
    plugin.calibrate()
    print("   ✅ Calibrated\n")
    
    # Інформація
    print("6. Getting info...")
    info = plugin.get_detector_info()
    for key, value in info.items():
        print(f"   {key}: {value}\n" if isinstance(value, dict) else f"   {key}: {value}")
    
    # Вимикаємо
    print("7. Shutting down...")
    plugin.on_shutdown()
    plugin.on_unload()
    print("   ✅ Shutdown complete\n")
    
    print("✅ Demo completed successfully!")
