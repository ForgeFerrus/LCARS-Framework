import QtQuick
import QtQuick.Shapes

Item {
    id: root
    property color btnColor: "#660000"
    property string text: ""
    property string factionEra: "klingon_24th"
    signal clicked()

    width: 120
    height: 80

    Shape {
        id: klingonShape
        anchors.fill: parent
        layer.enabled: true
        layer.samples: 8 // Згладжування країв

        ShapePath {
            fillColor: root.btnColor
            strokeColor: "transparent"
            strokeWidth: 0
            
            // Клінгонська форма з вирізом з трьох сторін
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
    }

    MouseArea {
        anchors.fill: parent
        onClicked: root.clicked()
        onPressed: klingonShape.opacity = 0.7
        onReleased: klingonShape.opacity = 1.0
    }
}
