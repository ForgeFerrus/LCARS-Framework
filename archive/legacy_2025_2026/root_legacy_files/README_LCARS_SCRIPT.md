# LCARS Script - Мова програмування для наукових симуляцій

## Огляд

**LCARS Script** - це спеціалізована мова програмування, розроблена для LCARS Framework, що поєднує естетику Star Trek інтерфейсів з потужністю наукових обчислень, особливо для Geant4 симуляцій та аналізу даних детекторів.

## 🚀 Швидкий старт

### 1. Запуск готового прикладу

```bash
# Запустити симуляцію частинок
python -m lcars.core.lcars_script.runtime scripts/particle_simulation.lcars

# Аналіз детектора
python -m lcars.core.lcars_script.runtime scripts/detector_analysis.lcars

# Енергетичний скан
python -m lcars.core.lcars_script.runtime scripts/energy_scan.lcars
```

### 2. Створення власного скрипту

```bash
# Створити шаблон
python -c "
from lcars.core.lcars_script.integration import get_lcars_script_manager
manager = get_lcars_script_manager()
manager.create_script_template('my_simulation', 'basic')
"

# Редагувати скрипт
nano scripts/my_simulation.lcars

# Запустити
python -m lcars.core.lcars_script.runtime scripts/my_simulation.lcars
```

## 📖 Документація

### Основні концепції

LCARS Script розроблена з урахуванням потреб наукових симуляцій:

- **Декларативний синтаксис** - фокус на що робити, а не як
- **Вбудована підтримка фізичних одиниць** - GeV, MeV, T, m, cm, мм
- **Event-driven архітектура** - інтеграція з LCARS EventBus
- **Спеціалізовані конструкції** - SIMULATION, DETECTOR, ANALYZER

### Синтаксис

#### Змінні та фізичні одиниці

```lcars
// Фізичні величини з одиницями виміру
beam_energy: 1.5 GeV
particle_count: 10000
magnetic_field: 3.8 T
detector_length: 2.5 m

// Стандартні змінні
simulation_name: "main_beam_test"
output_directory: "/data/simulations/"
```

#### Функції

```lcars
FUNCTION calculate_efficiency(detected, total) -> float {
    if total == 0 return 0.0
    return detected / total * 100
}

FUNCTION generate_momentum(energy) -> float {
    mass = 0.938  // GeV/c^2
    return sqrt(energy * energy - mass * mass)
}
```

#### Симуляції

```lcars
SIMULATION particle_collision {
    ENERGY beam_energy
    PARTICLES particle_count
    GEOMETRY cms_detector
    
    ON START {
        log("Starting simulation...")
        emit("simulation:started", {energy: beam_energy})
    }
    
    ON COMPLETE {
        efficiency = calculate_efficiency(detected, total)
        export("results.json", {efficiency: efficiency})
    }
}
```

#### Детектори

```lcars
DETECTOR cms_detector {
    LAYERS [
        {type: "pixel_silicon", thickness: 300 μm, position: [0, 0, 0]},
        {type: "ecal", thickness: 20 cm, position: [0, 0, 1.5m]}
    ]
    
    MAGNETIC_FIELD 3.8 T
    MATERIAL "silicon"
    
    ON HIT(particle) {
        record_hit(particle.position, particle.energy)
        emit("detector:hit", particle)
    }
}
```

#### Аналіз даних

```lcars
ANALYZER energy_spectrum {
    INPUT "simulation_output.root"
    
    PROCESS {
        data = load_data("simulation_output.root")
        histogram = create_histogram("energy_spectrum", 100, 0, 5 GeV)
        
        FOREACH event IN data {
            histogram.fill(event.particle.energy)
        }
        
        fit_result = fit_gaussian(histogram)
        export_plot(histogram, "energy_spectrum.png")
    }
}
```

### Вбудовані функції

#### Математичні функції

```lcars
sqrt(x)      // Квадратний корінь
sin(x)       // Синус
cos(x)       // Косинус
tan(x)       // Тангенс
abs(x)       // Модуль
min(a, b)    // Мінімум
max(a, b)    // Максимум
sum(array)   // Сума елементів
```

#### Фізичні константи

```lcars
c           // Швидкість світла, м/с
e           // Елементарний заряд, Кл
m_e         // Маса електрона, кг
m_p         // Маса протона, кг
h           // Постійна Планка, Дж·с
k_B         // Постійна Больцмана, Дж/К
```

#### Системні функції

```lcars
log(message)                    // Логування повідомлення
emit(event_name, data)          // Генерувати подію
export(filename, data)          // Експортувати дані
len(array)                      // Довжина масиву
range(start, end)               // Діапазон чисел
```

### Фізичні одиниці

Підтримуються наступні одиниці виміру:

- **Енергія:** eV, keV, MeV, GeV, TeV
- **Довжина:** mm, cm, m, km, μm, nm
- **Час:** ns, μs, ms, s, min, h
- **Маса:** eV/c², MeV/c², GeV/c², kg, g
- **Заряд:** e, C
- **Магнітне поле:** T, G
- **Температура:** K, °C

## 🏗️ Архітектура

### Компоненти

1. **Lexer** (`lexer.py`) - лексичний аналізатор
2. **Parser** (`parser.py`) - синтаксичний аналізатор, будує AST
3. **Interpreter** (`interpreter.py`) - інтерпретатор AST
4. **Compiler** (`compiler.py`) - компілятор в Python
5. **Runtime** (`runtime.py`) - середовище виконання
6. **Integration** (`integration.py`) - інтеграція з LCARS Framework

### Процес виконання

```
LCARS Script (.lcars)
        ↓
        Lexer (токени)
        ↓
        Parser (AST)
        ↓
    ┌─────────────┐
    │ Interpreter │  →  Пряме виконання
    └─────────────┘
        ↓
    ┌─────────────┐
    │  Compiler   │  →  Python код
    └─────────────┘
        ↓
    ┌─────────────┐
    │   Runtime   │  →  Виконання з інтеграцією
    └─────────────┘
```

## 🔧 Інтеграція з LCARS Framework

### EventBus інтеграція

```lcars
// Генерація подій
emit("simulation:started", {
    energy: beam_energy,
    particles: particle_count
})

// Підписка на події (в Python коді)
event_bus.subscribe(EventType.SIMULATION_STARTED, handler)
```

### Плагін система

LCARS Script інтегрується як плагін:

```python
from lcars.core.lcars_script.integration import initialize_lcars_script_integration

# Ініціалізація під час запуску LCARS
initialize_lcars_script_integration(plugin_manager)
```

## 📝 Приклади використання

### 1. Проста симуляція

```lcars
// Простий тест детектора
energy: 1 GeV
particles: 1000

SIMULATION simple_test {
    ENERGY energy
    PARTICLES particles
    
    ON COMPLETE {
        efficiency = calculate_efficiency(detected, particles)
        log("Detection efficiency: " + efficiency + "%")
    }
}
```

### 2. Аналіз енергетичного спектру

```lcars
ANALYZER spectrum_analysis {
    INPUT "data.root"
    
    PROCESS {
        data = load_data("data.root")
        spectrum = create_histogram("energy", 100, 0, 5 GeV)
        
        FOREACH event IN data {
            spectrum.fill(event.energy)
        }
        
        peak = find_peak(spectrum)
        log("Peak energy: " + peak.position + " GeV")
    }
}
```

### 3. Візуалізація

```lcars
VISUALIZE detector_3d {
    TYPE "3d_model"
    SOURCE cms_detector
    STYLE "lcars_tng"
    
    EXPORT "detector.glb"
    
    ON READY {
        show_in_ui("3d_viewer")
    }
}
```

## 🛠️ Розробка

### Компіляція скрипта

```python
from lcars.core.lcars_script import Lexer, Parser, PythonCompiler

# Читання скрипта
with open("script.lcars", "r") as f:
    source = f.read()

# Компіляція
lexer = Lexer(source)
tokens = lexer.tokenize()

parser = Parser(tokens)
ast = parser.parse()

compiler = PythonCompiler()
python_code = compiler.compile(ast)

# Збереження результату
with open("script_compiled.py", "w") as f:
    f.write(python_code)
```

### Інтерпретація скрипта

```python
from lcars.core.lcars_script import Lexer, Parser, Interpreter

# Інтерпретація
lexer = Lexer(source)
tokens = lexer.tokenize()

parser = Parser(tokens)
ast = parser.parse()

interpreter = Interpreter()
result = interpreter.interpret(ast)
```

### Валідація скрипта

```python
from lcars.core.lcars_script.integration import get_lcars_script_manager

manager = get_lcars_script_manager()
validation = manager.validate_script("script.lcars")

if validation['valid']:
    print("Script is valid!")
else:
    print("Errors:", validation['errors'])
```

## 📊 Статистика та моніторинг

### Отримання статистики виконання

```python
from lcars.core.lcars_script.runtime import runtime

# Статистика виконання
stats = runtime.get_execution_stats()
print(f"Total simulations: {stats.total_simulations}")
print(f"Completed: {stats.completed_simulations}")
print(f"Failed: {stats.failed_simulations}")

# Результати симуляцій
results = runtime.get_simulation_results()
for result in results:
    print(f"{result.name}: {result.status}")
```

### Моніторинг в реальному часі

```python
# Показати статус runtime
runtime.print_status()
```

## 🔌 Розширення

### Додавання вбудованих функцій

```python
def custom_function(args):
    # Ваша логіка
    return result

# Реєстрація в runtime
runtime.register_function("my_function", custom_function)
```

### Створення нових типів даних

```python
class CustomDataType:
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return f"Custom({self.value})"

# Інтеграція в інтерпретатор
```

## 🐛 Відладка

### Логування

```lcars
// Включити детальне логування
log("Debug: variable value = " + variable)
log("Debug: entering function")
log("Debug: simulation progress = " + progress + "%")
```

### Перевірка синтаксису

```bash
# Валідація скрипта
python -c "
from lcars.core.lcars_script.integration import get_lcars_script_manager
manager = get_lcars_script_manager()
validation = manager.validate_script('script.lcars')
print(validation)
"
```

### AST візуалізація

```python
from lcars.core.lcars_script import Lexer, Parser

lexer = Lexer(source)
tokens = lexer.tokenize()

parser = Parser(tokens)
ast = parser.parse()

# Друк AST для відладки
parser.print_ast(ast)
```

## 📚 Додаткові ресурси

- [Повна документація](docs/LCARS_SCRIPT_DESIGN.md)
- [API Reference](docs/API_REFERENCE.md)
- [Приклади скриптів](scripts/)
- [Тестові приклади](tests/lcars_script/)

## 🤝 Співпраця

### Внесок у проєкт

1. Форк репозиторію
2. Створити feature branch
3. Внести зміни
4. Додати тести
5. Створити Pull Request

### Тестування

```bash
# Запустити тести
python -m pytest tests/lcars_script/

# Тестування лексера
python -m lcars.core.lcars_script.lexer

# Тестування парсера
python -m lcars.core.lcars_script.parser

# Тестування інтерпретатора
python -m lcars.core.lcars_script.interpreter
```

## 📄 Ліцензія

LCARS Script є частиною LCARS Framework і розповсюджується під тією ж ліцензією.

## 🙏 Подяки

- Star Trek fandom за натхнення
- Розробникам Geant4 за фізичні моделі
- Спільноті Python за інструменти

---

**LCARS Script v1.0 - Enterprise Edition**  
*Where science meets Star Trek aesthetics*
