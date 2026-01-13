import QtQuick
import Qt5Compat.GraphicalEffects

Rectangle {
    id: root_StatusPanel
    width: 400; height: 200
    color: "#1a1a1a"
    border.color: Qt.lighter(root_StatusPanel.color, 1.5)
    border.width: 2
    radius: 0
    
    property bool active: false
    property string panelText: "SYSTEM STATUS"
    
    // Ефект світіння при активації
    Glow {
        anchors.fill: parent
        radius: 8
        samples: 17
        color: root_StatusPanel.active ? "white" : "transparent"
        Behavior on color { ColorAnimation { duration: 150 } }
    }
    
    // Текст панелі
    Text {
        text: root_StatusPanel.panelText
        anchors.centerIn: parent
        color: "white"
        font.bold: true
        font.pixelSize: 14
    }
    
    MouseArea {
        anchors.fill: parent
        onClicked: {
            console.log("StatusPanel panel clicked")
            root_StatusPanel.panelClicked()
        }
    }
    
    signal panelClicked()
}