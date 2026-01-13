import QtQuick
import Qt5Compat.GraphicalEffects

Rectangle {
    id: root_EngineeringPanel
    width: 300; height: 150
    color: "#1b2d1b"
    border.color: Qt.lighter(root_EngineeringPanel.color, 1.5)
    border.width: 2
    radius: 5
    
    property bool active: false
    property string panelText: "ENGINEERING"
    
    // Ефект світіння при активації
    Glow {
        anchors.fill: parent
        radius: 8
        samples: 17
        color: root_EngineeringPanel.active ? "white" : "transparent"
        Behavior on color { ColorAnimation { duration: 150 } }
    }
    
    // Текст панелі
    Text {
        text: root_EngineeringPanel.panelText
        anchors.centerIn: parent
        color: "white"
        font.bold: true
        font.pixelSize: 14
    }
    
    MouseArea {
        anchors.fill: parent
        onClicked: {
            console.log("EngineeringPanel panel clicked")
            root_EngineeringPanel.panelClicked()
        }
    }
    
    signal panelClicked()
}