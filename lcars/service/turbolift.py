from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
import time

# Типи палуб 
class DeckType(Enum):
    MAIN = "main"
    ENGINEERING = "engineering"
    SCIENCE = "science"
    BRIDGE = "bridge"
    AUXILIARY = "auxiliary"

@dataclass
class Deck:
    id: str
    name: str
    deckType: DeckType
    widget: Optional[Any] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
@dataclass
class Route:
    fromDeck: str
    toDeck: str
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

class TurboliftSystem(Service):
    def __init__(self):
        self.decks: Dict[str, Deck] = {}
        self.history: List[Route] = []
        self.currentDeck: Optional[str] = None
        self.listeners: List[Callable] = []
        self.transitions: Dict[str, Callable] = {}
        
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
    
    def transferTo(self, deckId: str, **kwargs) -> bool:
        # Перехід на вказану палубу
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
    
    def goBack(self) -> bool:
        # Повернення на попередню палубу
        if not self.history:
            return False
        lastRoute = self.history.pop()
        return self.transferTo(lastRoute.fromDeck, back=True)
    
    def getCurrentDeck(self) -> Optional[Deck]:
        # Отримання поточної палуби
        if self.currentDeck:
            return self.decks.get(self.currentDeck)
        return None
    
    def getDeckHistory(self) -> List[Route]:
        # Історія маршрутів
        return self.history.copy()
    
    def addListener(self, callback: Callable[[str, Deck], None]):
        # Додавання слухача подій
        self.listeners.append(callback)
        
    def registerTransition(self, deckId: str, handler: Callable[[Deck], None]):
        # Реєстрація обробника переходу
        self.transitions[deckId] = handler
        
    def getDecksByType(self, deckType: DeckType) -> List[Deck]:
        # Отримання палуб за типом
        return [d for d in self.decks.values() if d.deckType == deckType]
    
    def searchDecks(self, query: str) -> List[Deck]:
        # Пошук палуб за назвою або ідентифікатором
        query = query.lower()
        return [d for d in self.decks.values() 
                if query in d.name.lower() or query in d.id.lower()]
    
    def notify(self, event: str, deck: Deck):
        # Сповіщення слухачів про подію
        for listener in self.listeners:
            if callable(listener):
                listener(event, deck)
    
    def getStats(self) -> Dict[str, Any]:
        # Статистика навігації
        return {
            "totalDecks": len(self.decks),
            "current": self.currentDeck,
            "historyCount": len(self.history),
            "byType": {t.value: len(self.getDecksByType(t)) for t in DeckType}
        }

turboliftSubsystem: Optional[TurboliftSubsystem] = None
TurboliftSystem = TurboliftSubsystem

def getTurboliftSubsystem() -> TurboliftSubsystem:
    global turboliftSubsystem
    if turboliftSubsystem is None:
        turboliftSubsystem = TurboliftSubsystem()
    return turboliftSubsystem

__all__ = ["DeckType", "Deck", "Route", "TurboliftSubsystem", "TurboliftSystem", "getTurboliftSubsystem"]
