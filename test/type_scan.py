# test_chain.py
import sys
from lcars.base.type import LCARS

def RunChainDiagnostics():
    print("=" * 60)
    print("  LCARS DOT-CHAIN & RETRIEVE DIAGNOSTIC PROTOCOL")
    print("=" * 60)
    
    Errors = []

    # ТЕСТ 1: Перевірка існування кореня LCARS
    print("\n[ТЕСТ 1] Перевірка ядра LCARS...")
    if hasattr(LCARS, "Name"):
        print(f"  -> OK: Базове ядро активне: {LCARS.Name}")
    else:
        Errors.append("LCARS не має базових атрибутів")

    # ТЕСТ 2: Побудова ланцюжка Geometry (RectF / PointF)
    print("\n[ТЕСТ 2] Побудова ланцюжка Geometry -> RectF...")
    try:
        RectFClass = LCARS.Geometry.RectF
        print(f"  -> Отримано вузол: {RectFClass}")
        if RectFClass is not None:
            # Перевірка працездатності екземпляра
            Instance = RectFClass(0.0, 0.0, 100.0, 50.0)
            print(f"  -> OK: Створено екземпляр: {Instance}, ширина={Instance.width()}")
        else:
            Errors.append("LCARS.Geometry.RectF повернув None")
    except Exception as e:
        Errors.append(f"Помилка LCARS.Geometry.RectF: {e}")

    # ТЕСТ 3: Побудова ланцюжка Visual -> PainterPath
    print("\n[ТЕСТ 3] Побудова ланцюжка Visual -> PainterPath...")
    try:
        PainterPathClass = LCARS.Visual.PainterPath
        print(f"  -> Отримано вузол: {PainterPathClass}")
        if PainterPathClass is not None:
            PathInstance = PainterPathClass()
            print(f"  -> OK: Створено траєкторію PainterPath: {PathInstance}")
        else:
            Errors.append("LCARS.Visual.PainterPath повернув None")
    except Exception as e:
        Errors.append(f"Помилка LCARS.Visual.PainterPath: {e}")

    # ТЕСТ 4: Глибокий системний ланцюжок System -> Module -> Import
    print("\n[ТЕСТ 4] Глибокий системний ланцюг: LCARS.System.Module.Import...")
    try:
        ModuleImportFunc = LCARS.System.Module.Import
        print(f"  -> Отримано функцію: {ModuleImportFunc}")
        if callable(ModuleImportFunc):
            TestMod = ModuleImportFunc("math")
            print(f"  -> OK: Імпорт через ланцюг спрацював: модуль {TestMod.__name__}, pi={TestMod.pi}")
        else:
            Errors.append("LCARS.System.Module.Import не є функцією")
    except Exception as e:
        Errors.append(f"Помилка LCARS.System.Module.Import: {e}")

    # ТЕСТ 5: Перевірка проміжної ланки (не листок, а буфер)
    print("\n[ТЕСТ 5] Перевірка проміжної ланки (Namespace)...")
    try:
        VisualNode = LCARS.Visual
        Buffer = getattr(VisualNode, "PatternBuffer", None)
        print(f"  -> Вузол LCARS.Visual: {VisualNode}, PatternBuffer='{Buffer}'")
        if Buffer == "Base.Visual":
            print("  -> OK: Буфер побудовано коректно: Base.Visual")
        else:
            Errors.append(f"Невірний буфер для Visual: {Buffer}")
    except Exception as e:
        Errors.append(f"Помилка буфера Visual: {e}")

    # ПІДСУМОК
    print("\n" + "=" * 60)
    if not Errors:
        print("  РЕЗУЛЬТАТ: УСІ ТЕСТИ ПРОЙДЕНО! Ланцюжки будуються і читаються!")
    else:
        print(f"  РЕЗУЛЬТАТ: ВИЯВЛЕНО ПОМИЛОК: {len(Errors)}")
        for err in Errors:
            print(f"    [X] {err}")
    print("=" * 60)

if __name__ == "__main__":
    RunChainDiagnostics()