# ◤ LCARS BASE LAYER ARCHITECTURE // TITANIUM MASTER SPECIFICATION 🖖
# =============================================================================
# ОПИС: Базовий шар LCARS Framework (Фундамент системи).
#       Визначає векторну геометрію Окуди, палітри кольорів, сигнальні анімації,
#       контейнери інтерфейсу, центральний реєстр та систему типів DNA.
# СТАНДАРТ: Titanium (Zero-Except, Zero-Underscores, Strict PascalCase, Pure LCARS Classes).
# =============================================================================

## 🏛 1. АРХІТЕКТУРНИЙ ПРИНЦИП
`lcars/base/` є абсолютно незалежним фундаментом:
1. **Ізоляція**: Базовий шар не залежить від вищих шарів (`core`, `modules`, `ui`, `service`, `programs`).
2. **Єдиний простір імен `LCARS`** (`type.py`): Усі графічні типи, системні адаптери та протоколи доступні через клас `LCARS`.
3. **Реєстр платформи** (`register.py`): Центральна точка зв'язування всіх системних вузлів та мостів `Bridge.*`.

---

## 📁 2. СТРУКТУРА ФАЙЛІВ БАЗОВОГО ШАРУ

| Файл | Розмір | Призначення |
| :--- | :--- | :--- |
| **`animation.py`** | ~35 KB | Сигнальні драйвери (`Driver`) та алгоритмічні наукові дисплеї (`Warp`, `Starfield`, `WaveStream`, `ShieldHarmonics`, `Pulse`, `ScanningBar`) |
| **`catalog.py`** | ~5.5 KB | Паспорт підтримуваних технологічних стеків (`LCARSCatalog`: Core, Web, Science, Simulation, Quantum, AI) |
| **`component.py`** | ~37 KB | Векторне креслення канонічної геометрії Окуди (`Component`, `LCARSButton`, `LCARSElbow`, `LCARSBar`, `LCARSIndicator`, `LCARSLabel`) |
| **`default.py`** | ~11 KB | Канонічні колірні палітри LCARS, системні теми (`SystemTheme`) та конфігурація шрифтів |
| **`graphic.py`** | ~33 KB | Геометричні пропорції Окуди (`THICK`, `THIN`, `GAP`, `RADIUS`), примітиви `Primitive` та апаратний `Renderer` |
| **`info.py`** | ~3 KB | Єдиний системний паспорт, глобальна версія (`Version.Release`), метадані та живий розрахунок Зоряної Дати (`GetStardate()`) |
| **`interface.py`** | ~64 KB | Головні оболонки та контейнери інтерфейсу (`Panel`, `PADD`, `Element`, `Screen`, `Segment`, `.Vertical()`, `.Horizontal()`, `.Add()`) |
| **`register.py`** | ~148 KB | Центральний Реєстр усіх зв'язків платформи, системних сутностей та зовнішніх мостів `Bridge.*` |
| **`type.py`** | ~25 KB | Головний простір імен `LCARS`, базові DNA-типи, динамічні метакласи `Namespace` та `Directive` |

---

## 💎 3. ВЗАЄМОДІЯ ЧЕРЕЗ `LCARS`

Усі прикладні модулі та інтерфейси звертаються до бази через простір імен `LCARS`:
```python
from lcars.base.type import LCARS
from lcars.base.interface import Panel, LCARSLabel, LCARSButton, LCARSElbow, LCARSBar

# Створення панелі
MyPanel = Panel()
MyPanel.Vertical(15, 15, 15, 15, 10)

# Додавання елементів
Btn = LCARSButton("EXECUTE DIRECTIVE", Parent=MyPanel.widget)
MyPanel.Add(MyPanel.Layout, Btn)
```

---

## 🧪 4. ВАЛІДАЦІЯ БАЗОВОГО ШАРУ
Перевірка цілісності всіх модулів:
```powershell
& .\.venv\Scripts\python.exe -c "import lcars.base.animation, lcars.base.catalog, lcars.base.component, lcars.base.default, lcars.base.graphic, lcars.base.info, lcars.base.interface, lcars.base.register, lcars.base.type; print('ALL BASE MODULES OPERATIONAL!')"
```
