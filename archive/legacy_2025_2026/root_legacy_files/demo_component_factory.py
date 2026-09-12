#!/usr/bin/env python3
"""
Демонстрація LCARS Component Factory
Автоматична генерація QML компонентів для LCARS інтерфейсів
"""

import sys
import os
from pathlib import Path

# Додаємо шлях до lcars модулів
sys.path.insert(0, str(Path(__file__).parent))

from lcars.generators.component_factory import LcarsComponentFactory

def main():
    print("🚀 LCARS Component Factory - Демонстрація")
    print("=" * 50)
    
    # Створюємо фабрику
    factory = LcarsComponentFactory()
    
    print("\n1. 📋 Генерація клінгонських кнопок...")
    
    # Клінгонські кнопки з різними ерами
    klingon_eras = [
        ("Klingon22nd", "#400000", "22ND"),
        ("Klingon23rd", "#CC0000", "23RD"), 
        ("Klingon24th", "#660000", "24TH"),
        ("Klingon25th", "#A61A35", "25TH")
    ]
    
    for name, color, era in klingon_eras:
        factory.generate_klingon_button(
            name=name,
            color=color,
            text=era,
            era=era.lower(),
            width=120,
            height=80
        )
    
    print("\n2. 🔻 Генерація ромуланських кнопок...")
    romulan_colors = ["#006666", "#00FF99", "#1C7736", "#99CC99"]
    
    for i, color in enumerate(romulan_colors):
        factory.generate_component(
            component_type='romulan_button',
            name=f"RomulanButton{i+1}",
            image_path="",  # ShapePath не потребує зображення
            color=color,
            text=f"ROM{i+1}",
            width=120,
            height=60
        )
    
    print("\n3. 🔶 Генерація кардасіанських кнопок...")
    cardassian_colors = ["#CC3300", "#FF4400", "#FF6600", "#FF9900"]
    
    for i, color in enumerate(cardassian_colors):
        factory.generate_component(
            component_type='cardassian_button',
            name=f"CardassianButton{i+1}",
            image_path="",  # ShapePath не потребує зображення
            color=color,
            text=f"CAR{i+1}",
            width=100,
            height=60
        )
    
    print("\n4. 📁 Генерація кнопок на основі зображень...")
    
    # Припустимо що у вас є такі зображення
    sample_images = [
        ("TacticalChevron", "resources/tactical.png", "#CC0000", "TACTICAL"),
        ("EnginePanel", "resources/engines.png", "#40E0D0", "ENGINES"),
        ("ShieldPanel", "resources/shields.png", "#0099CC", "SHIELDS"),
        ("WeaponsPanel", "resources/weapons.png", "#FF6600", "WEAPONS")
    ]
    
    for name, img_path, color, text in sample_images:
        # Перевіряємо чи існує файл
        if os.path.exists(img_path):
            factory.generate_component(
                component_type='button',
                name=name,
                image_path=img_path,
                color=color,
                text=text,
                width=200,
                height=80
            )
        else:
            print(f"⚠️  Зображення не знайдено: {img_path}")
            # Створюємо компонент без зображення
            factory.generate_component(
                component_type='button',
                name=name,
                image_path="",
                color=color,
                text=text,
                width=200,
                height=80
            )
    
    print("\n5. 📋 Генерація панелей...")
    panels = [
        ("MainPanel", "#1a1a1a", "MAIN SYSTEMS", 400, 200),
        ("TacticalPanel", "#2d1b1b", "TACTICAL", 300, 150),
        ("EngineeringPanel", "#1b2d1b", "ENGINEERING", 300, 150)
    ]
    
    for name, color, text, width, height in panels:
        factory.generate_component(
            component_type='panel',
            name=name,
            image_path="",
            color=color,
            text=text,
            width=width,
            height=height,
            border_radius=5
        )
    
    print("\n6. 🎨 Генерація набору для фракцій...")
    
    # Генерація наборів для кожної фракції
    factions = ["klingon", "romulan", "cardassian"]
    eras = ["22nd", "23rd", "24th", "25th"]
    
    for faction in factions:
        for era in eras:
            try:
                files = factory.generate_from_palette(
                    faction=faction,
                    era=era,
                    component_types=['klingon_button' if faction == 'klingon' else 'button', 'panel']
                )
                print(f"✅ {faction} {era}: {len(files)} компонентів")
            except Exception as e:
                print(f"❌ Помилка {faction} {era}: {e}")
    
    print(f"\n🎉 Готово! Всі компоненти збережено в: {factory.output_dir}")
    print("\n💡 Використання в QML:")
    print("   import 'generated/Klingon24th.qml'")
    print("   Klingon24th {")
    print("       anchors.centerIn: parent")
    print("       onKlingonClicked: console.log('Klingon button clicked!')")
    print("   }")

if __name__ == "__main__":
    main()
