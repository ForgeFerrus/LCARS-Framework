from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
import time

# Типи палуб для навігації в турболіфті
class DeckType(Enum):
    MAIN = "main"
    ENGINEERING = "engineering"
    SCIENCE = "science"
    BRIDGE = "bridge"
    AUXILIARY = "auxiliary"

# Опис палуби з ідентифікатором та метаданими
@dataclass
class Deck:
    id: str
    name: str
    deckType: DeckType
    widget: Optional[Any] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

# Маршрут між палубами з позначкою часу
@dataclass
class Route:
    fromDeck: str
    toDeck: str
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

# Сервіс турболіфту для керування переходами між палубами
class TurboliftService:
    def __init__(self):
        self.decks: Dict[str, Deck] = {}
        self.history: List[Route] = []
        self.currentDeck: Optional[str] = None
        self.listeners: List[Callable] = []
        self.transitions: Dict[str, Callable] = {}
        
    # Реєстрація нової палуби в системі турболіфту
    def registerDeck(self, deckId: str, name: str, deckType: DeckType = DeckType.MAIN,
                     widget: Optional[Any] = None, metadata: Optional[Dict] = None) -> Deck:
        deck = Deck(
            id=deckId,
            name=name,
            deckType=deckType,
            widget=widget,
            metadata=metadata or {}
        )
        self.decks[deckId] = deck
        self.notify("deckRegistered", deck)
        return deck
    
    # Перехід на вказану палубу з фіксацією в історії
    def transferTo(self, deckId: str, **kwargs) -> bool:
        if deckId not in self.decks:
            return False
        previous = self.currentDeck
        self.currentDeck = deckId
        if previous:
            route = Route(fromDeck=previous, toDeck=deckId, metadata=kwargs)
            self.history.append(route)
        deck = self.decks[deckId]
        if deckId in self.transitions:
            handler = self.transitions[deckId]
            if callable(handler):
                handler(deck)
        self.notify("deckChanged", deck)
        return True
    
    # Повернення на попередню палубу з історії маршрутів
    def goBack(self) -> bool:
        if not self.history:
            return False
        lastRoute = self.history.pop()
        return self.transferTo(lastRoute.fromDeck, back=True)
    
    # Отримання поточної палуби
    def getCurrentDeck(self) -> Optional[Deck]:
        if self.currentDeck:
            return self.decks.get(self.currentDeck)
        return None
    
    # Отримання історії маршрутів
    def getDeckHistory(self) -> List[Route]:
        return self.history.copy()
    
    # Додавання слухача подій турболіфту
    def addListener(self, callback: Callable[[str, Deck], None]):
        self.listeners.append(callback)
        
    # Реєстрація обробника переходу для конкретної палуби
    def registerTransition(self, deckId: str, handler: Callable[[Deck], None]):
        self.transitions[deckId] = handler
        
    # Отримання палуб за типом
    def getDecksByType(self, deckType: DeckType) -> List[Deck]:
        return [d for d in self.decks.values() if d.deckType == deckType]
    
    # Пошук палуб за назвою або ідентифікатором
    def searchDecks(self, query: str) -> List[Deck]:
        query = query.lower()
        return [d for d in self.decks.values() 
                if query in d.name.lower() or query in d.id.lower()]
    
    # Сповіщення слухачів про подію
    def notify(self, event: str, deck: Deck):
        for listener in self.listeners:
            if callable(listener):
                listener(event, deck)
    
    # Статистика навігації по палубах
    def getStats(self) -> Dict[str, Any]:
        return {
            "totalDecks": len(self.decks),
            "current": self.currentDeck,
            "historyCount": len(self.history),
            "byType": {t.value: len(self.getDecksByType(t)) for t in DeckType}
        }

turboliftService: Optional[TurboliftService] = None

# Отримання або створення singleton-екземпляра сервісу турболіфту
def getTurboliftService() -> TurboliftService:
    global turboliftService
    if turboliftService is None:
        turboliftService = TurboliftService()
    return turboliftService
