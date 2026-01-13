#!/usr/bin/env python3
"""
LCARS Component Factory - автоматичний генератор QML компонентів
Створює QML файли на основі SVG/PNG зображень з динамічними кольорами та анімацією
"""

import os
import json
from typing import Optional, Dict, Any
from pathlib import Path

class LcarsComponentFactory:
    """Фабрика для створення LCARS QML компонентів"""
    
    def __init__(self, output_dir: str = "lcars/qml/generated"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Шаблони для різних типів компонентів
        self.templates = {
            'button': self._get_button_template(),
            'panel': self._get_panel_template(),
            'klingon_button': self._get_klingon_button_template(),
            'romulan_button': self._get_romulan_button_template(),
            'cardassian_button': self._get_cardassian_button_template()
        }
    
    def generate_component(self, 
                        component_type: str,
                        name: str, 
                        image_path: str,
                        color: str = "#40E0D0",
                        text: str = "SYSTEM",
                        **kwargs) -> str:
        """
        Генерує QML компонент
        
        Args:
            component_type: тип компонента (button, panel, klingon_button, etc.)
            name: назва компонента
            image_path: шлях до зображення (SVG/PNG)
            color: основний колір
            text: текст на компоненті
            **kwargs: додаткові параметри
            
        Returns:
            str: шлях до створеного QML файлу
        """
        if component_type not in self.templates:
            raise ValueError(f"Невідомий тип компонента: {component_type}")
        
        template = self.templates[component_type]
        
        # Підготовка параметрів
        params = {
            'name': name,
            'image_path': image_path,
            'color': color,
            'text': text,
            'width': kwargs.get('width', 250),
            'height': kwargs.get('height', 80),
            'font_size': kwargs.get('font_size', 14),
            'animation_duration': kwargs.get('animation_duration', 150),
            'border_radius': kwargs.get('border_radius', 0),
            'width_minus_10': kwargs.get('width', 250) - 10,
            'width_minus_15': kwargs.get('width', 250) - 15,
            'width_minus_20': kwargs.get('width', 250) - 20,
            'height_minus_5': kwargs.get('height', 80) - 5,
            'height_minus_20': kwargs.get('height', 80) - 20,
            'height_minus_15': kwargs.get('height', 80) - 15,
            'width_div_2': kwargs.get('width', 250) // 2,
            'width_div_2_plus_10': kwargs.get('width', 250) // 2 + 10,
            'width_div_2_minus_10': kwargs.get('width', 250) // 2 - 10,
            **kwargs
        }
        
        # Генерація QML контенту
        qml_content = template.format(**params)
        
        # Збереження файлу
        file_path = self.output_dir / f"{name}.qml"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(qml_content)
        
        print(f"✅ Компонент {name}.qml успішно згенеровано!")
        print(f"   Тип: {component_type}")
        print(f"   Зображення: {image_path}")
        print(f"   Колір: {color}")
        print(f"   Шлях: {file_path}")
        
        return str(file_path)
    
    def generate_klingon_button(self, 
                              name: str,
                              color: str = "#660000",
                              text: str = "",
                              era: str = "24th",
                              **kwargs) -> str:
        """Генерує клінгонську кнопку з ShapePath"""
        return self.generate_component(
            component_type='klingon_button',
            name=name,
            image_path="",  # Не використовується для ShapePath
            color=color,
            text=text,
            era=era,
            **kwargs
        )
    
    def generate_from_palette(self, 
                          faction: str,
                          era: str,
                          component_types: list = None) -> list:
        """
        Генерує набір компонентів для фракції/ери на основі палітри
        
        Args:
            faction: назва фракції (klingon, romulan, cardassian)
            era: ера (22nd, 23rd, 24th, 25th)
            component_types: список типів компонентів для генерації
            
        Returns:
            list: шляхи до створених файлів
        """
        from lcars.themes.theme import get_faction_colors
        
        if component_types is None:
            component_types = ['button', 'panel']
        
        palette = get_faction_colors(faction, era)
        generated_files = []
        
        for i, comp_type in enumerate(component_types):
            name = f"{faction}_{era}_{comp_type}_{i}"
            color = palette['button_colors'][i % len(palette['button_colors'])]
            
            file_path = self.generate_component(
                component_type=comp_type,
                name=name,
                image_path=f"resources/{faction}_{era}_{comp_type}.png",
                color=color,
                text=f"{faction.upper()} {comp_type.upper()}",
                width=200,
                height=80
            )
            generated_files.append(file_path)
        
        return generated_files
    
    def _get_button_template(self) -> str:
        """Шаблон для базової кнопки"""
        return '''import QtQuick
import Qt5Compat.GraphicalEffects

Item {{
    id: root_{name}
    width: {width}; height: {height}
    property bool active: false
    property color buttonColor: "{color}"
    property string buttonText: "{text}"

    // Основне зображення з вашим дизайном
    Image {{
        id: img
        source: "{image_path}"
        anchors.fill: parent
        visible: false // Ховаємо для накладання кольору
        fillMode: Image.PreserveAspectFit
    }}

    // Шейдер для динамічної зміни кольору
    ColorOverlay {{
        id: overlay
        anchors.fill: img
        source: img
        color: root_{name}.active ? "white" : root_{name}.buttonColor
        Behavior on color {{ ColorAnimation {{ duration: {animation_duration} }} }}
    }}

    // Текст на кнопці
    Text {{
        text: root_{name}.buttonText
        anchors.centerIn: parent
        color: root_{name}.active ? "black" : "white"
        font.bold: true
        font.pixelSize: {font_size}
        Behavior on color {{ ColorAnimation {{ duration: {animation_duration} }} }}
    }}

    // Інтерактивність
    MouseArea {{
        anchors.fill: parent
        hoverEnabled: true
        
        onPressed: root_{name}.active = true
        onReleased: root_{name}.active = false
        onExited: root_{name}.active = false
        
        onClicked: {{
            console.log("{name} activated")
            root_{name}.activated()
        }}
    }}
    
    signal activated()
}}'''
    
    def _get_panel_template(self) -> str:
        """Шаблон для панелі"""
        return '''import QtQuick
import Qt5Compat.GraphicalEffects

Rectangle {{
    id: root_{name}
    width: {width}; height: {height}
    color: "{color}"
    border.color: Qt.lighter(root_{name}.color, 1.5)
    border.width: 2
    radius: {border_radius}
    
    property bool active: false
    property string panelText: "{text}"
    
    // Ефект світіння при активації
    Glow {{
        anchors.fill: parent
        radius: 8
        samples: 17
        color: root_{name}.active ? "white" : "transparent"
        Behavior on color {{ ColorAnimation {{ duration: {animation_duration} }} }}
    }}
    
    // Текст панелі
    Text {{
        text: root_{name}.panelText
        anchors.centerIn: parent
        color: "white"
        font.bold: true
        font.pixelSize: {font_size}
    }}
    
    MouseArea {{
        anchors.fill: parent
        onClicked: {{
            console.log("{name} panel clicked")
            root_{name}.panelClicked()
        }}
    }}
    
    signal panelClicked()
}}'''
    
    def _get_klingon_button_template(self) -> str:
        """Шаблон для клінгонської кнопки з ShapePath"""
        return '''import QtQuick
import QtQuick.Shapes

Item {{
    id: root_{name}
    width: {width}; height: {height}
    property bool active: false
    property color buttonColor: "{color}"
    property string buttonText: "{text}"
    property string era: "{era}"

    Shape {{
        id: klingonShape
        anchors.fill: parent
        layer.enabled: true
        layer.samples: 8

        ShapePath {{
            fillColor: root_{name}.active ? "white" : root_{name}.buttonColor
            strokeColor: "#FFD700"
            strokeWidth: 2
            Behavior on fillColor {{ ColorAnimation {{ duration: {animation_duration} }} }}

            // Клінгонська форма з вирізом
            PathSvg {{
                path: "M 60,10 
                       L 45,25 
                       L 35,45 
                       L 15,70 
                       L 35,70 
                       L 45,55 
                       L 75,55 
                       L 85,70 
                       L 105,70 
                       L 85,45 
                       L 75,25 
                       Z"
            }}
        }}
    }}

    // Центральний круг
    Rectangle {{
        width: 16
        height: 16
        radius: 8
        color: "#000000"
        anchors.centerIn: parent
        border.color: "#FFD700"
        border.width: 2
    }}

    // Текст
    Text {{
        text: root_{name}.buttonText
        anchors.bottom: parent.bottom
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottomMargin: 5
        color: "#FFD700"
        font.bold: true
        font.pixelSize: {font_size}
        visible: root_{name}.buttonText !== ""
    }}

    MouseArea {{
        anchors.fill: parent
        hoverEnabled: true
        
        onPressed: root_{name}.active = true
        onReleased: root_{name}.active = false
        onExited: root_{name}.active = false
        
        onClicked: {{
            console.log("Klingon {name} clicked!")
            root_{name}.klingonClicked()
        }}
    }}
    
    signal klingonClicked()
}}'''
    
    def _get_romulan_button_template(self) -> str:
        """Шаблон для ромуланської кнопки"""
        return '''import QtQuick
import QtQuick.Shapes

Rectangle {{
    id: root_{name}
    width: {width}; height: {height}
    color: root_{name}.active ? "white" : "{color}"
    border.color: "#00FF99"
    border.width: 2
    radius: 5
    
    property bool active: false
    property color buttonColor: "{color}"
    property string buttonText: "{text}"

    // Ромуланська трапеція
    Shape {{
        anchors.fill: parent
        anchors.margins: 5
        layer.enabled: true

        ShapePath {{
            fillColor: "transparent"
            strokeColor: root_{name}.active ? "black" : "#00FF99"
            strokeWidth: 2
            Behavior on strokeColor {{ ColorAnimation {{ duration: {animation_duration} }} }}

            PathSvg {{
                path: "M 10,5 L {width_minus_10},5 L {width_minus_15},{height_minus_5} L 15,{height_minus_5} Z"
            }}
        }}
    }}

    Text {{
        text: root_{name}.buttonText
        anchors.centerIn: parent
        color: root_{name}.active ? "black" : "#00FF99"
        font.bold: true
        font.italic: true
        font.pixelSize: {font_size}
        Behavior on color {{ ColorAnimation {{ duration: {animation_duration} }} }}
    }}

    MouseArea {{
        anchors.fill: parent
        onPressed: root_{name}.active = true
        onReleased: root_{name}.active = false
        onExited: root_{name}.active = false
        
        onClicked: {{
            console.log("Romulan {name} activated")
            root_{name}.romulanActivated()
        }}
    }}
    
    signal romulanActivated()
}}'''
    
    def _get_cardassian_button_template(self) -> str:
        """Шаблон для кардасіанської кнопки"""
        return '''import QtQuick
import QtQuick.Shapes

Rectangle {{
    id: root_{name}
    width: {width}; height: {height}
    color: "transparent"
    
    property bool active: false
    property color buttonColor: "{color}"
    property string buttonText: "{text}"

    // Кардасіанський шестикутник
    Shape {{
        anchors.fill: parent
        layer.enabled: true

        ShapePath {{
            fillColor: root_{name}.active ? "white" : root_{name}.buttonColor
            strokeColor: "#FFD700"
            strokeWidth: 2
            Behavior on fillColor {{ ColorAnimation {{ duration: {animation_duration} }} }}

            PathSvg {{
                path: "M {width_div_2},10 L {width_minus_20},20 L {width_minus_15},{height_minus_20} L {width_div_2_plus_10},{height_minus_15} L {width_div_2_minus_10},{height_minus_15} L 15,{height_minus_20} L 20,20 Z"
            }}
        }}
    }}

    Text {{
        text: root_{name}.buttonText
        anchors.centerIn: parent
        color: root_{name}.active ? "black" : "#FFD700"
        font.bold: true
        font.pixelSize: {font_size}
        Behavior on color {{ ColorAnimation {{ duration: {animation_duration} }} }}
    }}

    MouseArea {{
        anchors.fill: parent
        onPressed: root_{name}.active = true
        onReleased: root_{name}.active = false
        onExited: root_{name}.active = false
        
        onClicked: {{
            console.log("Cardassian {name} activated")
            root_{name}.cardassianActivated()
        }}
    }}
    
    signal cardassianActivated()
}}'''

# Приклади використання
def demo_usage():
    """Демонстрація використання фабрики"""
    factory = LcarsComponentFactory()
    
    # 1. Генерація клінгонських кнопок
    print("🚀 Генерація клінгонських компонентів...")
    factory.generate_klingon_button(
        name="TacticalKlingon",
        color="#660000",
        text="TACTICAL",
        era="24th"
    )
    
    factory.generate_klingon_button(
        name="WeaponsKlingon", 
        color="#980000",
        text="WEAPONS",
        era="24th"
    )
    
    # 2. Генерація кнопок на основі зображень
    print("\n📁 Генерація кнопок з зображень...")
    factory.generate_component(
        component_type='button',
        name="TacticalChevron",
        image_path="resources/chevron_red.png",
        color="#CC0000",
        text="TACTICAL"
    )
    
    factory.generate_component(
        component_type='button',
        name="EnginePanel",
        image_path="resources/panel_teal.png", 
        color="#40E0D0",
        text="ENGINES"
    )
    
    # 3. Генерація панелей
    print("\n📋 Генерація панелей...")
    factory.generate_component(
        component_type='panel',
        name="MainPanel",
        image_path="resources/panel_bg.png",
        color="#1a1a1a",
        text="MAIN SYSTEMS",
        width=400,
        height=200
    )
    
    # 4. Генерація набору для фракції
    print("\n🎨 Генерація набору для фракції...")
    klingon_files = factory.generate_from_palette(
        faction="klingon",
        era="24th", 
        component_types=['button', 'panel', 'klingon_button']
    )
    
    print(f"\n✅ Всі компоненти згенеровано в: {factory.output_dir}")

if __name__ == "__main__":
    demo_usage()
