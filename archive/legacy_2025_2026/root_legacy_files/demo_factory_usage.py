#!/usr/bin/env python3
"""
Демонстрація роботи Component Factory
Показує як автоматично генерувати та використовувати QML компоненти
"""

import sys
from pathlib import Path

# Додаємо шлях до lcars модулів
sys.path.insert(0, str(Path(__file__).parent))

from lcars.generators.component_factory import LcarsComponentFactory

def show_how_it_works():
    """Показує як працює Component Factory"""
    
    print("🚀 Як працює Component Factory")
    print("=" * 50)
    
    # 1. Створення фабрики
    print("\n1️⃣ Створення фабрики:")
    factory = LcarsComponentFactory()
    print(f"   📁 Папка для компонентів: {factory.output_dir}")
    
    # 2. Генерація одного компонента
    print("\n2️⃣ Генерація клінгонської кнопки:")
    file_path = factory.generate_klingon_button(
        name="TacticalKlingon",
        color="#980000",
        text="TACTICAL",
        era="24th",
        width=120,
        height=80
    )
    print(f"   📄 Створено файл: {file_path}")
    
    # 3. Читання згенерованого файлу
    print("\n3️⃣ Згенерований QML код:")
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        print("   📝 QML код:")
        for i, line in enumerate(content.split('\n')[:20], 1):
            print(f"   {i:2d}: {line}")
        if len(content.split('\n')) > 20:
            print("   ...")
    
    # 4. Показуємо як використовувати в QML
    print("\n4️⃣ Як використовувати в QML:")
    print("   📋 Імпорт:")
    print("      import 'generated/TacticalKlingon.qml'")
    print()
    print("   🎯 Використання:")
    print("      TacticalKlingon {")
    print("          anchors.centerIn: parent")
    print("          onKlingonClicked: {")
    print("              console.log('Tactical button clicked!')")
    print("              // Ваш код тут...")
    print("          }")
    print("      }")
    
    # 5. Показуємо можливості фабрики
    print("\n5️⃣ Можливості фабрики:")
    
    print("\n   🔹 Генерація кнопок з зображень:")
    factory.generate_component(
        component_type='button',
        name="EngineButton",
        image_path="resources/engine_icon.png",
        color="#40E0D0",
        text="ENGINES"
    )
    
    print("\n   🔹 Генерація панелей:")
    factory.generate_component(
        component_type='panel',
        name="StatusPanel",
        image_path="",  # Панелі не потребують зображення
        color="#1a1a1a",
        text="SYSTEM STATUS",
        width=400,
        height=200
    )
    
    print("\n   🔹 Генерація для різних фракцій:")
    for faction in ["klingon", "romulan", "cardassian"]:
        for era in ["22nd", "23rd", "24th", "25th"]:
            try:
                files = factory.generate_from_palette(
                    faction=faction,
                    era=era,
                    component_types=['button']
                )
                print(f"      ✅ {faction} {era}: {len(files)} компонентів")
            except Exception as e:
                print(f"      ❌ {faction} {era}: {e}")
    
    # 6. Показуємо структуру файлів
    print("\n6️⃣ Структура згенерованих файлів:")
    generated_dir = factory.output_dir
    if generated_dir.exists():
        qml_files = list(generated_dir.glob("*.qml"))
        print(f"   📁 Всього QML файлів: {len(qml_files)}")
        
        # Групуємо за типами
        klingon_files = [f for f in qml_files if 'klingon' in f.name.lower()]
        romulan_files = [f for f in qml_files if 'romulan' in f.name.lower()]
        cardassian_files = [f for f in qml_files if 'cardassian' in f.name.lower()]
        panel_files = [f for f in qml_files if 'panel' in f.name.lower()]
        
        print(f"      🔺 Клінгонські: {len(klingon_files)}")
        print(f"      🔻 Ромуланські: {len(romulan_files)}")
        print(f"      🔶 Кардасіанські: {len(cardassian_files)}")
        print(f"      📋 Панелі: {len(panel_files)}")
    
    print("\n7️⃣ Переваги Component Factory:")
    print("   ✅ Автоматична генерація QML коду")
    print("   ✅ Єдиний стиль для всіх компонентів")
    print("   ✅ Динамічні кольори з палітр")
    print("   ✅ Анімації та інтерактивність")
    print("   ✅ Масштабованість та гнучкість")
    print("   ✅ Інтеграція з існуючими темами")
    
    print("\n🎉 Component Factory готовий до використання!")
    print(f"📁 Всі компоненти збережено в: {factory.output_dir}")

def show_component_example(component_name):
    """Показує приклад конкретного компонента"""
    factory = LcarsComponentFactory()
    component_path = factory.output_dir / f"{component_name}.qml"
    
    if component_path.exists():
        print(f"\n📄 Компонент: {component_name}.qml")
        print("-" * 40)
        
        with open(component_path, 'r', encoding='utf-8') as f:
            content = f.read()
            print(content)
        
        print(f"\n💡 Як використовувати {component_name}:")
        print(f"   import 'generated/{component_name}.qml'")
        print(f"   {component_name} {{")
        print(f"       anchors.centerIn: parent")
        print(f"       // Обробка кліків...")
        print(f"   }}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Показуємо конкретний компонент
        component_name = sys.argv[1]
        show_component_example(component_name)
    else:
        # Показуємо як працює фабрика
        show_how_it_works()
