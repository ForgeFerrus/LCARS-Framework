import QtQuick
import QtQuick.Shapes

Rectangle {
    id: root_CardassianButton3
    width: 100; height: 60
    color: "transparent"
    
    property bool active: false
    property color buttonColor: "#FF6600"
    property string buttonText: "CAR3"

    // Кардасіанський шестикутник
    Shape {
        anchors.fill: parent
        layer.enabled: true

        ShapePath {
            fillColor: root_CardassianButton3.active ? "white" : root_CardassianButton3.buttonColor
            strokeColor: "#FFD700"
            strokeWidth: 2
            Behavior on fillColor { ColorAnimation { duration: 150 } }

            PathSvg {
                path: "M 50,10 L 80,20 L 85,40 L 60,45 L 40,45 L 15,40 L 20,20 Z"
            }
        }
    }

    Text {
        text: root_CardassianButton3.buttonText
        anchors.centerIn: parent
        color: root_CardassianButton3.active ? "black" : "#FFD700"
        font.bold: true
        font.pixelSize: 14
        Behavior on color { ColorAnimation { duration: 150 } }
    }

    MouseArea {
        anchors.fill: parent
        onPressed: root_CardassianButton3.active = true
        onReleased: root_CardassianButton3.active = false
        onExited: root_CardassianButton3.active = false
        
        onClicked: {
            console.log("Cardassian CardassianButton3 activated")
            root_CardassianButton3.cardassianActivated()
        }
    }
    
    signal cardassianActivated()
}