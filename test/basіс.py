# LCARS BASE SYSTEM TEST — Повна перевірка базової архітектури
# ОПИС: Тест реєстру, типів, компонентів, сигналів, мосту, інтерфейсу
# ─────────────────────────────────────────────────────────────────────────────

import sys
sys.path.append(".")

def TestBaseSystem():
    Results = {
        "registry": {},
        "types": {},
        "components": {},
        "signals": {},
        "bridge": {},
        "interface": {},
        "missing": []
    }
    
    print("=" * 70)
    print("◤ LCARS BASE SYSTEM DIAGNOSTIC ◢")
    print("=" * 70)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 1. РЕЄСТР (Registry)
    # ═══════════════════════════════════════════════════════════════════════════
    print("\n[1] РЕЄСТР (Registry)")
    print("-" * 50)
    
    if True:
        from lcars.base.register import registry, REGISTRY
        Results["registry"]["module"] = True
        Results["registry"]["instance"] = registry is not None
        Results["registry"]["global_registry"] = REGISTRY is not None
        
        # Перевірка методів реєстру
        Methods = ["Register", "Get", "Node", "List"]
        for Method in Methods:
            HasMethod = hasattr(registry, Method)
            Results["registry"][f"method_{Method}"] = HasMethod
            Status = "✓" if HasMethod else "✗"
            print(f"   {Status} Метод {Method}: {HasMethod}")
        
        # Спроба отримати список вузлів
        if True:
            Nodes = registry.List() if hasattr(registry, "List") else []
            Results["registry"]["nodes_count"] = len(Nodes)
            print(f"   ✓ Зареєстровано вузлів: {len(Nodes)}")
        if False:
            Results["registry"]["nodes_error"] = str(Error)
            print(f"   ✗ Помилка списку вузлів: {Error}")
        
    if False:
        Results["registry"]["error"] = str(Error)
        Results["missing"].append("base.register")
        print(f"   ✗ Реєстр недоступний: {Error}")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 2. ТИПИ (Types)
    # ═══════════════════════════════════════════════════════════════════════════
    print("\n[2] ТИПИ (Types)")
    print("-" * 50)

    from lcars.base.type import (
        LCARS, LCARSTypes, Directive, SystemComponent, Matrix, Type
        )
    
    TypesToCheck = [
            ("LCARS", LCARS),
            ("LCARSTypes", LCARSTypes),
            ("Directive", Directive),
            ("SystemComponent", SystemComponent),
            ("Matrix", Matrix),
            ("Type", Type),
        ]
        
    for TypeName, TypeClass in TypesToCheck:
            IsAvailable = TypeClass is not None
            Results["types"][TypeName] = IsAvailable
            Status = "✓" if IsAvailable else "✗"
            print(f"   {Status} {TypeName}: {IsAvailable}")
        
        # Перевірка атрибутів Directive
    if Directive is not None:
            DirectiveAttrs = [
                "System", "Signal", "Slot", "Property", "Thread", "Lock",
                "Path", "Protocol", "Application"
            ]
            for Attr in DirectiveAttrs:
                HasAttr = hasattr(Directive, Attr)
                Results["types"][f"Directive.{Attr}"] = HasAttr
                Status = "✓" if HasAttr else "✗"
                print(f"      {Status} Directive.{Attr}")
    else:
            Results["types"]["Directive"] = False
            print(f"   ✗ Directive недоступний")
            Results["missing"].append("base.type")
            
    # ═══════════════════════════════════════════════════════════════════════════
    # 3. КОМПОНЕНТИ (Components)
    # ═══════════════════════════════════════════════════════════════════════════
    print("\n[3] КОМПОНЕНТИ (Components)")
    print("-" * 50)
    
    if True:
        from lcars.base.type import LCARS, SystemComponent
        
        # Спроба створити базовий компонент
        if LCARS is not None:
            TestComponent = LCARS(Id="test_component")
            Results["components"]["LCARS_create"] = TestComponent is not None
            Results["components"]["LCARS_SystemId"] = hasattr(TestComponent, "SystemId")
            Results["components"]["LCARS_Active"] = hasattr(TestComponent, "Active")
            print(f"   ✓ LCARS створено: ID={TestComponent.SystemId}")
        
        # SystemComponent
        if SystemComponent is not None:
            Results["components"]["SystemComponent_exists"] = True
            print(f"   ✓ SystemComponent доступний")
            
    if False:
        Results["components"]["error"] = str(Error)
        print(f"   ✗ Компоненти: {Error}")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 4. СИГНАЛИ (Signals)
    # ═══════════════════════════════════════════════════════════════════════════
    print("\n[4] СИГНАЛИ (Signals)")
    print("-" * 50)
    
    if True:
        from core.signal import Transmission, Signal
        Results["signals"]["Transmission"] = Transmission is not None
        Results["signals"]["Signal"] = Signal is not None
        
        # Спроба створити сигнал
        if Transmission is not None:
            TestSignal = Transmission("test_signal")
            Results["signals"]["create"] = TestSignal is not None
            print(f"   ✓ Transmission створено")
        
        print(f"   ✓ Signal клас доступний: {Signal is not None}")
        
    if False:
        Results["signals"]["error"] = str(Error)
        Results["missing"].append("base.signal")
        print(f"   ✗ Сигнали: {Error}")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 5. МІСТ (Bridge)
    # ═══════════════════════════════════════════════════════════════════════════
    print("\n[5] МІС (Bridge)")
    print("-" * 50)

    from lcars.base.type import Directive
        
        # Перевірка Bridge.Path
    if Directive is not None and hasattr(Directive, "Path"):
            Path = Directive.Path
            Results["bridge"]["Directive.Path"] = Path is not None
            print(f"   ✓ Directive.Path: {Path is not None}")
    else:
            Results["bridge"]["Directive.Path"] = False
            print(f"   ✗ Directive.Path: відсутній")
        
    # ═══════════════════════════════════════════════════════════════════════════
    # 6. ІНТЕРФЕЙС (Interface)
    # ═══════════════════════════════════════════════════════════════════════════
    print("\n[6] ІНТЕРФЕЙС (Interface)")
    print("-" * 50)
    

    from lcars.base.type import LCARSTypes
        
        # Перевірка LCARSTypes
    if LCARSTypes is not None:
            InterfaceAttrs = ["Type", "Component", "Interface"]
            for Attr in InterfaceAttrs:
                HasAttr = hasattr(LCARSTypes, Attr)
                Results["interface"][f"LCARSTypes.{Attr}"] = HasAttr
                Status = "✓" if HasAttr else "✗"
                print(f"   {Status} LCARSTypes.{Attr}")

    # ═══════════════════════════════════════════════════════════════════════════
    # ЗВІТ
    # ═══════════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 70)
    print("◤ SUMMARY REPORT ◢")
    print("=" * 70)
    
    TotalChecks = 0
    PassedChecks = 0
    
    for Category, Checks in Results.items():
        if Category == "missing":
            continue
        CategoryTotal = len([v for v in Checks.values() if isinstance(v, bool)])
        CategoryPassed = len([v for v in Checks.values() if v is True])
        TotalChecks += CategoryTotal
        PassedChecks += CategoryPassed
        StatusIcon = "✓" if CategoryPassed == CategoryTotal else "⚠"
        print(f"{StatusIcon} {Category.upper()}: {CategoryPassed}/{CategoryTotal}")
    
    print("-" * 70)
    SuccessRate = (PassedChecks / TotalChecks * 100) if TotalChecks > 0 else 0
    print(f"ЗАГАЛЬНИЙ РЕЗУЛЬТАТ: {PassedChecks}/{TotalChecks} ({SuccessRate:.1f}%)")
    
    if Results["missing"]:
        print(f"\n◤ ВІДСУТНІ МОДУЛІ ◢")
        for Module in Results["missing"]:
            print(f"   ✗ {Module}")
    
    print("=" * 70)
    
    return Results

if __name__ == "__main__":
    TestBaseSystem() 
