# ◤ TITANIUM HOLODECK SERVICE
# Файл: lcars/service/holodeck.py

import logging
from lcars.core.service import Service
from lcars.core.matrix import SystemMatrix

log = logging.getLogger("Holodeck")

# Ядро голографічної системи для створення віртуальних середовищ
class HolodeckCore(Service):
    def __init__(self):
        super().__init__()
        self.Name = "holodeck"
        self.ActiveProgram = None
        self.HoloMatrix = SystemMatrix([50, 50, 50], Id="HolodeckGrid-1")
        
    # Запуск системи голографічного проєктування
    def OnStart(self) -> None:
        log.info("Holodeck power systems initialized. Ready for programs.")
        
    # Зупинка голографічної системи
    def OnStop(self) -> None:
        self.StopProgram()
        log.info("Holodeck systems offline.")

    # Завантаження голографічної програми з імітацією матерії
    def LoadProgram(self, name: str):
        self.ActiveProgram = name
        log.info(f"Loading holo-program: {name}")
        
        # Simulate loading matter into the matrix
        import random
        # Resize grid dynamically based on "complexity"
        complexity = random.choice([30, 50, 80])
        self.HoloMatrix.Resize([complexity, complexity, complexity])
        
        self.HoloMatrix.Clear()
        
        # Fill it with random photon matter
        for _ in range(1000):
            x = random.randint(0, complexity - 1)
            y = random.randint(0, complexity - 1)
            z = random.randint(0, complexity - 1)
            matter_type = random.choice(["WOOD", "WATER", "METAL", "BIO", "ENERGY"])
            self.HoloMatrix.SetData(x, y, z, matter_type)
            
        log.info(f"Hologrid populated with {self.HoloMatrix.GetSize()} photon particles.")

    # Зупинка поточної голографічної програми
    def StopProgram(self):
        if self.ActiveProgram:
            log.info(f"Ending holo-program: {self.ActiveProgram}")
            self.HoloMatrix.Clear()
            self.ActiveProgram = None

    # Отримання статусу голографічної системи
    def GetStatus(self):
        return {
            "program": self.ActiveProgram or "IDLE",
            "particles": self.HoloMatrix.GetSize(),
            "dimensions": self.HoloMatrix.Dimensions
        }
