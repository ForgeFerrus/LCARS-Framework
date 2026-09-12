from __future__ import annotations
# Titanium Bridge Migration: from typing import Dict, List, Any, Optional
from lcars.service.quantum import get_quantum_service

class QuantumLab:
    def __init__(self):
        self.experiments: List[Dict] = []
        self.active_circuit: Optional[Any] = None
        self.quantum = get_quantum_service()
        
    def new_experiment(self, name: str, qubits: int) -> bool:
        circuit = self.quantum.create_circuit(qubits)
        if circuit:
            self.active_circuit = circuit
            self.experiments.append({
                "name": name,
                "qubits": qubits,
                "circuit": circuit,
                "status": "active"
            })
            return True
        return False
        
    def add_hadamard(self, target: int) -> bool:
        if not self.active_circuit:
            return False
        return self.quantum.add_gate(self.active_circuit, "h", target)
        
    def add_x_gate(self, target: int) -> bool:
        if not self.active_circuit:
            return False
        return self.quantum.add_gate(self.active_circuit, "x", target)
        
    def add_cnot(self, control: int, target: int) -> bool:
        if not self.active_circuit:
            return False
        return self.quantum.add_gate(self.active_circuit, "cx", target, control)
        
    def measure(self, target: int) -> bool:
        if not self.active_circuit:
            return False
        return self.quantum.add_gate(self.active_circuit, "measure", target)
        
    def run(self, shots: int = 1024) -> Optional[Dict]:
        if not self.active_circuit:
            return None
        return self.quantum.execute(self.active_circuit, shots)
        
    def get_stats(self) -> Dict:
        return {
            "experiments": len(self.experiments),
            "quantum_available": self.quantum.has_qiskit,
            "active": self.active_circuit is not None
        }
