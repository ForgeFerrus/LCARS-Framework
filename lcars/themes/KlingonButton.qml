import QtQuick
import QtQuick.Shapes

Rectangle {
    id: root
    property color btnColor: "#660000"
    property string text: ""
    property string factionEra: "klingon_24th"
    signal clicked()

    width: 120
    height: 80
    color: "#000000"  // Чорний фон для видимості
    border.color: "#FFD700"
    border.width: 2
    radius: 5

    Shape {
        id: klingonShape
        anchors.centerIn: parent
        width: parent.width - 20
        height: parent.height - 20
        layer.enabled: true
        layer.samples: 8

        ShapePath {
            fillColor: root.btnColor
            strokeColor: "#FFFFFF"
            strokeWidth: 2
            
            // Спрощена клінгонська форма
            PathSvg {
                path: "M 50,5 
                       L 70,5 
                       L 70,15 
                       L 85,15 
                       L 65,35 
                       L 75,45 
                       L 50,65 
                       L 25,45 
                       L 35,35 
                       L 15,15 
                       L 30,15 
                       L 30,5 
                       L 50,5 
                       Z"
            }
        }
    }

    // Центральний круг
    Rectangle {
        width: 12
        height: 12
        radius: 6
        color: "#000000"
        anchors.centerIn: parent
        border.color: "#FFD700"
        border.width: 2
    }

    MouseArea {
        anchors.fill: parent
        onClicked: {
            console.log("Klingon QML button clicked!")
            root.clicked()
        }
        onPressed: root.color = "#333333"
        onReleased: root.color = "#000000"
        
        hoverEnabled: true
        onEntered: root.border.color = "#FFFFFF"
        onExited: root.border.color = "#FFD700"
    }
}
