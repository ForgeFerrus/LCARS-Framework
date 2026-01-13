"""
Інтеграційний тест: Plugin System + Event Bus + Config Manager
===============================================================

Демонструє, як плагін використовує Event Bus та Config Manager
для комунікації зі системою.
"""

import logging
from pathlib import Path
import json
import sys

# Додамо path до lcars модулів
sys.path.insert(0, str(Path(__file__).parent.parent))

from lcars.core.plugin_system import LCARSPlugin, PluginRegistry
from lcars.core.event_bus import EventBus, Event, EventType
from lcars.core.config_manager import ConfigManager, ConfigSchema

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)-8s %(message)s'
)
logger = logging.getLogger(__name__)


# ═════════════════════════════════════════════════════════════════════════════
# ПРИКЛАД ПЛАГІНА: DETECTOR CONTROL
# ═════════════════════════════════════════════════════════════════════════════

class DetectorControlPlugin(LCARSPlugin):
    """
    Приклад плагіна для керування детектором.
    
    Демонструє:
    • Завантаження конфігурації
    • Прослуховування подій
    • Генерування подій
    • Експорт функціональності
    """
    
    def __init__(self, event_bus: EventBus, config_manager: ConfigManager):
        metadata = LCARSPlugin.Metadata(
            name="Detector Control",
            version="1.0.0",
            author="Enterprise",
            description="Управління детектором через плагін-архітектуру",
            dependencies=[]
        )
        super().__init__(metadata)
        
        self.event_bus = event_bus
        self.config_manager = config_manager
        self.detector_state = {
            "power": "off",
            "energy": 0.0,
            "particles": 0
        }
    
    def on_load(self) -> bool:
        """Викликається при завантаженні плагіна"""
        print(f"  📦 Loading plugin: {self.metadata.name}")
        
        # Підписуємось на конфігураційні зміни
        self.config_manager.watch(
            "detector",
            "energy",
            self._on_energy_changed
        )
        
        # Прослухуємо подію запуску
        self.event_bus.subscribe(
            EventType.SIMULATION_STARTED,
            self._on_simulation_started,
            priority=10
        )
        
        # Експортуємо API
        self.export("configure_detector", self.configure_detector)
        self.export("get_state", self.get_state)
        
        return True
    
    def on_unload(self) -> bool:
        """Викликається при вивантаженні"""
        print(f"  📦 Unloading plugin: {self.metadata.name}")
        return True
    
    def on_startup(self):
        """Викликається при старті приложення"""
        print(f"  🚀 Startup: {self.metadata.name}")
        
        # Генеруємо подію завантаження
        event = Event(
            EventType.PLUGIN_LOADED,
            source=self.metadata.name,
            data={"plugin": self.metadata.name, "version": self.metadata.version}
        )
        self.event_bus.emit(event)
    
    def on_shutdown(self):
        """Викликається при завершенні"""
        print(f"  🛑 Shutdown: {self.metadata.name}")
    
    def configure_detector(self, energy: float, particles: int) -> bool:
        """Налаштувати детектор"""
        print(f"\n  ⚙️  Configuring detector: energy={energy}, particles={particles}")
        
        self.config_manager.set("detector", "energy", energy)
        self.config_manager.set("detector", "particles", particles)
        
        self.detector_state["energy"] = energy
        self.detector_state["particles"] = particles
        
        # Генеруємо подію оновлення детектора
        event = Event(
            EventType.DETECTOR_UPDATED,
            source=self.metadata.name,
            data=self.detector_state.copy()
        )
        self.event_bus.emit(event)
        
        return True
    
    def get_state(self) -> dict:
        """Отримати стан детектора"""
        return self.detector_state.copy()
    
    def _on_energy_changed(self, config_name, key, old, new):
        """Callback при змінені енергії"""
        print(f"  ⚡ Energy changed: {old} → {new} MeV")
        self.detector_state["power"] = "on" if new > 0 else "off"
    
    def _on_simulation_started(self, event: Event):
        """Callback при старті симуляції"""
        print(f"  ▶️  Simulation started event received")
        print(f"     Parameters: {event.data}")


# ═════════════════════════════════════════════════════════════════════════════
# ПРИКЛАД ПЛАГІНА: ANALYSIS
# ═════════════════════════════════════════════════════════════════════════════

class AnalysisPlugin(LCARSPlugin):
    """Приклад другого плагіна для аналізу даних"""
    
    def __init__(self, event_bus: EventBus):
        metadata = LCARSPlugin.Metadata(
            name="Analysis",
            version="1.0.0",
            author="Enterprise",
            description="Аналіз результатів симуляцій"
        )
        super().__init__(metadata)
        self.event_bus = event_bus
    
    def on_load(self) -> bool:
        print(f"  📦 Loading plugin: {self.metadata.name}")
        
        # Прослухуємо завершення симуляцій
        self.event_bus.subscribe(
            EventType.SIMULATION_COMPLETED,
            self._on_simulation_completed,
            priority=5
        )
        
        return True
    
    def on_unload(self) -> bool:
        print(f"  📦 Unloading plugin: {self.metadata.name}")
        return True
    
    def on_startup(self):
        print(f"  🚀 Startup: {self.metadata.name}")
    
    def on_shutdown(self):
        print(f"  🛑 Shutdown: {self.metadata.name}")
    
    def _on_simulation_completed(self, event: Event):
        """Callback при завершенні симуляції"""
        print(f"  📊 Analyzing simulation results...")
        print(f"     Result: {event.data}")


# ═════════════════════════════════════════════════════════════════════════════
# ТЕСТ
# ═════════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 80)
    print("Integration Test: Plugins + Event Bus + Config Manager")
    print("=" * 80 + "\n")
    
    # 1. Ініціалізуємо системи
    print("1️⃣  Initializing systems...\n")
    event_bus = EventBus()
    config_manager = ConfigManager()
    
    # 2. Реєструємо схему детектора
    print("2️⃣  Registering configuration schema...\n")
    detector_schema = ConfigSchema(
        name="detector",
        required_keys=["energy"],
        optional_keys=["particles", "power"],
        type_hints={
            "energy": float,
            "particles": int,
            "power": str
        },
        defaults={
            "energy": 0.0,
            "particles": 0,
            "power": "off"
        }
    )
    config_manager.register_schema(detector_schema)
    
    # 3. Завантажимо конфігурацію
    print("3️⃣  Loading detector configuration...\n")
    detector_config = {
        "energy": 0.5,
        "particles": 5000,
        "power": "off"
    }
    config_path = Path("./detector_config.json")
    with open(config_path, 'w') as f:
        json.dump(detector_config, f)
    
    config_manager.load_config("detector", config_path)
    
    # 4. Створимо та завантажимо плагіни
    print("4️⃣  Creating and loading plugins...\n")
    detector_plugin = DetectorControlPlugin(event_bus, config_manager)
    analysis_plugin = AnalysisPlugin(event_bus)
    
    # Реєструємо плагіни
    plugin_registry = PluginRegistry()
    plugin_registry.register("detector_control", detector_plugin)
    plugin_registry.register("analysis", analysis_plugin)
    
    # Завантажимо їх
    detector_plugin.on_load()
    analysis_plugin.on_load()
    
    # 5. Викличемо on_startup
    print("\n5️⃣  Starting up...\n")
    detector_plugin.on_startup()
    analysis_plugin.on_startup()
    
    # 6. Імітуємо роботу
    print("\n6️⃣  Simulating detector operation...\n")
    print("  Scenario 1: Configure detector")
    detector_plugin.configure_detector(energy=1.5, particles=10000)
    
    print("\n  Scenario 2: Start simulation")
    start_event = Event(
        EventType.SIMULATION_STARTED,
        source="user",
        data={"energy": 1.5, "particles": 10000}
    )
    event_bus.emit(start_event)
    
    print("\n  Scenario 3: Complete simulation")
    complete_event = Event(
        EventType.SIMULATION_COMPLETED,
        source="simulator",
        data={"result": "success", "time": 2.5, "events": 9850}
    )
    event_bus.emit(complete_event)
    
    # 7. Статистика
    print("\n7️⃣  Statistics...\n")
    print("  📋 Active Plugins:")
    for name, plugin in plugin_registry.plugins.items():
        print(f"    • {name}: v{plugin.metadata.version}")
    
    print("\n  📡 Event Statistics:")
    event_bus.print_stats()
    
    print("\n  ⚙️  Configuration State:")
    config_manager.print_config("detector")
    
    print("\n  🎛️  Detector State:")
    state = detector_plugin.get_state()
    for key, value in state.items():
        print(f"    {key}: {value}")
    
    # 8. Завершимо
    print("\n8️⃣  Shutting down...\n")
    detector_plugin.on_shutdown()
    analysis_plugin.on_shutdown()
    
    plugin_registry.unregister("detector_control")
    plugin_registry.unregister("analysis")
    
    # Cleanup
    config_path.unlink()
    
    print("\n✅ Integration test completed successfully!")


if __name__ == "__main__":
    main()
