# 🚀 LCARS IDE - Швидкий Старт

## Ваша IDE це **VS Code** на вашому Desktop'у!

### ⚡ Що встановлено:
- ✅ Python debugger (F5)
- ✅ Run/Test commands (Ctrl+Shift+D)
- ✅ Code formatting (black)
- ✅ Linting (pylint)
- ✅ Integration з Registry & Kernel

---

## 📋 Основні команди (Ctrl+Shift+P)

### Запуск & Дебаг
- `Tasks: Run Task` → **Test: Current File**
- `Tasks: Run Task` → **Run: Current File**
- `Debug: Start Debugging` (F5)

### Дослідження
- `Tasks: Run Task` → **Check: Registry** (див всі компоненти)
- `Tasks: Run Task` → **Test: Kernel** (перевірити ядро)

### Розробка
- `Tasks: Run Task` → **Format: Current File** (чистить код)
- `Tasks: Run Task` → **Lint: Current File** (перевіри помилки)

---

## 📁 Структура проекту

```
LCARS-Framework/
├── lcars/
│   ├── base/           # ⚙️ Kernel, Registry, Types
│   ├── core/           # 🎯 Архітектура системи
│   ├── ui/             # 🖼️ UI компоненти
│   ├── modules/        # 🔧 Системні модулі
│   └── service/        # 🌐 Сервіси
├── .vscode/            # 🎨 Налаштування IDE
├── tests/              # 🧪 Тести
└── requirements.txt    # 📦 Залежності
```

---

## 🔍 Як писати код (Pure No-Q)

### ❌ ЗАБУТИ:
```python
from PyQt6.QtWidgets import QMainWindow  # БЕЗ прямих імпортів!
```

### ✅ ПРАВИЛЬНО:
```python
from lcars.base.register import registry

# Отримати компонент через Реєстр
MainWindow = registry.Get("Interface.Viewport")
Window = MainWindow()
```

---

## 📚 Документація

- **Kernel**: `lcars.core.kernel.py`
- **Registry**: `lcars.base.register.py`
- **Components**: `lcars.base.component.py`
- **Types**: `lcars.base.type.py`

---

## 🎯 Наступні кроки

1. **Explore**: `Tasks: Run Task` → **Check: Registry**
2. **Learn**: Прочитайте `lcars/core/kernel.py`
3. **Create**: Напишіть свій перший модуль в `lcars/modules/`
4. **Test**: Запустіть його через VS Code terminal

---

## ⚙️ Налаштування

- **Python interpreter**: автоматично (`.venv`)
- **Debugging**: встроєний debugpy
- **Auto format**: Ctrl+S (black)
- **Type checking**: Pylance (встроєний)

**Все готово! Приступайте до розробки! 🚀**
