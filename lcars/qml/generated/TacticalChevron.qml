import QtQuick
import Qt5Compat.GraphicalEffects

Item {
    id: root_TacticalChevron
    width: 200; height: 80
    property bool active: false
    property color buttonColor: "#CC0000"
    property string buttonText: "TACTICAL"

    // Основне зображення з вашим дизайном
    Image {
        id: img
        source: ""
        anchors.fill: parent
        visible: false // Ховаємо для накладання кольору
        fillMode: Image.PreserveAspectFit
    }

    // Шейдер для динамічної зміни кольору
    ColorOverlay {
        id: overlay
        anchors.fill: img
        source: img
        color: root_TacticalChevron.active ? "white" : root_TacticalChevron.buttonColor
        Behavior on color { ColorAnimation { duration: 150 } }
    }

    // Текст на кнопці
    Text {
        text: root_TacticalChevron.buttonText
        anchors.centerIn: parent
        color: root_TacticalChevron.active ? "black" : "white"
        font.bold: true
        font.pixelSize: 14
        Behavior on color { ColorAnimation { duration: 150 } }
    }

    // Інтерактивність
    MouseArea {
        anchors.fill: parent
        hoverEnabled: true
        
        onPressed: root_TacticalChevron.active = true
        onReleased: root_TacticalChevron.active = false
        onExited: root_TacticalChevron.active = false
        
        onClicked: {
            console.log("TacticalChevron activated")
            root_TacticalChevron.activated()
        }
    }
    
    signal activated()
}