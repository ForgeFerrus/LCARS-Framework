"""
LCARS Board Computer - Інтегрований бортовий комп'ютер системи
Центральний інтелект для управління всіма компонентами LCARS Framework
"""

import sys
import json
import logging
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from lcars_ai import MockComputerProvider, HuggingFaceProvider
# Додавання шляхів
project_root = str(Path(__file__).parent.parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Stub classes для автономного запуску
class EventType:
    SYSTEM_START = "system_start"
    SYSTEM_STOP = "system_stop"
    COMMAND_EXECUTED = "command_executed"
    PROJECT_LOADED = "project_loaded"
    SIMULATION_STARTED = "simulation_started"
    SIMULATION_COMPLETED = "simulation_completed"
    SIMULATION_ERROR = "simulation_error"
    PLUGIN_LOADED = "plugin_loaded"

class Event:
    def __init__(self, type_, data=None):
        self.type = type_
        self.data = data
        self.timestamp = datetime.now().isoformat()

class EventBus:
    """Stub Event Bus для автономного запуску"""
    def __init__(self):
        self.listeners = {}
    
    def subscribe(self, event_type, callback):
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        self.listeners[event_type].append(callback)
    
    def emit(self, event):
        if event.type in self.listeners:
            for callback in self.listeners[event.type]:
                callback(event)

try:
    from lcars.modules.project_manager import ProjectManager
except ImportError:
    # Stub ProjectManager
    class ProjectManager:
        def __init__(self, root_path):
            self.root_path = root_path
            self.projects = [
                type('Project', (), {'name': 'NX-01', 'path': root_path, 'description': 'Enterprise Project'}),
                type('Project', (), {'name': 'LCARS-Core', 'path': root_path, 'description': 'Core System'}),
                type('Project', (), {'name': 'Battle-Sim', 'path': root_path, 'description': 'Battle Simulation'}),
            ]
        
        def get_all_projects(self):
            return self.projects
        
        def get_project(self, name):
            for p in self.projects:
                if p.name == name:
                    return p
            return None

# Stub PluginManager
class PluginRegistry:
    def __init__(self):
        self.plugins = {}

class PluginManager:
    def __init__(self):
        self.plugins = {}
        self.registry = PluginRegistry()
    
    def load_plugin(self, name):
        return {"name": name, "status": "loaded"}
    
    def get_all_plugins(self):
        return list(self.plugins.keys())
    
    def discover_plugins(self):
        return {}


class SystemStatus(Enum):
    """Статуси системи"""
    ONLINE = "online"
    OFFLINE = "offline"
    STANDBY = "standby"
    ERROR = "error"
    MAINTENANCE = "maintenance"


@dataclass
class SystemMetrics:
    """Метрики системи"""
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    disk_usage: float = 0.0
    active_projects: int = 0
    running_simulations: int = 0
    system_temperature: float = 0.0
    uptime_hours: int = 0
    last_update: datetime = None
    
    def __post_init__(self):
        if self.last_update is None:
            self.last_update = datetime.now()


@dataclass
class Alert:
    """Системне сповіщення"""
    id: str
    level: str  # INFO, WARNING, ERROR, CRITICAL
    message: str
    source: str
    timestamp: datetime
    acknowledged: bool = False
    details: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.details is None:
            self.details = {}


class BoardComputer:
    """Бортовий комп'ютер LCARS - центральний інтелект системи"""
    
    def __init__(self):
        self.logger = logging.getLogger("BoardComputer")
        self.logger.setLevel(logging.INFO)
        
        # Система
        self.status = SystemStatus.STANDBY
        self.start_time = datetime.now()
        self.metrics = SystemMetrics()
        
        # Компоненти
        self.event_bus = EventBus()
        self.project_manager = ProjectManager(project_root)
        self.plugin_manager = PluginManager()
        
        # Стан
        self.active_projects: Dict[str, Any] = {}
        self.running_simulations: Dict[str, Any] = {}
        self.alerts: List[Alert] = []
        self.system_commands: Dict[str, Callable] = {}
        
        # Реєстрація команд
        self._register_system_commands()
        
        # Підписка на події
        self._subscribe_to_events()
        
        self.logger.info("Board Computer initialized")
    
    def _register_system_commands(self):
        """Зареєструвати системні команди"""
        self.system_commands = {
            "status": self.get_system_status,
            "metrics": self.get_system_metrics,
            "projects": self.get_projects_list,
            "analyze": self.analyze_project,
            "simulate": self.start_simulation,
            "stop": self.stop_simulation,
            "alerts": self.get_alerts,
            "ack_alert": self.acknowledge_alert,
            "health": self.health_check,
            "help": self.get_help,
        }
    
    def _subscribe_to_events(self):
        """Підписатися на системні події"""
        self.event_bus.subscribe(EventType.PROJECT_LOADED, self.on_project_loaded)
        self.event_bus.subscribe(EventType.SIMULATION_STARTED, self.on_simulation_started)
        self.event_bus.subscribe(EventType.SIMULATION_COMPLETED, self.on_simulation_completed)
        self.event_bus.subscribe(EventType.SIMULATION_ERROR, self.on_simulation_error)
        self.event_bus.subscribe(EventType.PLUGIN_LOADED, self.on_plugin_loaded)
    
    def initialize(self) -> bool:
        """Ініціалізувати бортовий комп'ютер"""
        try:
            self.logger.info("Initializing Board Computer systems...")
            
            # Завантаження плагінів
            # Optionally skip plugin loading in restricted environments
            if os.getenv('LCARS_DISABLE_PLUGINS', '0') in ('1', 'true', 'True'):
                self.logger.info('Plugin loading skipped via LCARS_DISABLE_PLUGINS')
                plugins = {}
            else:
                plugins = self.plugin_manager.discover_plugins()

            for plugin_name, plugin_path in plugins.items():
                try:
                    success = self.plugin_manager.load_plugin(plugin_name, plugin_path)
                except Exception as e:
                    logger.exception("Unhandled exception in %s", __file__)
                    raise

                    logger.exception("Unhandled exception in %s: %s", __file__, e)
                    raise

                    success = False
                    self.logger.exception(f"Exception while loading plugin {plugin_name}")

                if success:
                    self.logger.info(f"Plugin loaded: {plugin_name}")
                    self.add_alert("INFO", f"Plugin {plugin_name} loaded successfully", "BoardComputer")
                else:
                    self.logger.warning(f"Failed to load plugin: {plugin_name}")
                    self.add_alert("WARNING", f"Failed to load plugin {plugin_name}", "BoardComputer")
            
            # Аналіз проектів
            self._scan_projects()
            
            # Оновлення статусу
            self.status = SystemStatus.ONLINE
            self.add_alert("INFO", "Board Computer fully operational", "BoardComputer")
            
            self.logger.info("Board Computer initialization complete")
            return True
            
        except Exception as e:
            
            logger.exception("Unhandled exception in %s", __file__)
            
            raise

            self.logger.error(f"Board Computer initialization failed: {e}")
            self.status = SystemStatus.ERROR
            self.add_alert("ERROR", f"Initialization failed: {str(e)}", "BoardComputer")
            return False
    
    def execute_command(self, command: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Виконати команду"""
        if params is None:
            params = {}
        
        self.logger.info(f"Executing command: {command}")
        
        if command in self.system_commands:
            try:
                result = self.system_commands[command](**params)
                return {
                    "status": "success",
                    "command": command,
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                logger.exception("Unhandled exception in %s", __file__)
                raise

                self.logger.error(f"Command execution failed: {e}")
                self.add_alert("ERROR", f"Command {command} failed: {str(e)}", "BoardComputer")
                return {
                    "status": "error",
                    "command": command,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
        else:
            return {
                "status": "error",
                "command": command,
                "error": "Unknown command",
                "timestamp": datetime.now().isoformat()
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Отримати статус системи"""
        uptime = (datetime.now() - self.start_time).total_seconds() / 3600
        
        return {
            "status": self.status.value,
            "uptime_hours": round(uptime, 2),
            "start_time": self.start_time.isoformat(),
            "active_projects": len(self.active_projects),
            "running_simulations": len(self.running_simulations),
            "alerts_count": len(self.alerts),
            "plugins_loaded": len(self.plugin_manager.registry.plugins)
        }
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Отримати метрики системи"""
        try:
            import psutil
            
            self.metrics.cpu_usage = psutil.cpu_percent(interval=1)
            self.metrics.memory_usage = psutil.virtual_memory().percent
            self.metrics.disk_usage = psutil.disk_usage("/").percent
            self.metrics.uptime_hours = int((datetime.now() - self.start_time).total_seconds() / 3600)
            self.metrics.last_update = datetime.now()
            
            # Температура (якщо доступно)
            try:
                temps = psutil.sensors_temperatures()
                if temps:
                    temp_readings = list(temps.values())[0]
                    if temp_readings:
                        self.metrics.system_temperature = temp_readings[0].current
            except:
                pass
            
        except ImportError:
            self.logger.warning("psutil not available for system metrics")
        
        return asdict(self.metrics)
    
    def get_projects_list(self) -> List[Dict[str, Any]]:
        """Отримати список проектів"""
        projects = []
        project_names = self.project_manager.get_project_names()
        
        for name in project_names:
            project = self.project_manager.get_project(name)
            if project:
                projects.append({
                    "name": name,
                    "path": str(project.path),
                    "active": name in self.active_projects,
                    "type": self._detect_project_type(name)
                })
        
        return projects
    
    def _detect_project_type(self, project_name: str) -> str:
        """Визначити тип проекту"""
        if "NCC" in project_name.upper():
            return "NCC"
        elif "ENX" in project_name.upper():
            return "ENX"
        else:
            return "CUSTOM"
    
    def analyze_project(self, project_name: str) -> Dict[str, Any]:
        """Аналізувати проект"""
        project = self.project_manager.get_project(project_name)
        if not project:
            return {"error": "Project not found"}
        
        try:
            path = Path(project.path)
            
            # Підрахунок файлів
            cpp_files = len(list(path.rglob("*.cpp")))
            h_files = len(list(path.rglob("*.h")))
            macro_files = len(list(path.rglob("*.mac")))
            cmake_files = len(list(path.rglob("CMakeLists.txt")))
            
            # Розмір
            total_size = sum(f.stat().st_size for f in path.rglob("*") if f.is_file())
            
            # Остання модифікація
            last_modified = max(
                (f.stat().st_mtime for f in path.rglob("*") if f.is_file()),
                default=0
            )
            
            return {
                "name": project_name,
                "path": str(path),
                "files": {
                    "cpp": cpp_files,
                    "headers": h_files,
                    "macros": macro_files,
                    "cmake": cmake_files,
                    "total": cpp_files + h_files + macro_files
                },
                "size_bytes": total_size,
                "size_mb": round(total_size / (1024 * 1024), 2),
                "last_modified": datetime.fromtimestamp(last_modified).isoformat(),
                "has_geant4": cmake_files > 0,
                "has_macros": macro_files > 0
            }
            
        except Exception as e:
            
            logger.exception("Unhandled exception in %s", __file__)
            
            raise

            return {"error": f"Analysis failed: {str(e)}"}
    
    def start_simulation(self, project_name: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Запустити симуляцію"""
        if params is None:
            params = {}
        
        project = self.project_manager.get_project(project_name)
        if not project:
            return {"error": "Project not found"}
        
        sim_id = f"{project_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.running_simulations[sim_id] = {
            "id": sim_id,
            "project": project_name,
            "start_time": datetime.now(),
            "status": "running",
            "params": params
        }
        
        # Генерація події
        self.event_bus.emit(Event(
            EventType.SIMULATION_STARTED,
            source="BoardComputer",
            data={"simulation_id": sim_id, "project": project_name}
        ))
        
        self.add_alert("INFO", f"Simulation started: {sim_id}", "BoardComputer")
        
        return {
            "simulation_id": sim_id,
            "status": "started",
            "project": project_name
        }
    
    def stop_simulation(self, simulation_id: str) -> Dict[str, Any]:
        """Зупинити симуляцію"""
        if simulation_id not in self.running_simulations:
            return {"error": "Simulation not found"}
        
        sim = self.running_simulations[simulation_id]
        sim["status"] = "stopped"
        sim["end_time"] = datetime.now()
        
        # Генерація події
        self.event_bus.emit(Event(
            EventType.SIMULATION_COMPLETED,
            source="BoardComputer",
            data={"simulation_id": simulation_id, "status": "stopped"}
        ))
        
        self.add_alert("INFO", f"Simulation stopped: {simulation_id}", "BoardComputer")
        
        return {
            "simulation_id": simulation_id,
            "status": "stopped"
        }
    
    def get_alerts(self, level: str = None, acknowledged: bool = None) -> List[Dict[str, Any]]:
        """Отримати сповіщення"""
        alerts = self.alerts.copy()
        
        if level:
            alerts = [a for a in alerts if a.level == level]
        
        if acknowledged is not None:
            alerts = [a for a in alerts if a.acknowledged == acknowledged]
        
        # Сортування за часом (нові перші)
        alerts.sort(key=lambda x: x.timestamp, reverse=True)
        
        return [asdict(alert) for alert in alerts[:50]]  # Обмеження 50
    
    def acknowledge_alert(self, alert_id: str) -> Dict[str, Any]:
        """Підтвердити сповіщення"""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.acknowledged = True
                return {"status": "acknowledged", "alert_id": alert_id}
        
        return {"error": "Alert not found"}
    
    def add_alert(self, level: str, message: str, source: str, details: Dict[str, Any] = None):
        """Додати сповіщення"""
        alert = Alert(
            id=f"alert_{len(self.alerts)}_{datetime.now().strftime('%H%M%S')}",
            level=level,
            message=message,
            source=source,
            timestamp=datetime.now(),
            details=details
        )
        
        self.alerts.append(alert)
        
        # Автоматичне підтвердження інформаційних сповіщень
        if level == "INFO":
            alert.acknowledged = True
        
        # Обмеження кількості сповіщень
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-50:]
    
    def health_check(self) -> Dict[str, Any]:
        """Перевірка здоров'я системи"""
        health = {
            "overall": "healthy",
            "components": {},
            "issues": [],
            "timestamp": datetime.now().isoformat()
        }
        
        # Перевірка компонентів
        try:
            # Project Manager
            projects = self.project_manager.get_project_names()
            health["components"]["project_manager"] = {
                "status": "healthy",
                "projects_count": len(projects)
            }
        except Exception as e:
            logger.exception("Unhandled exception in %s", __file__)
            raise

            health["components"]["project_manager"] = {
                "status": "error",
                "error": str(e)
            }
            health["issues"].append(f"Project Manager error: {e}")
        
        # Event Bus
        try:
            health["components"]["event_bus"] = {
                "status": "healthy",
                "listeners_count": len(self.event_bus.listeners)
            }
        except Exception as e:
            logger.exception("Unhandled exception in %s", __file__)
            raise

            health["components"]["event_bus"] = {
                "status": "error",
                "error": str(e)
            }
            health["issues"].append(f"Event Bus error: {e}")
        
        # Plugin Manager
        try:
            health["components"]["plugin_manager"] = {
                "status": "healthy",
                "plugins_count": len(self.plugin_manager.registry.plugins)
            }
        except Exception as e:
            logger.exception("Unhandled exception in %s", __file__)
            raise

            health["components"]["plugin_manager"] = {
                "status": "error",
                "error": str(e)
            }
            health["issues"].append(f"Plugin Manager error: {e}")
        
        # Загальний статус
        if health["issues"]:
            health["overall"] = "degraded" if len(health["issues"]) < 3 else "unhealthy"
        
        return health
    
    def get_help(self) -> Dict[str, Any]:
        """Отримати довідку"""
        return {
            "available_commands": list(self.system_commands.keys()),
            "command_descriptions": {
                "status": "Get system status",
                "metrics": "Get system metrics",
                "projects": "List all projects",
                "analyze": "Analyze specific project",
                "simulate": "Start simulation",
                "stop": "Stop simulation",
                "alerts": "Get system alerts",
                "ack_alert": "Acknowledge alert",
                "health": "System health check",
                "help": "Show this help"
            },
            "examples": [
                {"command": "status", "description": "Get overall system status"},
                {"command": "projects", "description": "List all available projects"},
                {"command": "analyze", "params": {"project_name": "NCC-1701"}, "description": "Analyze specific project"},
                {"command": "simulate", "params": {"project_name": "NCC-1701", "energy": "1 GeV"}, "description": "Start simulation"}
            ]
        }
    
    def _scan_projects(self):
        """Сканувати проекти"""
        try:
            project_names = self.project_manager.get_project_names()
            for name in project_names:
                project = self.project_manager.get_project(name)
                if project:
                    self.active_projects[name] = {
                        "path": str(project.path),
                        "last_accessed": datetime.now()
                    }
            
            self.add_alert("INFO", f"Scanned {len(self.active_projects)} projects", "BoardComputer")
            
        except Exception as e:
            
            logger.exception("Unhandled exception in %s", __file__)
            
            raise

            self.logger.error(f"Project scan failed: {e}")
            self.add_alert("ERROR", f"Project scan failed: {str(e)}", "BoardComputer")
    
    # Event handlers
    def on_project_loaded(self, event: Event):
        """Обробник завантаження проекту"""
        project_name = event.data.get("project_name", "unknown")
        self.logger.info(f"Project loaded: {project_name}")
    
    def on_simulation_started(self, event: Event):
        """Обробник старту симуляції"""
        sim_id = event.data.get("simulation_id", "unknown")
        self.logger.info(f"Simulation started: {sim_id}")
    
    def on_simulation_completed(self, event: Event):
        """Обробник завершення симуляції"""
        sim_id = event.data.get("simulation_id", "unknown")
        self.logger.info(f"Simulation completed: {sim_id}")
        
        if sim_id in self.running_simulations:
            self.running_simulations[sim_id]["status"] = "completed"
            self.running_simulations[sim_id]["end_time"] = datetime.now()
    
    def on_simulation_error(self, event: Event):
        """Обробник помилки симуляції"""
        sim_id = event.data.get("simulation_id", "unknown")
        error = event.data.get("error", "unknown error")
        
        self.logger.error(f"Simulation error: {sim_id} - {error}")
        self.add_alert("ERROR", f"Simulation {sim_id} failed: {error}", "BoardComputer")
        
        if sim_id in self.running_simulations:
            self.running_simulations[sim_id]["status"] = "error"
            self.running_simulations[sim_id]["error"] = error
    
    def on_plugin_loaded(self, event: Event):
        """Обробник завантаження плагіна"""
        plugin_name = event.data.get("plugin_name", "unknown")
        self.logger.info(f"Plugin loaded: {plugin_name}")
    
    def shutdown(self):
        """Вимкнення бортового комп'ютера"""
        self.logger.info("Shutting down Board Computer...")
        
        # Зупинка всіх симуляцій
        for sim_id in list(self.running_simulations.keys()):
            self.stop_simulation(sim_id)
        
        # Вивантаження плагінів
        for plugin_name in list(self.plugin_manager.registry.plugins.keys()):
            try:
                self.plugin_manager.unload_plugin(plugin_name)
            except:
                pass
        
        self.status = SystemStatus.OFFLINE
        self.add_alert("INFO", "Board Computer shutdown complete", "BoardComputer")
        
        self.logger.info("Board Computer shutdown complete")


# Глобальний екземпляр бортового комп'ютера
_board_computer = None

def get_board_computer() -> BoardComputer:
    """Отримати глобальний екземпляр бортового комп'ютера"""
    global _board_computer
    if _board_computer is None:
        _board_computer = BoardComputer()
    return _board_computer


def initialize_board_computer() -> bool:
    """Ініціалізувати бортовий комп'ютер"""
    computer = get_board_computer()
    return computer.initialize()


if __name__ == "__main__":
    # Тестування бортового комп'ютера
    computer = BoardComputer()
    
    if computer.initialize():
        print("Board Computer initialized successfully")
        
        # Тестові команди
        print("\nSystem Status:")
        result = computer.execute_command("status")
        print(json.dumps(result, indent=2))
        
        print("\nProjects:")
        result = computer.execute_command("projects")
        print(json.dumps(result, indent=2))
        
        print("\nHelp:")
        result = computer.execute_command("help")
        print(json.dumps(result, indent=2))
        
    else:
        print("Board Computer initialization failed")
