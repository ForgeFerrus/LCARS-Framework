import QtQuick
import QtQuick.Shapes

Item {
    id: root
    property color btnColor: "#FF0000"
    property string text: ""
    signal clicked()

    width: 200
    height: 180

    Shape {
        id: klingonShape
        anchors.fill: parent
        layer.enabled: true
        layer.samples: 8 // Згладжування країв

        ShapePath {
            fillColor: root.btnColor
            strokeColor: "transparent"
            
            // Малюємо за годинниковою стрілкою (спрощений шлях за вашим фото)
            PathSvg {
                path: "M 50,0 
                       L 150,0 
                       L 150,20 
                       L 200,20 
                       L 160,80 
                       L 180,95 
                       L 100,200 
                       L 20,95 
                       L 40,80 
                       L 0,20 
                       L 50,20 
                       Z"
            }
        }
    }

    // Текст по центру кнопки
    Text {
        anchors.centerIn: parent
        anchors.verticalCenterOffset: -10 // Зсув, бо низ гострий
        text: root.text
        color: "white"
        font.bold: true
        font.pixelSize: 16
    }

    MouseArea {
        anchors.fill: parent
        onClicked: root.clicked()
        onPressed: klingonShape.opacity = 0.7
        onReleased: klingonShape.opacity = 1.0
    }
}
