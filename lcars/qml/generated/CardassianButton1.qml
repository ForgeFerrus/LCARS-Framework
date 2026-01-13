import QtQuick
import QtQuick.Shapes

Rectangle {
    id: root_CardassianButton1
    width: 100; height: 60
    color: "transparent"
    
    property bool active: false
    property color buttonColor: "#CC3300"
    property string buttonText: "CAR1"

    // Кардасіанський шестикутник
    Shape {
        anchors.fill: parent
        layer.enabled: true

        ShapePath {
            fillColor: root_CardassianButton1.active ? "white" : root_CardassianButton1.buttonColor
            strokeColor: "#FFD700"
            strokeWidth: 2
            Behavior on fillColor { ColorAnimation { duration: 150 } }

            PathSvg {
                path: "M 50,10 L 80,20 L 85,40 L 60,45 L 40,45 L 15,40 L 20,20 Z"
            }
        }
    }

    Text {
        text: root_CardassianButton1.buttonText
        anchors.centerIn: parent
        color: root_CardassianButton1.active ? "black" : "#FFD700"
        font.bold: true
        font.pixelSize: 14
        Behavior on color { ColorAnimation { duration: 150 } }
    }

    MouseArea {
        anchors.fill: parent
        onPressed: root_CardassianButton1.active = true
        onReleased: root_CardassianButton1.active = false
        onExited: root_CardassianButton1.active = false
        
        onClicked: {
            console.log("Cardassian CardassianButton1 activated")
            root_CardassianButton1.cardassianActivated()
        }
    }
    
    signal cardassianActivated()
}