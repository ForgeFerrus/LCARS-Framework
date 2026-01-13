import QtQuick
import Qt5Compat.GraphicalEffects

Rectangle {
    id: root_MainPanel
    width: 400; height: 200
    color: "#1a1a1a"
    border.color: Qt.lighter(root_MainPanel.color, 1.5)
    border.width: 2
    radius: 5
    
    property bool active: false
    property string panelText: "MAIN SYSTEMS"
    
    // Ефект світіння при активації
    Glow {
        anchors.fill: parent
        radius: 8
        samples: 17
        color: root_MainPanel.active ? "white" : "transparent"
        Behavior on color { ColorAnimation { duration: 150 } }
    }
    
    // Текст панелі
    Text {
        text: root_MainPanel.panelText
        anchors.centerIn: parent
        color: "white"
        font.bold: true
        font.pixelSize: 14
    }
    
    MouseArea {
        anchors.fill: parent
        onClicked: {
            console.log("MainPanel panel clicked")
            root_MainPanel.panelClicked()
        }
    }
    
    signal panelClicked()
}