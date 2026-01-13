"""
Event Bus для LCARS Enterprise
===============================

Глобальна система подій для комунікації між плагінами та компонентами
без прямої залежності один від одного.
"""

import logging
from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


# ═════════════════════════════════════════════════════════════════════════════
# ТИПИ ПОДІЙ
# ═════════════════════════════════════════════════════════════════════════════

class EventType(Enum):
    """Типи подій у системі"""
    
    # Цикл життя приложення
    APP_STARTUP = "app:startup"
    APP_SHUTDOWN = "app:shutdown"
    APP_CONFIG_CHANGED = "app:config_changed"
    
    # Керування плагінами
    PLUGIN_LOADED = "plugin:loaded"
    PLUGIN_UNLOADED = "plugin:unloaded"
    
    # Симуляції
    SIMULATION_STARTED = "simulation:started"
    SIMULATION_COMPLETED = "simulation:completed"
    SIMULATION_ERROR = "simulation:error"
    SIMULATION_CANCELLED = "simulation:cancelled"
    
    # Детектор
    DETECTOR_UPDATED = "detector:updated"
    DETECTOR_GEOMETRY_CHANGED = "detector:geometry_changed"
    
    # Дані
    DATA_LOADED = "data:loaded"
    DATA_EXPORTED = "data:exported"
    
    # UI
    UI_THEME_CHANGED = "ui:theme_changed"
    UI_COMPONENT_UPDATED = "ui:component_updated"


@dataclass
class Event:
    """Подія в системі"""
    
    event_type: EventType
    source: str  # Хто генерує подію
    data: Dict[str, Any] = None
    timestamp: datetime = None
    event_id: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.event_id is None:
            self.event_id = str(uuid.uuid4())
        if self.data is None:
            self.data = {}
    
    def __str__(self):
        return f"Event({self.event_type.value}, source={self.source})"


# ═════════════════════════════════════════════════════════════════════════════
# EVENT LISTENER
# ═════════════════════════════════════════════════════════════════════════════

@dataclass
class EventListener:
    """Слухач подій"""
    
    listener_id: str
    callback: Callable
    event_types: List[EventType]
    priority: int = 0  # Вищий пріоритет = викликається раніше
    
    def should_handle(self, event_type: EventType) -> bool:
        """Чи слухач обробляє цей тип подій"""
        return event_type in self.event_types
    
    def handle(self, event: Event) -> bool:
        """Обробити подію"""
        try:
            self.callback(event)
            return True
        except Exception as e:
            logger.error(f"Error in event listener {self.listener_id}: {e}")
            return False


# ═════════════════════════════════════════════════════════════════════════════
# EVENT BUS
# ═════════════════════════════════════════════════════════════════════════════

class EventBus:
    """
    Центральна шина подій для системи.
    
    Дозволяє різним компонентам генерувати та слухати події
    без прямої залежності один від одного.
    
    Приклад:
        >>> bus = EventBus()
        >>> 
        >>> def on_sim_complete(event):
        ...     print(f"Симуляція завершена: {event.data}")
        >>> 
        >>> bus.subscribe(
        ...     EventType.SIMULATION_COMPLETED,
        ...     on_sim_complete,
        ...     source="detector"
        ... )
        >>> 
        >>> event = Event(
        ...     EventType.SIMULATION_COMPLETED,
        ...     source="detector",
        ...     data={"result": "success"}
        ... )
        >>> bus.emit(event)
    """
    
    _instance = None  # Singleton
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'listeners'):
            self.listeners: Dict[EventType, List[EventListener]] = {}
            self.event_history: List[Event] = []
            self.max_history = 1000
            logger.info("✓ EventBus initialized (Singleton)")
    
    def subscribe(
        self,
        event_type: EventType,
        callback: Callable,
        priority: int = 0,
        source_filter: Optional[str] = None
    ) -> str:
        """
        Підписатись на подію.
        
        Args:
            event_type: Тип подій для прослуховування
            callback: Функція-обработник
            priority: Пріоритет (вищий = викликається раніше)
            source_filter: Фільтр по джерелу (опціонально)
        
        Returns:
            ID слухача (для пізнішого відписання)
        """
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        
        listener_id = f"{callback.__name__}_{uuid.uuid4().hex[:8]}"
        
        listener = EventListener(
            listener_id=listener_id,
            callback=callback if source_filter is None 
                    else lambda e: callback(e) if e.source == source_filter else None,
            event_types=[event_type],
            priority=priority
        )
        
        self.listeners[event_type].append(listener)
        
        # Сортуємо по пріоритету
        self.listeners[event_type].sort(key=lambda l: l.priority, reverse=True)
        
        logger.debug(f"✓ Subscribed to {event_type.value} (ID: {listener_id})")
        return listener_id
    
    def unsubscribe(self, event_type: EventType, listener_id: str) -> bool:
        """
        Відписатись від подій.
        
        Args:
            event_type: Тип подій
            listener_id: ID слухача (отриманий при subscribe)
        
        Returns:
            True якщо відписано успішно
        """
        if event_type not in self.listeners:
            return False
        
        self.listeners[event_type] = [
            l for l in self.listeners[event_type]
            if l.listener_id != listener_id
        ]
        
        logger.debug(f"✓ Unsubscribed from {event_type.value} (ID: {listener_id})")
        return True
    
    def emit(self, event: Event) -> int:
        """
        Генерувати подію.
        
        Args:
            event: Подія для генерування
        
        Returns:
            Кількість слухачів, які обробили подію
        """
        self.event_history.append(event)
        
        # Обмежуємо розмір історії
        if len(self.event_history) > self.max_history:
            self.event_history = self.event_history[-self.max_history:]
        
        handled_count = 0
        
        if event.event_type in self.listeners:
            for listener in self.listeners[event.event_type]:
                if listener.handle(event):
                    handled_count += 1
        
        logger.debug(
            f"📡 Event emitted: {event.event_type.value} "
            f"(handled by {handled_count} listeners)"
        )
        
        return handled_count
    
    def clear_history(self):
        """Очистити історію подій"""
        self.event_history.clear()
    
    def get_history(self, event_type: Optional[EventType] = None) -> List[Event]:
        """Отримати історію подій"""
        if event_type is None:
            return self.event_history.copy()
        
        return [e for e in self.event_history if e.event_type == event_type]
    
    def get_stats(self) -> Dict[str, Any]:
        """Статистика по подіям"""
        stats = {}
        
        for event_type in EventType:
            count = len([e for e in self.event_history if e.event_type == event_type])
            if count > 0:
                stats[event_type.value] = count
        
        return stats
    
    def print_stats(self):
        """Вивести статистику"""
        print("\n📊 Event Bus Statistics:")
        print("-" * 50)
        stats = self.get_stats()
        
        if not stats:
            print("  (No events recorded)")
            return
        
        for event_type, count in sorted(stats.items(), key=lambda x: x[1], reverse=True):
            print(f"  {event_type}: {count}")
        
        print("-" * 50)


# ═════════════════════════════════════════════════════════════════════════════
# GLOBAL EVENT BUS
# ═════════════════════════════════════════════════════════════════════════════

# Глобальна шина подій - доступна звідусіль
event_bus = EventBus()


# ═════════════════════════════════════════════════════════════════════════════
# ТЕСТ
# ═════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import logging
    
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(levelname)-8s %(message)s'
    )
    
    print("=" * 80)
    print("LCARS Enterprise Event Bus - Demo")
    print("=" * 80 + "\n")
    
    # Створимо слухачів
    def on_simulation_started(event: Event):
        print(f"\n🟢 SIM STARTED: {event.data}")
    
    def on_simulation_completed(event: Event):
        print(f"🔵 SIM COMPLETED: {event.data}")
    
    def on_plugin_loaded(event: Event):
        print(f"📦 PLUGIN LOADED: {event.data}")
    
    # Підписуємось
    bus = EventBus()
    
    bus.subscribe(EventType.SIMULATION_STARTED, on_simulation_started, priority=10)
    bus.subscribe(EventType.SIMULATION_COMPLETED, on_simulation_completed, priority=5)
    bus.subscribe(EventType.PLUGIN_LOADED, on_plugin_loaded)
    
    # Генеруємо події
    print("\n📡 Emitting events...\n")
    
    bus.emit(Event(
        EventType.PLUGIN_LOADED,
        source="plugin_manager",
        data={"plugin": "detector_control", "version": "1.0.0"}
    ))
    
    bus.emit(Event(
        EventType.SIMULATION_STARTED,
        source="detector",
        data={"energy": 1.0, "particles": 10000}
    ))
    
    bus.emit(Event(
        EventType.SIMULATION_COMPLETED,
        source="detector",
        data={"result": "success", "time": 2.5}
    ))
    
    # Статистика
    bus.print_stats()
    
    print("\n✅ Event bus working correctly!")
