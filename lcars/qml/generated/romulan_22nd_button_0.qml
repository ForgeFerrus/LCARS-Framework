import QtQuick
import Qt5Compat.GraphicalEffects

Item {
    id: root_romulan_22nd_button_0
    width: 200; height: 80
    property bool active: false
    property color buttonColor: "#336666"
    property string buttonText: "ROMULAN BUTTON"

    // Основне зображення з вашим дизайном
    Image {
        id: img
        source: "resources/romulan_22nd_button.png"
        anchors.fill: parent
        visible: false // Ховаємо для накладання кольору
        fillMode: Image.PreserveAspectFit
    }

    // Шейдер для динамічної зміни кольору
    ColorOverlay {
        id: overlay
        anchors.fill: img
        source: img
        color: root_romulan_22nd_button_0.active ? "white" : root_romulan_22nd_button_0.buttonColor
        Behavior on color { ColorAnimation { duration: 150 } }
    }

    // Текст на кнопці
    Text {
        text: root_romulan_22nd_button_0.buttonText
        anchors.centerIn: parent
        color: root_romulan_22nd_button_0.active ? "black" : "white"
        font.bold: true
        font.pixelSize: 14
        Behavior on color { ColorAnimation { duration: 150 } }
    }

    // Інтерактивність
    MouseArea {
        anchors.fill: parent
        hoverEnabled: true
        
        onPressed: root_romulan_22nd_button_0.active = true
        onReleased: root_romulan_22nd_button_0.active = false
        onExited: root_romulan_22nd_button_0.active = false
        
        onClicked: {
            console.log("romulan_22nd_button_0 activated")
            root_romulan_22nd_button_0.activated()
        }
    }
    
    signal activated()
}