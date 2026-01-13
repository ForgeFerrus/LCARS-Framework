import QtQuick
import Qt5Compat.GraphicalEffects

Rectangle {
    id: root_cardassian_24th_panel_1
    width: 200; height: 80
    color: "#CC0000"
    border.color: Qt.lighter(root_cardassian_24th_panel_1.color, 1.5)
    border.width: 2
    radius: 0
    
    property bool active: false
    property string panelText: "CARDASSIAN PANEL"
    
    // Ефект світіння при активації
    Glow {
        anchors.fill: parent
        radius: 8
        samples: 17
        color: root_cardassian_24th_panel_1.active ? "white" : "transparent"
        Behavior on color { ColorAnimation { duration: 150 } }
    }
    
    // Текст панелі
    Text {
        text: root_cardassian_24th_panel_1.panelText
        anchors.centerIn: parent
        color: "white"
        font.bold: true
        font.pixelSize: 14
    }
    
    MouseArea {
        anchors.fill: parent
        onClicked: {
            console.log("cardassian_24th_panel_1 panel clicked")
            root_cardassian_24th_panel_1.panelClicked()
        }
    }
    
    signal panelClicked()
}