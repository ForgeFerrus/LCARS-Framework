"""
Qt Designer - Початківцям
==========================

КРОК 1: Запуск Qt Designer
─────────────────────────
Вже запущено! Вікно повинно бути видимо на екрані.
Якщо не видимо - запустіть файл: launch_designer.bat

КРОК 2: Створення нової форми
────────────────────────────
1. В Qt Designer: File → New → Dialog with Buttons Bottom
   (Вибираємо "Dialog" - це найпростіша форма)

2. Натисніть "Create"

Тепер ви бачите порожню форму з двома кнопками (OK, Cancel).

КРОК 3: Додавання компонентів
──────────────────────────────
На ЛІВІЙ стороні Qt Designer є "Widget Box" зі всіма компонентами:
┌────────────────┐
│ Widget Box     │
├────────────────┤
│ - Common       │
│  ├─ PushButton │  ← Кнопка
│  ├─ Label      │  ← Текст
│  ├─ LineEdit   │  ← Введення тексту
│  ├─ SpinBox    │  ← Число (ціле)
│  ├─ DoubleSpinBox │ ← Число (з комою)
│  ├─ ComboBox   │  ← Список (вибір)
│  └─ ...        │
│ - Containers   │
│  ├─ GroupBox   │  ← Група компонентів
│  └─ ...        │
│ - Input Widgets│
│  └─ ...        │
└────────────────┘

КРОК 4: Приклад - Форма для детектора
──────────────────────────────────────

Давайте створимо форму з параметрами детектора:

  ╔════════════════════════════╗
  ║   Crystal Parameters       ║
  ╠════════════════════════════╣
  ║                            ║
  ║  Radius: [2.0] ←────────   ║  (DoubleSpinBox)
  ║  Height: [2.0] ←────────   ║  (DoubleSpinBox)
  ║                            ║
  ║  Material: [Cobalt-59 ▼]   ║  (ComboBox)
  ║                            ║
  ║  Shield Thickness: [1.0]   ║  (DoubleSpinBox)
  ║                            ║
  ║  [Build] [Export] [Reset]  ║  (PushButton x3)
  ║                            ║
  ╚════════════════════════════╝

ЯК РОБИТИ:
──────────

1️⃣ Додайте Label "Radius:"
   - У Widget Box знайдіть "Label"
   - Перетягніть на форму
   - Напишіть текст "Radius:"

2️⃣ Додайте DoubleSpinBox праворуч
   - У Widget Box: Common → DoubleSpinBox
   - Перетягніть праворуч від Label

3️⃣ Повторіть для інших полів (Height, Material, Shield Thickness)

4️⃣ Додайте 3 кнопки (Build, Export, Reset)
   - Common → PushButton (3 рази)

5️⃣ ДУЖЕ ВАЖЛИВО: Задайте imena компонентів!
   ──────────────────────────────────────
   
   Натисніть на компонент, знизу в "Property Editor" змініть:
   - "objectName" (друге поле)
   
   Приклад:
   ┌─────────────────────┐
   │ Property Editor     │
   ├─────────────────────┤
   │ Property | Value    │
   │ ────────────────────│
   │ text | "Radius"     │  ← Це видиме текст на формі
   │ objectName | spinRadius │ ← ЦЕ НАЙВАЖЛИВІШЕ!
   │ value | 2.0         │
   │ ...                 │
   └─────────────────────┘
   
   НАЗВИ для компонентів:
   ─────────────────────
   - Label "Radius:" → label_radius
   - DoubleSpinBox → spin_radius
   - Label "Height:" → label_height
   - DoubleSpinBox → spin_height
   - Label "Material:" → label_material
   - ComboBox → combo_material
   - Label "Shield:" → label_shield
   - DoubleSpinBox → spin_shield
   - PushButton "Build" → btn_build
   - PushButton "Export" → btn_export
   - PushButton "Reset" → btn_reset

6️⃣ Розставте все в Grid Layout
   - Виберіть усі компоненти (Ctrl+A)
   - Натисніть Right Click
   - Lay Out → Layout in Grid
   
   (Або вручну перетягніть в сітку)

7️⃣ Збережіть форму
   - File → Save
   - Назва: detector_params.ui
   - Папка: lcars/ui/forms/
   
   ✅ Готово! Форма збережена як .ui файл

КРОК 5: Конвертація .ui файлу в Python код
───────────────────────────────────────────

Тепер треба перетворити .ui файл в Python код.

Запустіть в терміналі (в папці lcars/ui/forms/):

  pyuic6 -o detector_params.py detector_params.ui

Це створить файл detector_params.py з класом Ui_Dialog.

КРОК 6: Використання в коді
────────────────────────────

Тепер можна використовувати форму в коді:

  from lcars.ui.forms.detector_params import Ui_Dialog
  from PyQt6.QtWidgets import QDialog
  
  class DetectorParamsDialog(QDialog):
      def __init__(self):
          super().__init__()
          self.ui = Ui_Dialog()
          self.ui.setupUi(self)
          
          # Тепер можна використовувати всі компоненти!
          self.ui.spin_radius.setValue(3.0)
          self.ui.combo_material.addItems(["Co-59", "Lead", "Tungsten"])
          self.ui.btn_build.clicked.connect(self.on_build_clicked)
      
      def on_build_clicked(self):
          radius = self.ui.spin_radius.value()
          material = self.ui.combo_material.currentText()
          print(f"Building detector: radius={radius}, material={material}")

ПОРАДИ
──────

✅ Завжди перед збереженням задавайте objectName компонентам!
✅ Використовуйте мnemonic імена (spin_radius, btn_build, тощо)
✅ Розставляйте компоненти в Grid Layout, не вручну!
✅ Перевіряйте превю: View → Preview (Ctrl+Alt+P)
✅ Якщо щось не так - Edit → Undo (Ctrl+Z)

ПОМИЛКИ, ЯКІ ЧАСТО ТРАПЛЯЮТЬСЯ
───────────────────────────────

❌ "objectName" не заданий
   → Генерується код з назвами типу "pushButton_2"
   → Важко знайти в коді
   
   ✅ Рішення: Завжди задавайте objectName!

❌ Форма виглядає криво
   → Компоненти розставлені вручну
   
   ✅ Рішення: Виберіть все (Ctrl+A) → Right Click → Layout in Grid

❌ Значення не зберігаються
   → Забули задати "value" у DoubleSpinBox
   
   ✅ Рішення: Виберіть компонент → Property Editor → value

НАСТУПНІ КРОКИ
──────────────

1. Відкрийте Qt Designer вікно
2. Створіть нову форму (File → New → Dialog with Buttons Bottom)
3. Додайте компоненти за схемою вище
4. Задайте objectName кожному
5. Розставте в Grid Layout
6. Збережіть як detector_params.ui
7. Запустіть: pyuic6 -o detector_params.py detector_params.ui
8. Напишіть мені результат! 📨

Будь які питання? Напишіть! 🤔
"""

print(__doc__)
