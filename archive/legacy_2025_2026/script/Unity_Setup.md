# Unity LCARS - Інструкція встановлення

## Крок 1: Встановлення Unity

1. **Завантажте Unity Hub** з [unity.com](https://unity.com/download)
2. **Встановіть Unity Hub**
3. **Встановіть Unity Editor** (рекомендовано версія 2022.3 LTS)
4. **Встановіть модулі:**
   - ✅ Windows Build Support
   - ✅ Visual Studio Editor
   - ✅ TextMeshPro

## Крок 2: Створення проєкту

1. **Запустіть Unity Hub**
2. **Створіть новий проєкт:**
   - Назва: `LCARS Framework`
   - Template: `3D Core` або `2D Core`
   - Версія: `2022.3 LTS`

## Крок 3: Встановлення пакетів

1. **Відкрийте Package Manager** (`Window > Package Manager`)
2. **Встановіть TextMeshPro:**
   - Знайдіть `TextMeshPro`
   - Натисніть `Install`
   - Імпортуйте TMP Essentials

## Крок 4: Імпорт скриптів

1. **Створіть папку `Scripts`** в `Assets`
2. **Скопіюйте файли:**
   - `LCARS_Unity.cs`
   - `LCARS_Elbow.cs`
   - в папку `Assets/Scripts`

## Крок 5: Створення префабів

1. **Створіть папку `Prefabs`** в `Assets`
2. **Створіть префаби:**

### Elbow Prefab:
1. **Створіть пустий GameObject** (`Create Empty`)
2. **Назвіть `LCARS_Elbow`**
3. **Додайте компонент `Sprite Renderer`**
4. **Додайте скрипт `LCARSElbow`**
5. **Налаштуйте:**
   - Corner Type: `TopLeft`
   - Thickness: `1`
   - Elbow Color: `Yellow`
   - Elbow Text: `◤ LCARS`
6. **Перетягніть в папку `Prefabs`**

### Button Prefab:
1. **Створіть пустий GameObject**
2. **Назвіть `LCARS_Button`**
3. **Додайте `Sprite Renderer`**
4. **Додайте `Box Collider 2D`**
5. **Створіть матеріал:**
   - Колір: `Orange`
   - Назвіть `LCARS_Orange`
6. **Застосуйте матеріал до Sprite Renderer**
7. **Перетягніть в папку `Prefabs`**

### Scanner Prefab:
1. **Створіть пустий GameObject**
2. **Назвіть `LCARS_Scanner`**
3. **Додайте `Sprite Renderer`**
4. **Створіть матеріал:**
   - Колір: `Gray`
   - Назвіть `LCARS_Gray`
5. **Перетягніть в папку `Prefabs`**

### Display Prefab:
1. **Створіть пустий GameObject**
2. **Назвіть `LCARS_Display`**
3. **Додайте `Sprite Renderer`**
4. **Створіть матеріал:**
   - Колір: `Blue`
   - Прозорість: `80%`
   - Назвіть `LCARS_Blue`
5. **Перетягніть в папку `Prefabs`**

## Крок 6: Налаштування сцени

1. **Створіть пустий GameObject** (`Create Empty`)
2. **Назвіть `LCARS_Manager`**
3. **Додайте скрипт `LCARSManager`**
4. **Налаштуйте компонент:**
   - Перетягніть префаби в відповідні поля
   - Налаштуйте кольори палітри

## Крок 7: Налаштування камери

1. **Виберіть Main Camera**
2. **Налаштуйте:**
   - Position: `(0, 0, -10)`
   - Background: `Black`
   - Size: `10` (для 2D)

## Крок 8: Запуск

1. **Натисніть Play** ▶️
2. **Перевірте LCARS інтерфейс**
3. **Натисніть ESC** для виходу з Play Mode

## Результат

✅ **Отримаєте справжній LCARS інтерфейс:**
- Плавні дуги elbows
- Градієнтні кнопки
- Анімований сканер
- Дисплеї зі світінням
- Інтерактивні елементи
- Пульсація та анімації

## Переваги Unity

🚀 **Сучасна графіка**
🎨 **Візуальний редактор**
⚡ **Апаратне прискорення**
📱 **Кросплатформенність**
🎯 **Готові компоненти**
🔧 **Проста розробка**

Це **найкращий варіант** для створення справжнього LCARS!
