#!/usr/bin/env python3
# ◤ ТЕСТУВАННЯ СИСТЕМИ ЗАВАНТАЖЕННЯ LCARS ◢

import sys
from pathlib import Path

# Додавання проекту до Python path
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

print("="*60)
print("◤ LCARS BOOT SYSTEM TEST")
print("="*60)

# Тест 1: Запуск BIOS boot screen
print("\n1. Testing BIOS Boot Screen...")
try:
    from lcars.ui.screen.boot import run_bios
    print("✓ BIOS boot screen available")
    print("  Run: python -c \"from lcars.ui.screen.boot import run_bios; run_bios()\"")
except Exception as e:
    print(f"✗ BIOS boot screen failed: {e}")

# Тест 2: Тест системи boot
print("\n2. Testing System Boot...")
try:
    from lcars.system.boot import quickBoot, EmergencyMode, QuickSystemCheck
    print("✓ System boot components available")
    
    # Тест швидкої перевірки
    checker = QuickSystemCheck()
    checker.init()
    success = checker.run()
    report = checker.getReport()
    print(f"  Quick check: {report['status']}")
    if report['errors']:
        print(f"  Errors: {report['errors']}")
    if report['warnings']:
        print(f"  Warnings: {report['warnings']}")
        
except Exception as e:
    print(f"✗ System boot failed: {e}")

# Тест 3: Тест Emergency Mode
print("\n3. Testing Emergency Mode...")
try:
    emergency = EmergencyMode()
    emergency.init({"error": "Test error", "stage": "TEST"})
    print("✓ Emergency mode available")
    print("  Note: UI will be shown if GUI available")
except Exception as e:
    print(f"✗ Emergency mode failed: {e}")

# Тест 4: Тест Bootstrap
print("\n4. Testing Bootstrap...")
try:
    from lcars.core.bootstrap import Start, StartEmergency, StartBootScreen
    print("✓ Bootstrap functions available")
    print("  Functions: Start(), StartEmergency(), StartBootScreen()")
except Exception as e:
    print(f"✗ Bootstrap failed: {e}")

print("\n" + "="*60)
print("◤ BOOT SYSTEM READY")
print("="*60)
print("\nUsage examples:")
print("  1. Normal boot: python -c \"from lcars.core.bootstrap import Start; Start()\"")
print("  2. BIOS screen: python -c \"from lcars.core.bootstrap import StartBootScreen; StartBootScreen()\"")
print("  3. Emergency: python -c \"from lcars.core.bootstrap import StartEmergency; StartEmergency()\"")
print("="*60)
