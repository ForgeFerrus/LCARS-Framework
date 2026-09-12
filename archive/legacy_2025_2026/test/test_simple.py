#!/usr/bin/env python3
"""
LCARS Service — Простий тест запуску
"""

print("◤ LCARS SERVICE TEST")
print("=" * 40)

# Test 1: Provider imports
print("\n[1] Testing provider imports...")
try:
    from service.provider import AIProviderManager, GemmaBackend, get_provider
    print("    ✓ provider.py OK")
except Exception as e:
    print(f"    ✗ provider.py: {e}")

# Test 2: Copilot imports  
print("\n[2] Testing copilot imports...")
try:
    from service.copilot import Copilot, AgentManager
    print("    ✓ copilot.py OK")
except Exception as e:
    print(f"    ✗ copilot.py: {e}")

# Test 3: Service package
print("\n[3] Testing service package...")
try:
    from service import get_provider, GemmaBackend, AgentManager
    print("    ✓ service/__init__.py OK")
except Exception as e:
    print(f"    ✗ service/__init__.py: {e}")

# Test 4: Basic instantiation
print("\n[4] Testing basic instantiation...")
try:
    from service import GemmaBackend
    gemma = GemmaBackend()
    info = gemma.get_info()
    print(f"    ✓ GemmaBackend: {info['name']} | variants: {len(info['variants'])}")
except Exception as e:
    print(f"    ✗ GemmaBackend: {e}")

print("\n" + "=" * 40)
print("◤ TEST COMPLETE")
