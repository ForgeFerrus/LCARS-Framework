import QtQuick 2.15
import QtQuick.Controls 2.15

ApplicationWindow {
    visible: true
    width: 800
    height: 600
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
        width: 300; height: 30
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.margins: 10
        color: c_orange
    }

    // --- Бічна панель ---
    Rectangle {
        width: 100
        anchors.left: parent.left
        anchors.top: lcarsElbow.bottom
        anchors.bottom: parent.bottom
        anchors.margins: 10
        color: c_orange
    }

    // --- ЗАГОЛОВОК ---
    Text {
        text: "🚀 Klingon ShapePath Button Demo"
        font.family: "Arial"
        font.pixelSize: 28
        font.bold: true
        color: c_orange
        anchors.left: lcarsElbow.right
        anchors.top: parent.top
        anchors.margins: 20
    }

    // --- КНОПКИ ПЕРЕКЛЮЧЕННЯ ЕР ---
    Column {
        anchors.left: parent.left
        anchors.top: lcarsElbow.bottom
        anchors.topMargin: 40
        anchors.leftMargin: 15
        spacing: 10

        // Компонент кнопки ери
        component EraButton: Rectangle {
            width: 80; height: 35
            color: btnColor
            property string era: ""
            property color btnColor: c_purple
            
            Text {
                text: era.split("_")[1].toUpperCase()
                anchors.right: parent.right
                anchors.rightMargin: 5
                anchors.verticalCenter: parent.verticalCenter
                font.bold: true
                font.pixelSize: 11
                color: "white"
            }
            
            MouseArea {
                anchors.fill: parent
                onClicked: {
                    console.log("Era: " + era)
                    bridge.button_clicked(era)
                    // Оновлюємо колір клінгонської кнопки
                    klingonButton.btnColor = bridge.get_klingon_color(era)
                }
                onPressed: parent.color = "white"
                onReleased: parent.color = btnColor
            }
        }

        EraButton { era: "klingon_22nd"; btnColor: "#8B0000" }
        EraButton { era: "klingon_23rd"; btnColor: "#660000" }
        EraButton { era: "klingon_24th"; btnColor: "#990000" }
        EraButton { era: "klingon_25th"; btnColor: "#CC0000" }
        
        Item { width: 80; height: 20 }
        
        EraButton { era: "Exit"; btnColor: c_red }
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
            text: "✅ ShapePath Klingon Button"
            color: c_orange
            font.pixelSize: 20
            font.bold: true
            anchors.top: parent.top
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.topMargin: 20
        }

        // Клінгонська кнопка
        KlingonButton {
            id: klingonButton
            anchors.centerIn: parent
            btnColor: bridge.get_klingon_color("klingon_24th")
            text: ""
            onClicked: {
                console.log("Klingon button clicked!")
                bridge.button_clicked("Klingon")
            }
        }

        // Опис кнопки
        Text {
            text: "✨ Векторна клінгонська кнопка з ShapePath\n✨ Ідеально масштабується на будь-якому екрані\n✨ Динамічні кольори для різних ер\n✨ Згладжування країв (anti-aliasing)"
            color: c_orange
            font.pixelSize: 14
            anchors.bottom: parent.bottom
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.bottomMargin: 20
        }
    }
}
