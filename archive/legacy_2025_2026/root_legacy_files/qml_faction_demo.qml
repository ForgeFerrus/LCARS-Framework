import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

ApplicationWindow {
    visible: true
    width: 1000
    height: 800
    color: "black"
    
    // Прибираємо рамку вікна
    flags: Qt.FramelessWindowHint 

    // --- КОЛЬОРИ LCARS ---
    readonly property color c_orange: "#ff9c00"
    readonly property color c_purple: "#cc99cc"
    readonly property color c_red: "#cc6666"

    // --- ГОЛОВНИЙ ЛІКОТЬ ---
    Rectangle {
        id: lcarsElbow
        width: 400; height: 30
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.margins: 10
        color: c_orange
    }

    // --- Бічна панель ---
    Rectangle {
        width: 120
        anchors.left: parent.left
        anchors.top: lcarsElbow.bottom
        anchors.bottom: parent.bottom
        anchors.margins: 10
        color: c_orange
    }

    // --- ЗАГОЛОВОК ---
    Text {
        text: "🚀 Фракційні LCARS Інтерфейси (QML)"
        font.family: "Arial"
        font.pixelSize: 32
        font.bold: true
        color: c_orange
        anchors.left: lcarsElbow.right
        anchors.top: parent.top
        anchors.margins: 20
    }

    // --- КНОПКИ ПЕРЕКЛЮЧЕННЯ ФРАКЦІЙ ---
    Column {
        anchors.left: parent.left
        anchors.top: lcarsElbow.bottom
        anchors.topMargin: 40
        anchors.leftMargin: 15
        spacing: 10

        // Компонент кнопки фракції
        component FactionButton: Rectangle {
            width: 100; height: 40
            color: btnColor
            property string faction: ""
            property color btnColor: c_purple
            
            Text {
                text: faction.toUpperCase()
                anchors.right: parent.right
                anchors.rightMargin: 5
                anchors.verticalCenter: parent.verticalCenter
                font.bold: true
                font.pixelSize: 12
                color: "white"
            }
            
            MouseArea {
                anchors.fill: parent
                onClicked: {
                    console.log("Faction: " + faction)
                    bridge.button_clicked(faction)
                    // Оновлюємо кнопки
                    klingonButton.btnColor = bridge.get_faction_color("klingon_24th")
                    romulanButton.btnColor = bridge.get_faction_color("romulan_24th")
                    cardassianButton.btnColor = bridge.get_faction_color("cardassian_24th")
                }
                onPressed: parent.color = "white"
                onReleased: parent.color = btnColor
            }
        }

        FactionButton { faction: "Klingon"; btnColor: "#660000" }
        FactionButton { faction: "Romulan"; btnColor: "#0066cc" }
        FactionButton { faction: "Cardassian"; btnColor: "#cc6600" }
        
        Item { width: 100; height: 20 }
        
        FactionButton { faction: "Exit"; btnColor: c_red }
    }

    // --- КОНТЕНТНА ЧАСТИНА ---
    Rectangle {
        id: contentArea
        color: "transparent"
        border.color: c_purple
        border.width: 2
        anchors.left: lcarsElbow.right
        anchors.top: lcarsElbow.bottom
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.margins: 20

        // Заголовок контенту
        Text {
            text: "QML ShapePath Фракційні Кнопки"
            color: c_orange
            font.pixelSize: 24
            font.bold: true
            anchors.top: parent.top
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.topMargin: 20
        }

        // Кнопки фракцій
        Row {
            anchors.centerIn: parent
            spacing: 30

            // Клінгонська кнопка
            Column {
                spacing: 10
                KlingonButton {
                    id: klingonButton
                    btnColor: bridge.get_faction_color("klingon_24th")
                    text: ""
                    onClicked: {
                        console.log("Klingon button clicked!")
                        bridge.button_clicked("Klingon")
                    }
                }
                Text {
                    text: "KLINGON"
                    color: "#660000"
                    font.bold: true
                    font.pixelSize: 14
                    anchors.horizontalCenter: parent.horizontalCenter
                }
            }

            // Ромуланська кнопка (поки що прямокутник)
            Column {
                spacing: 10
                Rectangle {
                    width: 120; height: 80
                    color: bridge.get_faction_color("romulan_24th")
                    radius: 10
                    Text {
                        anchors.centerIn: parent
                        text: "ROMULAN"
                        color: "white"
                        font.bold: true
                    }
                    MouseArea {
                        anchors.fill: parent
                        onClicked: {
                            console.log("Romulan button clicked!")
                            bridge.button_clicked("Romulan")
                        }
                    }
                }
                Text {
                    text: "ROMULAN"
                    color: "#0066cc"
                    font.bold: true
                    font.pixelSize: 14
                    anchors.horizontalCenter: parent.horizontalCenter
                }
            }

            // Кардасіанська кнопка (поки що прямокутник)
            Column {
                spacing: 10
                Rectangle {
                    width: 120; height: 80
                    color: bridge.get_faction_color("cardassian_24th")
                    radius: 5
                    Text {
                        anchors.centerIn: parent
                        text: "CARDASSIAN"
                        color: "white"
                        font.bold: true
                    }
                    MouseArea {
                        anchors.fill: parent
                        onClicked: {
                            console.log("Cardassian button clicked!")
                            bridge.button_clicked("Cardassian")
                        }
                    }
                }
                Text {
                    text: "CARDASSIAN"
                    color: "#cc6600"
                    font.bold: true
                    font.pixelSize: 14
                    anchors.horizontalCenter: parent.horizontalCenter
                }
            }
        }

        // Інформаційний текст
        Text {
            text: "✅ QML ShapePath кнопки з динамічними кольорами фракцій\n✅ Векторна графіка - ідеально масштабується\n✅ Інтеграція з існуючими палітрами"
            color: c_orange
            font.pixelSize: 16
            anchors.bottom: parent.bottom
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.bottomMargin: 20
        }
    }
}
