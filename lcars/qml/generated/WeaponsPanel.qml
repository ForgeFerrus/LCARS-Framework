import QtQuick
import Qt5Compat.GraphicalEffects

Item {
    id: root_WeaponsPanel
    width: 200; height: 80
    property bool active: false
    property color buttonColor: "#FF6600"
    property string buttonText: "WEAPONS"

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
        color: root_WeaponsPanel.active ? "white" : root_WeaponsPanel.buttonColor
        Behavior on color { ColorAnimation { duration: 150 } }
    }

    // Текст на кнопці
    Text {
        text: root_WeaponsPanel.buttonText
        anchors.centerIn: parent
        color: root_WeaponsPanel.active ? "black" : "white"
        font.bold: true
        font.pixelSize: 14
        Behavior on color { ColorAnimation { duration: 150 } }
    }

    // Інтерактивність
    MouseArea {
        anchors.fill: parent
        hoverEnabled: true
        
        onPressed: root_WeaponsPanel.active = true
        onReleased: root_WeaponsPanel.active = false
        onExited: root_WeaponsPanel.active = false
        
        onClicked: {
            console.log("WeaponsPanel activated")
            root_WeaponsPanel.activated()
        }
    }
    
    signal activated()
}