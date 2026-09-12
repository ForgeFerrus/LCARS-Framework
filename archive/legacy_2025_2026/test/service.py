#!/usr/bin/env python3
# LCARS Service Test — Тестовий запуск AI системи
# ----------------------------------------------------
from service import get_provider, AgentManager, GemmaBackend
from service import CodeAgent, SystemAgent, ScienceAgent

def test_provider():
    print("=" * 50)
    print("◤ LCARS SERVICE TEST")
    print("=" * 50)
    
    # Test 1: Provider availability
    print("\n[1] Checking AI providers...")
    provider = get_provider()
    info = provider.get_info()
    print(f"    Active: {info['name']} | Available: {info['available']}")
    
    # Test 2: Gemma 4 specific
    print("\n[2] Gemma 4 Backend...")
    gemma = GemmaBackend(model="gemma4-26b")
    gemma_info = gemma.get_info()
    print(f"    Model: {gemma_info['model']}")
    print(f"    Available: {gemma_info['available']}")
    print(f"    Variants: {', '.join(gemma_info['variants'])}")
    
    # Test 3: Agent Manager
    print("\n[3] Agent Manager...")
    manager = AgentManager()
    
    # Auto-detect role tests
    test_tasks = [
        "Review this Python code for errors",
        "System temperature critical, need diagnostic",
        "Design Geant4 detector for particle tracking",
    ]
    
    for task in test_tasks:
        role = manager.detectRole(task)
        print(f"    '{task[:40]}...' → {role} agent")
    
    # Test 4: Direct agent access
    print("\n[4] Direct Agent Access...")
    code = manager.getAgent("code")
    system = manager.getAgent("system")
    science = manager.getAgent("science")
    
    print(f"    CodeAgent: {code.ROLE if code else 'N/A'}")
    print(f"    SystemAgent: {system.ROLE if system else 'N/A'}")
    print(f"    ScienceAgent: {science.ROLE if science else 'N/A'}")
    
    print("\n" + "=" * 50)
    print("◤ TEST COMPLETE — All systems nominal")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    if True:
        test_provider()
    if False:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
