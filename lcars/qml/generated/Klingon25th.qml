import QtQuick
import QtQuick.Shapes

Item {
    id: root_Klingon25th
    width: 120; height: 80
    property bool active: false
    property color buttonColor: "#A61A35"
    property string buttonText: "25TH"
    property string era: "25th"

    Shape {
        id: klingonShape
        anchors.fill: parent
        layer.enabled: true
        layer.samples: 8

        ShapePath {
            fillColor: root_Klingon25th.active ? "white" : root_Klingon25th.buttonColor
            strokeColor: "#FFD700"
            strokeWidth: 2
            Behavior on fillColor { ColorAnimation { duration: 150 } }

            // Клінгонська форма з вирізом
            PathSvg {
                path: "M 60,10 
                       L 45,25 
                       L 35,45 
                       L 15,70 
                       L 35,70 
                       L 45,55 
                       L 75,55 
                       L 85,70 
                       L 105,70 
                       L 85,45 
                       L 75,25 
                       Z"
            }
        }
    }

    // Центральний круг
    Rectangle {
        width: 16
        height: 16
        radius: 8
        color: "#000000"
        anchors.centerIn: parent
        border.color: "#FFD700"
        border.width: 2
    }

    // Текст
    Text {
        text: root_Klingon25th.buttonText
        anchors.bottom: parent.bottom
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottomMargin: 5
        color: "#FFD700"
        font.bold: true
        font.pixelSize: 14
        visible: root_Klingon25th.buttonText !== ""
    }

    MouseArea {
        anchors.fill: parent
        hoverEnabled: true
        
        onPressed: root_Klingon25th.active = true
        onReleased: root_Klingon25th.active = false
        onExited: root_Klingon25th.active = false
        
        onClicked: {
            console.log("Klingon Klingon25th clicked!")
            root_Klingon25th.klingonClicked()
        }
    }
    
    signal klingonClicked()
}