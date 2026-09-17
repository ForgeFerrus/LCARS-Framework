# ◤ LCARS BASE LAYER ARCHITECTURE // TITANIUM MASTER SPECIFICATION 🖖
# =============================================================================
# ОПИС: Базовий шар LCARS Framework (Фундамент системи).
#       Визначає векторну геометрію Окуди, канонічні палітри кольорів, 
#       сигнально-часові анімаційні приводи, наукові та навігаційні дисплеї,
#       контейнери інтерфейсу, центральний реєстр та систему типів DNA.
# СТАНДАРТ: Titanium (Zero-Except, Zero-Underscores, Strict PascalCase, Pure LCARS Classes).
# =============================================================================

## 🏛 1. АРХІТЕКТУРНІ ПРИНЦИПИ
`lcars/base/` є абсолютно незалежним фундаментом системи:
1. **Ізоляція та чистота**: Базовий шар не має зворотних залежностей від вищих шарів (`core`, `modules`, `programs`).
2. **Єдиний простір імен `LCARS`** (`type.py`): Всі системні адаптери, графічні типи та протоколи доступні централізовано через клас `LCARS`.
3. **Реєстр платформи** (`register.py`): Центральна диспетчеризація зв'язків компонентів та системних мостів.
4. **Чистий вектор замість віджетів** (`component.py`, `graphic.py`): Компоненти є логічними вузлами на шині ODN із чистим математичним рендерингом `Draw(Context, Device)` через `QPainterPath`, без зайвих важких віджетів операційної системи.

---

## 📁 2. СТРУКТУРА ФАЙЛІВ БАЗОВОГО ШАРУ

| Файл | Розмір | Призначення та ключові сутності |
| :--- | :--- | :--- |
| **`animation.py`** | ~56 KB | **Часовий привід та алгоритмічні дисплеї:**<br>• *Приводи*: `Driver`, `Animation`<br>• *Збірки*: `Sequencer`, `Parallel`, `Stagger`<br>• *Переходи*: `Reveal`, `Conceal`, `Transition`, `Blink`<br>• *Текст*: `Typewriter` (`Write`), `TextDecode` (`Decode`)<br>• *Дисплеї*: `WaveStream` (7 режимів), `Scanning`, `Pulse`, `DiagnosticGrid`, `DataStream`, `Starfield` (Impulse + Warp) |
| **`catalog.py`** | ~5.5 KB | Паспорт підтримуваних технологічних стеків (`LCARSCatalog`: Core, Web, Science, Simulation, Quantum, AI) |
| **`component.py`** | ~28 KB | **Базовий сенсорний вузол інтерфейсу (ODN Node):**<br>• `Component` (наслідує `Visual`)<br>• `LCARSButton` (6 типів геометрії: Rect, Pill, PillHalf, Soft, SoftHalf, Elbow)<br>• `LCARSBar` (канонічні балки та рейки каркасу)<br>• `LCARSIndicator` (світлові маркери: Rect, Soft, PillHalf)<br>• `LCARSElbow` (несучі кутові вигини каркасу Окуди)<br>• `LCARSLabel` (типографіка Swiss 911 Ultra Compressed) |
| **`default.py`** | ~12 KB | **Палітра кольорів та теми:**<br>• `Palette` (канонічні кольори TNG/DS9/Voyager: Tango, Federation Blue, Red Alert)<br>• `SystemTheme` (керування динамічними станами та яскравістю)<br>• `FontStyle` (типографічний хелпер для стилів шрифту) |
| **`desktop.py`** | ~32 KB | Системні віконні адаптери та десктопне середовище терміналу LCARS |
| **`graphic.py`** | ~40 KB | **Низькорівневе векторне математичне ядро:**<br>• Топологічні трейсери: `TraceCap`, `TraceElbow`, `TraceRounded`, `TraceRect`<br>• Класи оптики: `Visual`, `Topology`, `Graphic`<br>• Апаратний випромінювач світла: `Emitter` (`Renderer`) із прямим викликом `Draw(Context, Device)` |
| **`info.py`** | ~3 KB | Системний паспорт, глобальна версія (`Version.Release`) та розрахунок Зоряної Дати (`GetStardate()`) |
| **`interface.py`** | ~43 KB | **Оптичні поверхні та готові канонічні композиції (без префіксу LCARS):**<br>• Поверхня полотна: `Surface(Display)`<br>• Контейнер: `Element` (`SetVertical`, `SetHorizontal`, `Add`, `AddStretch`)<br>• Композиції: `Header`, `Footer`, `Sidebar`, `Bracket`, `DataBlock`, `Toolbar`, `StatBar`, `ScanningBar`, `Panel`, `AccessPanel`, `Screen`, `PADD` |
| **`register.py`** | ~161 KB | Центральний Реєстр усіх підсистем, вузлів інтерфейсу та зовнішніх мостів `Bridge.*` |
| **`type.py`** | ~29 KB | Головний фасад `LCARS`, базові DNA-типи, протоколи вирівнювання та клавіш |

---

## 💎 3. ВЗАЄМОДІЯ ТА СТАНДАРТИ ВИКОРИСТАННЯ

### 3.1. Складання канонічного екрана (Interface Compositions)
```python
from lcars.base.default import Palette
from lcars.base.interface import Screen, Header, Footer, Sidebar, Bracket, Panel
from lcars.base.component import LCARSButton, LCARSLabel

# Створення екрана
Root = Screen(Title="TACTICAL DEFENSE CONSOLE", Width=1280, Height=800)

# Додавання канонічних блоків без префіксів
Root.Add(Header(Title="PRIMARY SENSOR GRID // USS ENTERPRISE", Spectrum=Palette.Buttons[2]))

MainPanel = Panel(Spectrum=Palette.Background)
MainPanel.SetHorizontal()

# Додавання лівого сайдбару та робочої області
MainPanel.Add(Sidebar(Width=220))
MainPanel.Add(Bracket(Width=600, Height=400))

Root.Add(MainPanel)
Root.Add(Footer(Title="SYSTEMS NOMINAL // LEVEL 1 DIAGNOSTIC CLEAR", Spectrum=Palette.Buttons[0]))
```

### 3.2. Використання анімаційного рушія (Animation Suite)
```python
from lcars.base.animation import WaveStream, Starfield, Sequencer, Parallel, Stagger, Reveal, Typewriter

# 1. Підпросторовий спектрограф (7 режимів)
Waves = WaveStream(Mode="Harmonic", Frequency=3.0, Speed=0.04)
Waves.Start()

# 2. 3D навігаційне зоряне поле (Impulse / Warp)
Viewscreen = Starfield(Mode="Warp", StarCount=200)
Viewscreen.Start()

# 3. Композиція запуску терміналу (Паралельно + Каскадно)
FrameAnim = Parallel().Add(Reveal().Start(Target=TopBar), Reveal().Start(Target=BottomBar))
ButtonsAnim = Stagger().Add(*[Reveal().Start(Target=btn) for btn in ButtonList])

BootSequence = Sequencer().Add(FrameAnim).Add(ButtonsAnim).Play()
```

---

## 🧪 4. ВАЛІДАЦІЯ БАЗОВОГО ШАРУ
Перевірка цілісності всіх 10 модулів базового шару:
```powershell
py -c "import lcars.base.animation, lcars.base.catalog, lcars.base.component, lcars.base.default, lcars.base.desktop, lcars.base.graphic, lcars.base.info, lcars.base.interface, lcars.base.register, lcars.base.type; print('ALL BASE MODULES OPERATIONAL [EXIT 0]')"
```
