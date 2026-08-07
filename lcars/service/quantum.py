from __future__ import annotations
import random
import importlib.util
from typing import List, Dict, Any, Optional

# Квантовий сервіс для роботи з квантовими обчисленнями
class QuantumService:
    def __init__(self):
        self.backend = None
        self.has_qiskit = False
        self.circuits: List[Any] = []
        self.checkDeps()
    
    # Перевірка наявності залежностей qiskit та qiskit_aer
    def checkDeps(self):
        self.hasQiskit = importlib.util.find_spec("qiskit") is not None and importlib.util.find_spec("qiskit_aer") is not None
    
    # Створення квантового кола з вказаною кількістю кубітів
    def createCircuit(self, numQubits: int) -> Optional[Any]:
        if not self.hasQiskit:
            return None
        from qiskit import QuantumCircuit
        circuit = QuantumCircuit(numQubits)
        self.circuits.append(circuit)
        return circuit
    
    # Додавання гейту до квантового кола
    def addGate(self, circuit: Any, gateType: str, target: int, control: Optional[int] = None) -> bool:
        if not circuit:
            return False
        if gateType == "h":
            circuit.h(target)
        elif gateType == "x":
            circuit.x(target)
        elif gateType == "cx" and control is not None:
            circuit.cx(control, target)
        elif gateType == "measure":
            circuit.measure(target, target)
        return True
    
    # Виконання квантового кола на симуляторі
    def execute(self, circuit: Any, shots: int = 1024) -> Optional[Dict]:
        if not self.hasQiskit or not circuit:
            return None
        from qiskit import transpile
        from qiskit_aer import Aer
        simulator = Aer.get_backend('qasm_simulator')
        compiled = transpile(circuit, simulator)
        job = simulator.run(compiled, shots=shots)
        result = job.result()
        return {
            "counts": result.get_counts(),
            "shots": shots,
            "success": True
        }
    
    # Отримання статистики квантового бекенду
    def GetStats(self) -> Dict[str, Any]:
        return {
            "backend": "qiskit" if self.hasQiskit else "none",
            "circuits": len(self.circuits),
            "available": self.hasQiskit
        }

# Глобальний екземпляр квантового сервісу (singleton)
QuantumServiceSingleton: Optional[QuantumService] = None

# Отримання або створення singleton-екземпляра квантового сервісу
def getQuantumService() -> QuantumService:
    global QuantumServiceSingleton
    if QuantumServiceSingleton is None:
        QuantumServiceSingleton = QuantumService()
    return QuantumServiceSingleton
