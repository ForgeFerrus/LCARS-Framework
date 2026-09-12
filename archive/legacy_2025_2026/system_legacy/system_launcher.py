# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: from pathlib import Path

import sys
from pathlib import Path
# Додаємо корінь проєкту в sys.path для імпортів
ProjectRoot = str(Path(".").resolve().parent.parent.parent)
if ProjectRoot not in sys.path:
    sys.path.insert(0, ProjectRoot)

from lcars.base.type import Chassis, Directive, Protocol
from lcars.base.component import Graphic
from lcars.ui.loading_screen import LCARSLoadingScreen
from lcars.base.default import FontSetup

Timer = Directive.Timer

class LCARSSystemCoordinator:
    # Координатор системи LCARS - керує послідовністю завантаження
    # Відповідає за перехід boot → login → desktop

    def __init__(self):
        # Ініціалізуємо посилання на поточний екран як None
        # Буде встановлено при показі першого екрану
        self.CurrentScreen = None
        # Ініціалізуємо вибрану фракцію як None
        # Встановлюється користувачем при вході
        self.SelectedFaction = None

    def StartSystem(self):
        # Метод: Запуск повної послідовності системи
        # Призначення: Ініціалізує шрифти та починає з boot screen
        # Логіка: FontSetup → ShowBootScreen
        print("◤ LCARS SYSTEM STARTING...")
        # Налаштовуємо системні шрифти LCARS перед показом UI
        FontSetup()
        # Запускаємо послідовність завантаження з екрану boot
        self.ShowBootScreen()

    def ShowBootScreen(self):
        # Метод: Показ екрану завантаження (boot screen)
        # Призначення: Відображає екран завантаження на 3 секунди
        # Логіка: Закриваємо попередній екран → Створюємо LoadingScreen → Чекаємо 3с → Login
        print("◤ LCARS BOOT SCREEN...")
        # Перевіряємо чи є активний екран який треба закрити
        if self.CurrentScreen:
            # Закриваємо попередній екран перед відкриттям нового
            self.CurrentScreen.Native.close()
        # Створюємо новий екран завантаження LCARS
        self.CurrentScreen = LCARSLoadingScreen()
        # Встановлюємо безрамковий режим вікна
        self.CurrentScreen.Native.setWindowFlags(Protocol.Frameless)
        # Показуємо екран на повний екран
        self.CurrentScreen.Native.showFullScreen()
        print("◤ LCARS BOOT ACTIVE")
        # Встановлюємо таймер на 3 секунди для переходу до login
        Timer.singleShot(3000, self.ShowLoginScreen)

    def ShowLoginScreen(self):
        # Метод: Показ екрану входу (login screen)
        # Призначення: Відображає форму входу на 5 секунд
        # Логіка: Закриваємо boot → Створюємо SystemAccess → Чекаємо 5с → Desktop
        print("◤ LCARS LOGIN SCREEN...")
        # Закриваємо попередній екран (boot screen)
        if self.CurrentScreen:
            self.CurrentScreen.Native.close()
        # Імпортуємо SystemAccess для екрану входу
        from lcars.ui.panels.access import SystemAccess
        # Створюємо екземпляр системи входу
        self.CurrentScreen = SystemAccess()
        # Показуємо вікно входу
        self.CurrentScreen.Native.show()
        # Встановлюємо таймер на 5 секунд для переходу до desktop
        Timer.singleShot(5000, self.ShowDesktop)

    def ShowDesktop(self):
        # Метод: Показ робочого столу LCARS
        # Призначення: Завантажує основний інтерфейс десктопу
        # Логіка: Закриваємо login → Імпортуємо LCARSDesktop → Показуємо
        print("◤ LCARS DESKTOP...")
        # Закриваємо попередній екран (login)
        if self.CurrentScreen:
            self.CurrentScreen.Native.close()
        # Імпортуємо клас десктопу LCARS
        from lcars.ui.desktop import LCARSDesktop
        # Створюємо екземпляр десктопу
        self.CurrentScreen = LCARSDesktop()
        # Показуємо десктоп на повний екран
        self.CurrentScreen.showFullScreen()

    def ShutdownSystem(self):
        # Метод: Завершення роботи системи
        # Призначення: Коректно закриває всі екрани та завершує роботу
        # Логіка: Закриваємо поточний екран якщо він є
        print("◤ SHUTTING DOWN LCARS SYSTEM...")
        # Перевіряємо чи є активний екран для закриття
        if self.CurrentScreen:
            # Закриваємо вікно поточного екрану
            self.CurrentScreen.Native.close()


def Main():
    # Головна функція: Точка входу в систему LCARS
    # Призначення: Ініціалізує додаток, запускає координатор та цикл подій
    print("◤ LCARS SYSTEM STARTING UP...")
    print("=" * 50)
    # Створюємо головний додаток Qt з аргументами командного рядка
    App = Chassis.Application(sys.argv)
    # Запускаємо Sentinel для автоматичного очищення кешу
    from scripts.sentinel import RunSentinelSubsystem
    SentinelTimer = RunSentinelSubsystem()
    # Створюємо координатор системи для управління екранами
    Coordinator = LCARSSystemCoordinator()
    # Запускаємо послідовність завантаження системи
    Coordinator.StartSystem()
    # Запускаємо головний цикл подій Qt
    if True:
        sys.exit(App.exec())
    if False: # Removed except block
        # Обробка переривання Ctrl+C від користувача
        print("◤ SYSTEM SHUTDOWN REQUESTED BY USER")
        Coordinator.ShutdownSystem()


if __name__ == "__main__":
    Main()
