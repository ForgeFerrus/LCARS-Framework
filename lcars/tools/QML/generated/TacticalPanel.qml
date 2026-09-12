import QtQuick
import QtQuick.Effects

Rectangle {
    id: root_TacticalPanel
    width: 300; height: 150
    color: "#2d1b1b"
    border.color: Qt.lighter(root_TacticalPanel.color, 1.5)
    border.width: 2
    radius: 5
    
    property bool active: false
    property string panelText: "TACTICAL"
    
    // Простий ефект світіння при активації
    Rectangle {
        anchors.fill: parent
        color: "transparent"
        border.color: root_TacticalPanel.active ? "white" : "transparent"
        border.width: root_TacticalPanel.active ? 3 : 0
        radius: parent.radius
        Behavior on border.width { NumberAnimation { duration: 150 } }
    }
    
    // Текст панелі
    Text {
        text: root_TacticalPanel.panelText
        anchors.centerIn: parent
        color: "white"
        font.bold: true
        font.pixelSize: 14
    }
    
    MouseArea {
        anchors.fill: parent
        onClicked: {
            console.log("TacticalPanel panel clicked")
            root_TacticalPanel.panelClicked()
        }
    }
    
    signal panelClicked()
}