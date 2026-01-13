import QtQuick
import QtQuick.Shapes

Rectangle {
    id: root_RomulanButton1
    width: 120; height: 60
    color: root_RomulanButton1.active ? "white" : "#006666"
    border.color: "#00FF99"
    border.width: 2
    radius: 5
    
    property bool active: false
    property color buttonColor: "#006666"
    property string buttonText: "ROM1"

    // Ромуланська трапеція
    Shape {
        anchors.fill: parent
        anchors.margins: 5
        layer.enabled: true

        ShapePath {
            fillColor: "transparent"
            strokeColor: root_RomulanButton1.active ? "black" : "#00FF99"
            strokeWidth: 2
            Behavior on strokeColor { ColorAnimation { duration: 150 } }

            PathSvg {
                path: "M 10,5 L 110,5 L 105,55 L 15,55 Z"
            }
        }
    }

    Text {
        text: root_RomulanButton1.buttonText
        anchors.centerIn: parent
        color: root_RomulanButton1.active ? "black" : "#00FF99"
        font.bold: true
        font.italic: true
        font.pixelSize: 14
        Behavior on color { ColorAnimation { duration: 150 } }
    }

    MouseArea {
        anchors.fill: parent
        onPressed: root_RomulanButton1.active = true
        onReleased: root_RomulanButton1.active = false
        onExited: root_RomulanButton1.active = false
        
        onClicked: {
            console.log("Romulan RomulanButton1 activated")
            root_RomulanButton1.romulanActivated()
        }
    }
    
    signal romulanActivated()
}