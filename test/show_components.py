import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lcars.base.type import LCARS

print("=" * 80)
print("◤ LCARS FRAMEWORK — COMPLETE COMPONENT STRUCTURE ◢")
print("=" * 80)
print()

print("СТРУКТУРА КОМПОНЕНТІВ LCARS BASE:")
print("-" * 80)

# Отримуємо всі компоненти з lcars.base.component
import lcars.base.component as component_module

print()
print("КЛАСИ В lcars.base.component:")
print("-" * 80)

component_classes = []
for name in dir(component_module):
    if not name.startswith('_'):
        obj = getattr(component_module, name)
        if isinstance(obj, type):
            component_classes.append((name, obj))

for name, cls in sorted(component_classes):
    module_name = cls.__module__
    class_name = cls.__name__
    print(f"  {class_name:25s} | Модуль: {module_name}")

print()
print("=" * 80)
print("ІМПОРТУВАННЯ ВСІХ КОМПОНЕНТІВ:")
print("-" * 80)

from lcars.base.component import (
    Graphic,
    Component,
    Primitive,
    LCARSButton,
    Button1,
    Button2,
    Button3,
    Button4,
    Button5,
    PillButton,
    RectButton,
    LeftRoundButton,
    RightRoundButton,
    LCARSLabel,
    Label1,
    LCARSElbow,
    Elbow1,
    Elbow2,
    Elbow3,
    Elbow4,
    LCARSBar,
    LCARSContour,
    LCARSDivider,
    LCARSDataBlock,
    LCARSStatBar,
    LCARSPadd
)

print("  ✅ Усі компоненти успішно імпортовано")
print()
print("=" * 80)
print("ВЕРХІВНЯ РОДСТВА КОМПОНЕНТІВ:")
print("-" * 80)

print()
print("Graphic (базовий клас для всіх графічних елементів)")
print("  ├─ Primitive (примітиви для малювання)")
print("  ├─ Component (контейнер для елементів)")
print("  ├─ LCARSButton (базова кнопка)")
print("  │   ├─ Button1 (кнопка типу 1)")
print("  │   ├─ Button2 (кнопка типу 2)")
print("  │   ├─ Button3 (кнопка типу 3)")
print("  │   ├─ Button4 (кнопка типу 4)")
print("  │   ├─ Button5 (кнопка типу 5)")
print("  │   ├─ PillButton (овальна кнопка)")
print("  │   ├─ RectButton (прямокутна кнопка)")
print("  │   ├─ LeftRoundButton (кнопка з лівим заокругленням)")
print("  │   └─ RightRoundButton (кнопка з правим заокругленням)")
print("  ├─ LCARSLabel (базовий лейбл)")
print("  │   └─ Label1 (лейбл типу 1)")
print("  ├─ LCARSElbow (базовий ельбоу - кутовий елемент)")
print("  │   ├─ Elbow1 (ельбоу типу 1)")
print("  │   ├─ Elbow2 (ельбоу типу 2)")
print("  │   ├─ Elbow3 (ельбоу типу 3)")
print("  │   └─ Elbow4 (ельбоу типу 4)")
print("  ├─ LCARSBar (базова смуга)")
print("  │   └─ LCARSContour (контурна смуга)")
print("  ├─ LCARSDivider (роздільник)")
print("  ├─ LCARSDataBlock (блок даних)")
print("  └─ LCARSStatBar (статусна смуга)")

print()
print("=" * 80)
print("СТАТУС ВІЗУАЛЬНИХ КОМПОНЕНТІВ:")
print("-" * 80)

from lcars.base.register import registry
visual_keys = [key for key in registry.List() if key.startswith('Visual.')]
available_visual = sum(1 for key in visual_keys if registry.Has(key))
total_visual = len(visual_keys)
percentage = int((available_visual / total_visual) * 100) if total_visual > 0 else 0

print(f"  Visual сектор: {available_visual}/{total_visual} доступно ({percentage}%)")
print()
print("Деякі доступні візуальні компоненти:")
visual_samples = [
    'Visual.Bitmap',
    'Visual.Brush', 
    'Visual.Clipboard',
    'Visual.Color',
    'Visual.Font',
    'Visual.Painter',
    'Visual.Pixmap',
]
for sample in visual_samples[:10]:
    status = "✅ Доступно" if registry.Has(sample) else "❌ Недоступно"
    print(f"  {status} | {sample}")

print()
print("=" * 80)
print("◤ СТРУКТУРА ЗАВЕРШЕНА ◢")
print("=" * 80)
