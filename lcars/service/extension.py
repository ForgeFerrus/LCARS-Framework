# ◤ TITANIUM EXTENSION SUBSYSTEM
# Файл: lcars/service/extension.py
# Призначення: Менеджер плагінів та розширень системи
# Керує завантаженням та реєстрацією зовнішніх модулів

from lcars.core.conduit import Service

# Сервіс розширень та плагінів
class ExtensionSubsystem(Service):
    def __init__(self):
        super().__init__()
        self.Name = "extension"
        self.Extensions = {}
        self.ExtensionDir = "plugins"

    # Реєстрація розширення за ім'ям та об'єктом
    def Register(self, Name: str, Extension: object) -> bool:
        if Name and Extension:
            self.Extensions[Name] = Extension
            return True
        return False

    # Зняття з реєстрації розширення за ім'ям
    def Unregister(self, Name: str) -> bool:
        if Name in self.Extensions:
            del self.Extensions[Name]
            return True
        return False

    # Отримання розширення за ім'ям
    def Get(self, Name: str):
        return self.Extensions.get(Name)

    # Список зареєстрованих розширень
    def ListExtensions(self):
        return list(self.Extensions.keys())

    # Кількість зареєстрованих розширень
    def Count(self):
        return len(self.Extensions)

    # Перевірка наявності розширення
    def Has(self, Name: str) -> bool:
        return Name in self.Extensions

    # Очищення всіх розширень
    def Clear(self):
        self.Extensions.clear()
