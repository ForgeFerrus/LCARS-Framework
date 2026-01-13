import QtQuick
import Qt5Compat.GraphicalEffects

Item {
    id: root_EngineButton
    width: 250; height: 80
    property bool active: false
    property color buttonColor: "#40E0D0"
    property string buttonText: "ENGINES"

    // Основне зображення з вашим дизайном
    Image {
        id: img
        source: "resources/engine_icon.png"
        anchors.fill: parent
        visible: false // Ховаємо для накладання кольору
        fillMode: Image.PreserveAspectFit
    }

    // Шейдер для динамічної зміни кольору
    ColorOverlay {
        id: overlay
        anchors.fill: img
        source: img
        color: root_EngineButton.active ? "white" : root_EngineButton.buttonColor
        Behavior on color { ColorAnimation { duration: 150 } }
    }

    // Текст на кнопці
    Text {
        text: root_EngineButton.buttonText
        anchors.centerIn: parent
        color: root_EngineButton.active ? "black" : "white"
        font.bold: true
        font.pixelSize: 14
        Behavior on color { ColorAnimation { duration: 150 } }
    }

    // Інтерактивність
    MouseArea {
        anchors.fill: parent
        hoverEnabled: true
        
        onPressed: root_EngineButton.active = true
        onReleased: root_EngineButton.active = false
        onExited: root_EngineButton.active = false
        
        onClicked: {
            console.log("EngineButton activated")
            root_EngineButton.activated()
        }
    }
    
    signal activated()
}