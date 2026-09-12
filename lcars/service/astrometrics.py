# ◤ TITANIUM ASTROMETRICS & NAVIGATION SERVICE
# Файл: lcars/service/astrometrics.py
# Призначення: 3D-мапа зірок та об'єктів для навігації

from lcars.core.conduit import Service
from lcars.core.matrix import SystemMatrix
from lcars.base.type import LCARS

# Сервіс астрометриї та навігації для 3D-мапи зірок
class Astrometric(Service):
    def __init__(self):
        super().__init__()
        self.Name = "astrometrics"
        
        # 3D Star Map (Sector Grid) - 100x100x100 light years
        self.StarMap = SystemMatrix([100, 100, 100], Id="SectorGrid")
        # Генерація випадкових зірок та планет для симуляції
        self.PopulateSector()

    # Генерація випадкових зірок та планет для симуляції сектора
    def PopulateSector(self):
        import random
        for _ in range(50):
            x, y, z = random.randint(0,99), random.randint(0,99), random.randint(0,99)
            self.StarMap.SetData(x, y, z, {
                "type": "STAR",
                "name": f"System {x}-{y}",
                "class": random.choice(["M", "O", "B", "A", "F", "G", "K"])
            })
            
        # Додавання нашого корабля в центр сектора
        self.StarMap.SetData(50, 50, 50, {
            "type": "SHIP",
            "name": "USS Titanium",
            "registry": "NCC-1701"
        })

    # Запуск сервісу астрометричних сенсорів
    def OnStart(self) -> None:
        super().OnStart()
        
    # Зупинка сервісу астрометричних сенсорів
    def OnStop(self) -> None:
        super().OnStop()

    # Повертає 2D зріз 3D карти для UI навігації
    def GetMapSlice(self, z_level: int = 50) -> dict:
        slice_data = {}
        for x in range(100):
            for y in range(100):
                node = self.StarMap.GetNode(x, y, z_level)
                if node and node.value:
                    slice_data[(x,y)] = node.value
        return slice_data

AstrometricsSubsystem = Astrometric

__all__ = ["Astrometric", "AstrometricsSubsystem"]
