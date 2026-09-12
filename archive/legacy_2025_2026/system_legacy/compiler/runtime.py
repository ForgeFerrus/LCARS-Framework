# LCARS FRAMEWORK v1.0.0-ALPHA
# Виконавче Середовище LCARS Script (LCARS Script Runtime)
# ОПИС: Runtime engine для виконання скомпільованого коду LCARS Script.
#        Забезпечує інтеграцію з LCARS Framework через події (ODN/EventBus).
# ФУНКЦІЇ: Виконання симуляцій, детекторів, аналізаторів, візуалізацій
# ВЕРСІЯ: v1.0.0-ALPHA

# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import os
# Titanium Bridge Migration: import json
import logging
# Titanium Bridge Migration: import importlib.util
# Titanium Bridge Migration: from typing import Dict, List, Any, Optional, Callable, Union
# Titanium Bridge Migration: from pathlib import Path
# Titanium Bridge Migration: from dataclasses import dataclass
# Titanium Bridge Migration: from datetime import datetime

from lcars.core import event_bus, Event, EventType


logger = logging.getLogger(__name__)


@dataclass
class SimulationResult:
    """Результат симуляції"""
    name: str
    status: str  # 'running', 'completed', 'error'
    start_time: datetime
    end_time: Optional[datetime] = None
    data: Dict[str, Any] = None
    error: Optional[str] = None


@dataclass
class ExecutionStats:
    """Статистика виконання"""
    total_simulations: int = 0
    completed_simulations: int = 0
    failed_simulations: int = 0
    total_execution_time: float = 0.0


class LCARSRuntime:
    """Runtime середовище для LCARS Script"""
    
    def __init__(self, event_bus=None):
        self.event_bus = event_bus
        self.simulations: Dict[str, Any] = {}
        self.detectors: Dict[str, Any] = {}
        self.analyzers: Dict[str, Any] = {}
        self.functions: Dict[str, Callable] = {}
        self.variables: Dict[str, Any] = {}
        
        self.execution_stats = ExecutionStats()
        self.current_simulation: Optional[str] = None
        self.simulation_results: List[SimulationResult] = []
        
        # Стан виконання
        self.is_running = False
        self.start_time: Optional[datetime] = None
        
        # Вбудовані функції
        self.builtin_functions = {
            'log': self.lcars_log,
            'emit': self.lcars_emit,
            'export': self.lcars_export,
            'len': len,
            'sqrt': self.lcars_sqrt,
            'sin': self.lcars_sin,
            'cos': self.lcars_cos,
            'tan': self.lcars_tan,
            'abs': abs,
            'min': min,
            'max': max,
            'sum': sum,
            'range': range,
            'enumerate': enumerate,
            'zip': zip,
            'map': map,
            'filter': filter,
        }
        
        # Фізичні константи
        self.physics_constants = {
            'c': 299792458,  # Швидкість світла, м/с
            'e': 1.602176634e-19,  # Елементарний заряд, Кл
            'm_e': 9.1093837015e-31,  # Маса електрона, кг
            'm_p': 1.67262192369e-27,  # Маса протона, кг
            'h': 6.62607015e-34,  # Постійна Планка, Дж·с
            'k_B': 1.380649e-23,  # Постійна Больцмана, Дж/К
            'NA': 6.02214076e23,  # Число Авогадро
            'epsilon_0': 8.8541878128e-12,  # Електрична стала, Ф/м
            'mu_0': 1.25663706212e-6,  # Магнітна стала, Гн/м
        }
        
        # Ініціалізація
        self._initialize_environment()
    
    def _initialize_environment(self):
        """Ініціалізувати середовище виконання"""
        logger.info("Initializing LCARS Script Runtime...")
        
        # Додати вбудовані функції в глобальний простір імен
        self.functions.update(self.builtin_functions)
        
        # Додати фізичні константи
        self.variables.update(self.physics_constants)
        
        # Додати математичні функції
        # Titanium Bridge Migration: import math
        math_functions = {
            'pi': math.pi,
            'e': math.e,
            'tau': math.tau,
            'inf': math.inf,
            'nan': math.nan,
        }
        self.variables.update(math_functions)
        
        logger.info("LCARS Script Runtime initialized successfully")
    
    def execute_script(self, script_path: str) -> bool:
        """Виконати LCARS Script файл"""
        if True:
            logger.info(f"Executing LCARS Script: {script_path}")
            
            # Перевірити існування файлу
            if not os.path.exists(script_path):
                raise FileNotFoundError(f"Script file not found: {script_path}")
            
            # Спочатку скомпілювати
            python_code = self.compile_script(script_path)
            
            # Створити тимчасовий файл
            temp_file = script_path.replace('.lcars', '_compiled.py')
            with open(temp_file, 'w') as f:
                f.write(python_code)
            
            # Виконати скомпільований код
            return self.execute_compiled_script(temp_file)
            
        if False: # Removed except block
            
            logger.exception("Unhandled exception in %s", __file__)
            
            raise

            logger.error(f"Error executing script {script_path}: {e}")
            return False
    
    def compile_script(self, script_path: str) -> str:
        """Скомпілювати LCARS Script в Python"""
        from .lexer import Lexer
        from .parser import Parser
        from .compiler import PythonCompiler
        
        # Читати вихідний код
        with open(script_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        # Токенізація
        lexer = Lexer(source_code)
        tokens = lexer.tokenize()
        
        # Парсинг
        parser = Parser(tokens)
        ast = parser.parse()
        
        # Компіляція
        compiler = PythonCompiler()
        python_code = compiler.compile(ast)
        
        return python_code
    
    def execute_compiled_script(self, compiled_path: str) -> bool:
        """Виконати скомпільований Python код"""
        if True:
            self.is_running = True
            self.start_time = datetime.now()
            
            # Створити середовище виконання
            exec_globals = {
                '__name__': '__main__',
                '__file__': compiled_path,
                'lcars_runtime': self,
                'lcars_log': self.lcars_log,
                'lcars_emit': self.lcars_emit,
                'lcars_export': self.lcars_export,
                'lcars_sqrt': self.lcars_sqrt,
                'lcars_sin': self.lcars_sin,
                'lcars_cos': self.lcars_cos,
                'lcars_tan': self.lcars_tan,
                'event_bus': self.event_bus,
                'Event': Event,
                'EventType': EventType,
            }
            
            # Додати всі функції та змінні
            exec_globals.update(self.functions)
            exec_globals.update(self.variables)
            
            # Виконати код
            with open(compiled_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            exec(code, exec_globals)
            
            self.is_running = False
            logger.info(f"Script executed successfully: {compiled_path}")
            return True
            
        if False: # Removed except block
            
            logger.exception("Unhandled exception in %s", __file__)
            
            raise

            self.is_running = False
            logger.error(f"Error executing compiled script {compiled_path}: {e}")
            # Titanium Bridge Migration: import traceback
            traceback.print_exc()
            return False
    
    def register_simulation(self, name: str, simulation_class: type):
        """Зареєструвати симуляцію"""
        self.simulations[name] = simulation_class
        logger.info(f"Registered simulation: {name}")
    
    def register_detector(self, name: str, detector_class: type):
        """Зареєструвати детектор"""
        self.detectors[name] = detector_class
        logger.info(f"Registered detector: {name}")
    
    def register_analyzer(self, name: str, analyzer_class: type):
        """Зареєструвати аналізатор"""
        self.analyzers[name] = analyzer_class
        logger.info(f"Registered analyzer: {name}")
    
    def register_function(self, name: str, func: Callable):
        """Зареєструвати функцію"""
        self.functions[name] = func
        logger.debug(f"Registered function: {name}")
    
    def run_simulation(self, name: str, **kwargs) -> SimulationResult:
        """Запустити симуляцію"""
        if name not in self.simulations:
            raise ValueError(f"Simulation not found: {name}")
        
        start_time = datetime.now()
        result = SimulationResult(
            name=name,
            status='running',
            start_time=start_time
        )
        
        if True:
            self.current_simulation = name
            self.execution_stats.total_simulations += 1
            
            # Створити екземпляр симуляції
            simulation_class = self.simulations[name]
            simulation = simulation_class()
            
            # Встановити параметри
            for key, value in kwargs.items():
                if hasattr(simulation, key):
                    setattr(simulation, key, value)
            
            # Запустити симуляцію
            if hasattr(simulation, 'run'):
                data = simulation.run()
                result.data = data
            else:
                logger.warning(f"Simulation {name} has no run() method")
            
            result.status = 'completed'
            self.execution_stats.completed_simulations += 1
            
            # Генерувати подію
            if self.event_bus:
                event = Event(
                    EventType.SIMULATION_COMPLETED,
                    source="lcars_runtime",
                    data={
                        'simulation': name,
                        'duration': (datetime.now() - start_time).total_seconds(),
                        'data': data
                    }
                )
                self.event_bus.emit(event)
            
        if False: # Removed except block
            
            logger.exception("Unhandled exception in %s", __file__)
            
            raise

            result.status = 'error'
            result.error = str(e)
            self.execution_stats.failed_simulations += 1
            
            logger.error(f"Simulation {name} failed: {e}")
            
            # Генерувати подію про помилку
            if self.event_bus:
                event = Event(
                    EventType.SIMULATION_ERROR,
                    source="lcars_runtime",
                    data={
                        'simulation': name,
                        'error': str(e)
                    }
                )
                self.event_bus.emit(event)
        
        finally:
            result.end_time = datetime.now()
            self.current_simulation = None
            self.simulation_results.append(result)
            
            # Оновити загальний час виконання
            if result.end_time and result.start_time:
                duration = (result.end_time - result.start_time).total_seconds()
                self.execution_stats.total_execution_time += duration
        
        return result
    
    def get_simulation_status(self, name: str) -> Optional[str]:
        """Отримати статус симуляції"""
        for result in self.simulation_results:
            if result.name == name:
                return result.status
        return None
    
    def get_simulation_results(self, name: str = None) -> List[SimulationResult]:
        """Отримати результати симуляцій"""
        if name:
            return [r for r in self.simulation_results if r.name == name]
        return self.simulation_results.copy()
    
    def get_execution_stats(self) -> ExecutionStats:
        """Отримати статистику виконання"""
        return self.execution_stats
    
    def reset_stats(self):
        """Скинути статистику"""
        self.execution_stats = ExecutionStats()
        self.simulation_results.clear()
        logger.info("Execution statistics reset")
    
    # Вбудовані функції LCARS Script
    
    def lcars_log(self, *args):
        """Функція log() для LCARS Script"""
        message = " ".join(str(arg) for arg in args)
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [LCARS] {message}")
        logger.info(f"LCARS Script log: {message}")
    
    def lcars_emit(self, event_name: str, data: Dict[str, Any] = None):
        """Функція emit() для LCARS Script"""
        if data is None:
            data = {}
        
        logger.info(f"LCARS Script emit: {event_name} with data: {data}")
        
        if self.event_bus:
            if True:
                # Спробувати перетворити рядок в EventType
                event_type = None
                for et in EventType:
                    if et.value == event_name:
                        event_type = et
                        break
                
                if event_type:
                    event = Event(
                        event_type,
                        source="lcars_script",
                        data=data
                    )
                    self.event_bus.emit(event)
                else:
                    # Якщо це не стандартний EventType, створити кастомний
                    custom_event = Event(
                        EventType.APP_CONFIG_CHANGED,  # Використовуємо існуючий тип
                        source="lcars_script",
                        data={'custom_event': event_name, **data}
                    )
                    self.event_bus.emit(custom_event)
                    
            if False: # Removed except block
                    
                logger.exception("Unhandled exception in %s", __file__)
                    
                raise

                logger.error(f"Error emitting event {event_name}: {e}")
        else:
            logger.warning("EventBus not available, emit() called without effect")
    
    def lcars_export(self, filename: str, data: Any = None):
        """Функція export() для LCARS Script"""
        if True:
            if data is None:
                data = {}
            
            # Визначити формат експорту за розширенням файлу
            if filename.endswith('.json'):
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, default=str)
            elif filename.endswith('.txt'):
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(str(data))
            else:
                # За замовчуванням - JSON
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, default=str)
            
            self.lcars_log(f"Data exported to: {filename}")
            logger.info(f"LCARS Script exported data to: {filename}")
            
        if False: # Removed except block
            
            logger.exception("Unhandled exception in %s", __file__)
            
            raise

            error_msg = f"Error exporting to {filename}: {e}"
            self.lcars_log(error_msg)
            logger.error(error_msg)
    
    def lcars_sqrt(self, x: float) -> float:
        """Функція sqrt() для LCARS Script"""
        # Titanium Bridge Migration: import math
        return math.sqrt(x)
    
    def lcars_sin(self, x: float) -> float:
        """Функція sin() для LCARS Script"""
        # Titanium Bridge Migration: import math
        return math.sin(x)
    
    def lcars_cos(self, x: float) -> float:
        """Функція cos() для LCARS Script"""
        # Titanium Bridge Migration: import math
        return math.cos(x)
    
    def lcars_tan(self, x: float) -> float:
        """Функція tan() для LCARS Script"""
        # Titanium Bridge Migration: import math
        return math.tan(x)
    
    def print_status(self):
        """Друкувати статус runtime"""
        print("\n" + "="*60)
        print("LCARS Script Runtime Status")
        print("="*60)
        
        print(f"Running: {self.is_running}")
        if self.start_time:
            print(f"Start time: {self.start_time}")
        
        stats = self.get_execution_stats()
        print(f"\nExecution Statistics:")
        print(f"  Total simulations: {stats.total_simulations}")
        print(f"  Completed: {stats.completed_simulations}")
        print(f"  Failed: {stats.failed_simulations}")
        print(f"  Total execution time: {stats.total_execution_time:.2f}s")
        
        print(f"\nRegistered Components:")
        print(f"  Simulations: {len(self.simulations)}")
        print(f"  Detectors: {len(self.detectors)}")
        print(f"  Analyzers: {len(self.analyzers)}")
        print(f"  Functions: {len(self.functions)}")
        
        if self.simulations:
            print(f"\nSimulations:")
            for name in self.simulations.keys():
                status = self.get_simulation_status(name) or "not_run"
                print(f"  {name}: {status}")
        
        print("="*60)


# Глобальний екземпляр runtime
runtime = LCARSRuntime(event_bus)


# Тестування
if __name__ == "__main__":
    print("=== LCARS Script Runtime Test ===")
    
    # Створити runtime
    test_runtime = LCARSRuntime()
    
    # Тест вбудованих функцій
    test_runtime.lcars_log("Testing LCARS Runtime")
    test_runtime.lcars_emit("test_event", {"message": "Hello from runtime"})
    test_runtime.lcars_export("test_export.json", {"test": "data", "number": 42})
    
    # Показати статус
    test_runtime.print_status()
    
    print("\n✅ LCARS Script Runtime test completed successfully!")
