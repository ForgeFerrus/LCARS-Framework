import QtQuick
import QtQuick.Controls

ApplicationWindow {
    visible: true
    width: 800
    height: 600
    color: "black"
    title: "🚀 Generated LCARS Components Demo"

    // Імпортуємо згенеровані компоненти
    // В реальному додатку вони будуть в папці lcars/qml/generated/

    Rectangle {
        anchors.fill: parent
        color: "#000000"

        // Заголовок
        Text {
            text: "🚀 GENERATED LCARS COMPONENTS"
            color: "#FFD700"
            font.pixelSize: 24
            font.bold: true
            anchors.top: parent.top
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.topMargin: 20
        }

        // Клінгонські кнопки
        Column {
            anchors.left: parent.left
            anchors.top: parent.top
            anchors.topMargin: 80
            anchors.leftMargin: 20
            spacing: 10

            Text {
                text: "🔺 KLINGON BUTTONS"
                color: "#CC0000"
                font.pixelSize: 16
                font.bold: true
            }

            Row {
                spacing: 10
                // Тут будуть імпортовані компоненти:
                // Klingon22nd { onKlingonClicked: console.log("22nd clicked") }
                // Klingon23rd { onKlingonClicked: console.log("23rd clicked") }
                // Klingon24th { onKlingonClicked: console.log("24th clicked") }
                // Klingon25th { onKlingonClicked: console.log("25th clicked") }
                
                Rectangle { width: 120; height: 80; color: "#400000"; border.color: "#FFD700"; border.width: 2 }
                Rectangle { width: 120; height: 80; color: "#CC0000"; border.color: "#FFD700"; border.width: 2 }
                Rectangle { width: 120; height: 80; color: "#660000"; border.color: "#FFD700"; border.width: 2 }
                Rectangle { width: 120; height: 80; color: "#A61A35"; border.color: "#FFD700"; border.width: 2 }
            }
        }

        // Ромуланські кнопки
        Column {
            anchors.left: parent.left
            anchors.top: parent.top
            anchors.topMargin: 200
            anchors.leftMargin: 20
            spacing: 10

            Text {
                text: "🔻 ROMULAN BUTTONS"
                color: "#00FF99"
                font.pixelSize: 16
                font.bold: true
            }

            Row {
                spacing: 10
                // RomulanButton1 { onRomulanActivated: console.log("Rom1 clicked") }
                // RomulanButton2 { onRomulanActivated: console.log("Rom2 clicked") }
                // RomulanButton3 { onRomulanActivated: console.log("Rom3 clicked") }
                // RomulanButton4 { onRomulanActivated: console.log("Rom4 clicked") }
                
                Rectangle { width: 120; height: 60; color: "#006666"; border.color: "#00FF99"; border.width: 2; radius: 5 }
                Rectangle { width: 120; height: 60; color: "#00FF99"; border.color: "#00FF99"; border.width: 2; radius: 5 }
                Rectangle { width: 120; height: 60; color: "#1C7736"; border.color: "#00FF99"; border.width: 2; radius: 5 }
                Rectangle { width: 120; height: 60; color: "#99CC99"; border.color: "#00FF99"; border.width: 2; radius: 5 }
            }
        }

        // Кардасіанські кнопки
        Column {
            anchors.left: parent.left
            anchors.top: parent.top
            anchors.topMargin: 320
            anchors.leftMargin: 20
            spacing: 10

            Text {
                text: "🔶 CARDASSIAN BUTTONS"
                color: "#FFD700"
                font.pixelSize: 16
                font.bold: true
            }

            Row {
                spacing: 10
                // CardassianButton1 { onCardassianActivated: console.log("Car1 clicked") }
                // CardassianButton2 { onCardassianActivated: console.log("Car2 clicked") }
                // CardassianButton3 { onCardassianActivated: console.log("Car3 clicked") }
                // CardassianButton4 { onCardassianActivated: console.log("Car4 clicked") }
                
                Rectangle { width: 100; height: 60; color: "#CC3300"; border.color: "#FFD700"; border.width: 2 }
                Rectangle { width: 100; height: 60; color: "#FF4400"; border.color: "#FFD700"; border.width: 2 }
                Rectangle { width: 100; height: 60; color: "#FF6600"; border.color: "#FFD700"; border.width: 2 }
                Rectangle { width: 100; height: 60; color: "#FF9900"; border.color: "#FFD700"; border.width: 2 }
            }
        }

        // Панелі
        Column {
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.topMargin: 80
            anchors.rightMargin: 20
            spacing: 15

            Text {
                text: "📋 SYSTEM PANELS"
                color: "#40E0D0"
                font.pixelSize: 16
                font.bold: true
            }

            // MainPanel { onPanelClicked: console.log("Main panel clicked") }
            Rectangle { width: 300; height: 100; color: "#1a1a1a"; border.color: "#40E0D0"; border.width: 2; radius: 5 }

            // TacticalPanel { onPanelClicked: console.log("Tactical panel clicked") }
            Rectangle { width: 250; height: 80; color: "#2d1b1b"; border.color: "#CC0000"; border.width: 2; radius: 5 }

            // EngineeringPanel { onPanelClicked: console.log("Engineering panel clicked") }
            Rectangle { width: 250; height: 80; color: "#1b2d1b"; border.color: "#00FF99"; border.width: 2; radius: 5 }
        }

        // Інструкція
        Text {
            text: "💡 Component Factory автоматично створив ці QML компоненти!
               \n🔧 Використання: import 'generated/Klingon24th.qml'
               \n📁 Всі файли в: lcars/qml/generated/"
            color: "#FFFFFF"
            font.pixelSize: 12
            anchors.bottom: parent.bottom
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.margins: 20
            horizontalAlignment: Text.AlignHCenter
        }
    }
}
