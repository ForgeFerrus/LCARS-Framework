# Central system error types for LCARS.
# Це центральне місце, де визначаються базові системні винятки, які
# можуть використовуватись у всьому LCARS. Інші модулі можуть імпортувати
# їх звідси.
# Для зворотної сумісності старі імпорти з lcars.base.errors також працюють.

class LCARSError(Exception):
    # Базове виключення для LCARS (всі системні помилки мають успадковуватись від нього).
    pass

class ComponentNotFound(LCARSError):
    # Помилка, яка кидається, коли компонент не знайдений у реєстрі.
    pass

PublicExports = ["LCARSError", "ComponentNotFound"]
