import QtQuick 2.15
import QtQuick.Controls 2.15

ApplicationWindow {
    visible: true
    width: 1024
    height: 768
    color: "black"
    
    // Прибираємо рамку вікна ОС
    flags: Qt.FramelessWindowHint 

    // --- КОЛЬОРИ LCARS ---
    readonly property color c_orange: "#ff9c00"
    readonly property color c_purple: "#cc99cc"
    readonly property color c_red: "#cc6666"

    // --- ГОЛОВНИЙ ЛІКОТЬ (спрощена версія) ---
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
        width: 100
        anchors.left: parent.left
        anchors.top: lcarsElbow.bottom
        anchors.bottom: parent.bottom
        anchors.margins: 10
        color: c_orange
    }

    // --- ЗАГОЛОВОК ---
    Text {
        text: "LCARS SYSTEM 47"
        font.family: "Arial"
        font.pixelSize: 40
        font.bold: true
        color: c_orange
        anchors.left: lcarsElbow.right
        anchors.top: parent.top
        anchors.margins: 20
    }

    // --- КНОПКИ МЕНЮ (Зліва) ---
    Column {
        anchors.left: parent.left
        anchors.top: lcarsElbow.bottom
        anchors.topMargin: 40
        anchors.leftMargin: 15
        spacing: 5

        // Компонент кнопки
        component LcarsButton: Rectangle {
            width: 80; height: 35
            color: btnColor
            property string label: ""
            property color btnColor: c_purple
            
            Text {
                text: label.toUpperCase()
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
                    console.log("Clicked: " + label)
                    con.button_clicked(label)
                    if(label === "Exit") con.exit_system()
                }
                onPressed: parent.color = "white"
                onReleased: parent.color = btnColor
            }
        }

        LcarsButton { label: "Library"; btnColor: c_purple }
        LcarsButton { label: "Tactical"; btnColor: c_red }
        LcarsButton { label: "Sensors"; btnColor: c_orange }
        
        Item { width: 80; height: 20 }
        
        LcarsButton { label: "Exit"; btnColor: c_red }
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

        // Клінгонська кнопка в контентній області
        KlingonButton {
            anchors.centerIn: parent
            btnColor: "#660000"
            text: "KLINGON"
            onClicked: {
                console.log("Klingon button clicked!")
                con.button_clicked("Klingon")
            }
        }

        Text {
            text: "SYSTEM ONLINE\nAWAITING INPUT..."
            color: c_orange
            font.pixelSize: 24
            anchors.top: parent.top
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.topMargin: 20
        }
    }
}
