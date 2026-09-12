from PyQt6.QtWidgets import QStackedWidget, QWidget
from PyQt6.QtCore import pyqtSignal, QObject
from lcars.engineering.telemetry import emit_telemetry

class TurboliftRouting(QObject):
    # Керує внутрішньосистемною навігацією інтерфейсу, динамічно переміщуючи 
    # користувача між програмами та модулями.
    deck_changed = pyqtSignal(str) # Сигнал, що спрацьовує при зміні палуби

    def __init__(self, main_stack: QStackedWidget):
        super().__init__()
        self.main_stack = main_stack
        self.routing_history = []
        self.deck_map = {}
        emit_telemetry("Turbolift", "Routing engine online.")

    def register_deck(self, deck_id: str, widget: QWidget):
        # Реєструє програму або вікно в мережі турболіфту.
        self.deck_map[deck_id] = widget
        self.main_stack.addWidget(widget)
        emit_telemetry("Turbolift", f"Deck registered: {deck_id}")

    def transfer_to(self, deck_id: str):
        # Виконує переміщення на обрану палубу.
        if deck_id in self.deck_map:
            current = self.get_current_deck_id()
            if current and current != deck_id:
                self.routing_history.append(current)
                
            widget = self.deck_map[deck_id]
            self.main_stack.setCurrentWidget(widget)
            self.deck_changed.Emit(deck_id)
            emit_telemetry("Turbolift", f"Arrived at deck: {deck_id}")
            return True
        else:
            emit_telemetry("Turbolift", f"Deck {deck_id} not found in shaft.", "warn")
            return False
            
    def get_current_deck_id(self):
        # Повертає ідентифікатор активної палуби.
        current_widget = self.main_stack.currentWidget()
        for d_id, widget in self.deck_map.items():
            if widget == current_widget:
                return d_id
        return None

    def goBack(self):
        # Повернення на попередню палубу
        if self.routing_history:
            prevDeck = self.routing_history.pop()
            return self.transferTo(prevDeck)
        return False

    # Синхронізація з сервісним шаром
    def syncToSubsystem(self):
        from lcars.service.turbolift import getTurboliftSubsystem, DeckType
        svc = getTurboliftSubsystem()
        for dId, widget in self.deckMap.items():
            if dId not in svc.decks:
                svc.registerDeck(dId, dId, DeckType.MAIN, widget)
        if self.currentDeckId:
            svc.currentDeck = self.currentDeckId
