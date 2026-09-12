"""Compatibility shim.

The implementation of the LCARS component factory has been moved to
`lcars.engineering.generators.component_factory`. This module re-exports the
`LcarsComponentFactory` class for backward compatibility with existing imports.
"""

from lcars.engineering.generators.component_factory import LcarsComponentFactory  # type: ignore

__all__ = ["LcarsComponentFactory"]
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
    Text {
        text: root_{name}.panelText
        anchors.centerIn: parent
        color: "white"
        font.bold: false
        font.pixelSize: {font_size}
    }
    
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
        font.bold: false
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
        font.bold: false
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
        font.bold: false
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
