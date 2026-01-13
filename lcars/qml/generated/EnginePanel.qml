import QtQuick
import Qt5Compat.GraphicalEffects

Item {
    id: root_EnginePanel
    width: 200; height: 80
    property bool active: false
    property color buttonColor: "#40E0D0"
    property string buttonText: "ENGINES"

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
        color: root_EnginePanel.active ? "white" : root_EnginePanel.buttonColor
        Behavior on color { ColorAnimation { duration: 150 } }
    }

    // Текст на кнопці
    Text {
        text: root_EnginePanel.buttonText
        anchors.centerIn: parent
        color: root_EnginePanel.active ? "black" : "white"
        font.bold: true
        font.pixelSize: 14
        Behavior on color { ColorAnimation { duration: 150 } }
    }

    // Інтерактивність
    MouseArea {
        anchors.fill: parent
        hoverEnabled: true
        
        onPressed: root_EnginePanel.active = true
        onReleased: root_EnginePanel.active = false
        onExited: root_EnginePanel.active = false
        
        onClicked: {
            console.log("EnginePanel activated")
            root_EnginePanel.activated()
        }
    }
    
    signal activated()
}