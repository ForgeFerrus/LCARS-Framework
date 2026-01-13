import QtQuick
import Qt5Compat.GraphicalEffects

Item {
    id: root_ShieldPanel
    width: 200; height: 80
    property bool active: false
    property color buttonColor: "#0099CC"
    property string buttonText: "SHIELDS"

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
        color: root_ShieldPanel.active ? "white" : root_ShieldPanel.buttonColor
        Behavior on color { ColorAnimation { duration: 150 } }
    }

    // Текст на кнопці
    Text {
        text: root_ShieldPanel.buttonText
        anchors.centerIn: parent
        color: root_ShieldPanel.active ? "black" : "white"
        font.bold: true
        font.pixelSize: 14
        Behavior on color { ColorAnimation { duration: 150 } }
    }

    // Інтерактивність
    MouseArea {
        anchors.fill: parent
        hoverEnabled: true
        
        onPressed: root_ShieldPanel.active = true
        onReleased: root_ShieldPanel.active = false
        onExited: root_ShieldPanel.active = false
        
        onClicked: {
            console.log("ShieldPanel activated")
            root_ShieldPanel.activated()
        }
    }
    
    signal activated()
}