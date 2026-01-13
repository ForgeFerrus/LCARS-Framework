import QtQuick
import QtQuick.Shapes

Rectangle {
    id: root_RomulanButton4
    width: 120; height: 60
    color: root_RomulanButton4.active ? "white" : "#99CC99"
    border.color: "#00FF99"
    border.width: 2
    radius: 5
    
    property bool active: false
    property color buttonColor: "#99CC99"
    property string buttonText: "ROM4"

    // Ромуланська трапеція
    Shape {
        anchors.fill: parent
        anchors.margins: 5
        layer.enabled: true

        ShapePath {
            fillColor: "transparent"
            strokeColor: root_RomulanButton4.active ? "black" : "#00FF99"
            strokeWidth: 2
            Behavior on strokeColor { ColorAnimation { duration: 150 } }

            PathSvg {
                path: "M 10,5 L 110,5 L 105,55 L 15,55 Z"
            }
        }
    }

    Text {
        text: root_RomulanButton4.buttonText
        anchors.centerIn: parent
        color: root_RomulanButton4.active ? "black" : "#00FF99"
        font.bold: true
        font.italic: true
        font.pixelSize: 14
        Behavior on color { ColorAnimation { duration: 150 } }
    }

    MouseArea {
        anchors.fill: parent
        onPressed: root_RomulanButton4.active = true
        onReleased: root_RomulanButton4.active = false
        onExited: root_RomulanButton4.active = false
        
        onClicked: {
            console.log("Romulan RomulanButton4 activated")
            root_RomulanButton4.romulanActivated()
        }
    }
    
    signal romulanActivated()
}