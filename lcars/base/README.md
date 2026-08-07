# LCARS Base — Завершений базовий шар (Titanium Standard)

`lcars/base/` — фундаментальне стабільне ядро фреймворку. Визначає базові типи, реєстр, канонічну палітру, графічні примітиви та підсистему візуальних компонентів.

> ⚠️ **СТАТУС:** Базовий шар повністю завершений, зафіксований і **не підлягає змінам**. Всі додавання та прикладні розширення будуються виключно поверх цього фундаментального шару.

---

## Архітектурний стандарт

1. **Іммутабельність**: Вищі шари (`service`, `ui`, `engineering`, `plugins`) будуються від `base`, але `base` є повністю незалежним.
2. **Titanium CamelCase**: Всі класи, методи та властивості дотримуються єдиного стандарту найменування Titanium.
3. **Zero-Except**: Жодного маскування помилок чи прихованих `except Exception` у базі.
4. **Єдиний метаклас резолвінгу (`Namespace`)**:
   - `LCARS.Core` — сигнали, слоти, потоки, таймери;
   - `LCARS.Geometry` — розміри, точки, геометрія;
   - `LCARS.Interface` — контейнери, вікна, віджети, PADD;
   - `LCARS.Visual` — стилі, палітри, кольори, шрифти;
   - `LCARS.Protocol` — протоколи вирівнювання, відображення, введення;
   - `LCARS.System` — стандартні системні простори імен Python.

---

## Структура файлів бази

| Файл | Призначення |
|---|---|
| `register.py` | Центральний реєстр `LCARSRegister` (`registry`). Єдина точка мапінгу системних і базових модулів. |
| `type.py` | Кореневі класи `LCARS`, `Namespace`, `SystemComponent` та експорт ключових типів. |
| `default.py` | Канонічна палітра LCARS (`Palette`), шрифти (`FontStyle`), глобальні налаштування та стилі. |
| `component.py` | Базові елементи LCARS: кнопки (`LCARSButton`), мітки (`LCARSLabel`), індикатори (`LCARSIndicator`), бари (`LCARSBar`). |
| `interface.py` | Структурні оболонки UI: `PADD`, `Segment`, `DataBlock`, `Element`, `Screen`. |
| `graphic.py` | Носії графічного рендерингу та команди малювання. |
| `animation.py` | Стандартні анімації LCARS (`Warp`, `DataStream`, `Scanner`). |
| `catalog.py` | `LCARSCatalog` — каталог підтримуваних категорій систем. |
| `version.py` | Версіонування ядра Titanium Master. |

---

## Взаємодія з вищими шарами

- **Синхронізація сигналів**: Оптична мережа `ODN` (`lcars.core.signal`) та сервіс `SubspaceBridge` (`lcars.service.bridge`) взаємодіють з базовим реєстром для динамічного виклику директив (`Directive`) та модулів (`Link`).
- **Бортовий комп'ютер**: `BoardComputer` (`lcars.service.onboard`) використовує `Matrix` та `interface.py` для побудови інтерфейсу PADD.

---

## Перевірка цілісності

```powershell
python -m compileall -q lcars/base
```

Приклад використання типів:

```python
from lcars.base.type import LCARS

alignment = LCARS.Protocol.AlignmentFlag.AlignCenter
orientation = LCARS.Protocol.Orientation.Horizontal

Зовнішні бібліотеки не є базовими типами й не додаються до списку `LCARS`. Єдина базова операція мосту — підключення зареєстрованої бібліотеки:

```python
from lcars.base.register import Bridge

OpenAI = Bridge.Connect("OpenAI")
```

Міст використовується тільки для зовнішніх залежностей. Базові та системні типи беруться з відповідних записів `Base.*` і `System.*`.

## Приклади

```python
from lcars.base.type import LCARS

Application = LCARS.Application
Button = LCARS.Button
Line = LCARS.Line
Process = LCARS.Process
Path = LCARS.SystemPath
```

Для старих рядкових шляхів протоколів збережена сумісність:

```python
Center = LCARS.Load("Protocol.Align.Center")
```

## Перевірка базового шару

Синтаксис:

```powershell
python -m compileall -q lcars tests test
```

Цільові тести реєстру та базової консолі:

```powershell
python -m pytest -q tests/test_register.py tests/test_console.py
```

Поточний результат цільової перевірки: `3 passed`.

Повна система ще розвивається; помилки у вищих шарах, зокрема в `AlertSystem`, не є частиною базового списку типів.
