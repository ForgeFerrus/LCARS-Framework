import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Qt5Compat.GraphicalEffects

ApplicationWindow {
    visible: true
    width: 1200
    height: 800
    color: "black"
    title: "🚀 LCARS System - Generated Components"

    // Імпортуємо згенеровані компоненти
    // В реальному додатку вони будуть в папці lcars/qml/generated/

    Rectangle {
        anchors.fill: parent
        color: "#000000"

        // Головна панель заголовка
        Rectangle {
            id: headerPanel
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.right: parent.right
            height: 80
            color: "#1a1a1a"
            border.color: "#40E0D0"
            border.width: 2

            Text {
                text: "🚀 LCARS BATTLE CRUISER INTERFACE"
                color: "#40E0D0"
                font.pixelSize: 24
                font.bold: true
                anchors.centerIn: parent
            }

            // Статусні індикатори
            Row {
                anchors.right: parent.right
                anchors.verticalCenter: parent.verticalCenter
                anchors.rightMargin: 20
                spacing: 10

                Rectangle { width: 15; height: 15; radius: 7.5; color: "#00FF00" }
                Rectangle { width: 15; height: 15; radius: 7.5; color: "#00FF00" }
                Rectangle { width: 15; height: 15; radius: 7.5; color: "#FFFF00" }
                Rectangle { width: 15; height: 15; radius: 7.5; color: "#FF0000" }
            }
        }

        // Ліва панель - Клінгонські системи
        Rectangle {
            id: klingonPanel
            anchors.left: parent.left
            anchors.top: headerPanel.bottom
            anchors.bottom: parent.bottom
            width: 300
            color: "#1a0a0a"
            border.color: "#660000"
            border.width: 2

            Column {
                anchors.fill: parent
                anchors.margins: 10
                spacing: 10

                Text {
                    text: "🔺 KLINGON SYSTEMS"
                    color: "#FFD700"
                    font.pixelSize: 18
                    font.bold: true
                }

                // Клінгонські кнопки (згенеровані)
                Row {
                    spacing: 5
                    // Klingon22nd { onKlingonClicked: console.log("22nd system") }
                    Rectangle { width: 70; height: 45; color: "#400000"; border.color: "#FFD700"; border.width: 1 }
                    Rectangle { width: 70; height: 45; color: "#CC0000"; border.color: "#FFD700"; border.width: 1 }
                    Rectangle { width: 70; height: 45; color: "#660000"; border.color: "#FFD700"; border.width: 1 }
                    Rectangle { width: 70; height: 45; color: "#A61A35"; border.color: "#FFD700"; border.width: 1 }
                }

                // Тактичні кнопки
                Text {
                    text: "TACTICAL SYSTEMS"
                    color: "#FF6600"
                    font.pixelSize: 14
                    font.bold: true
                }

                Grid {
                    columns: 3
                    spacing: 5
                    
                    Rectangle { width: 60; height: 35; color: "#980000"; border.color: "#FFD700"; border.width: 1 }
                    Rectangle { width: 60; height: 35; color: "#CA0000"; border.color: "#FFD700"; border.width: 1 }
                    Rectangle { width: 60; height: 35; color: "#D73713"; border.color: "#FFD700"; border.width: 1 }
                    Rectangle { width: 60; height: 35; color: "#E7730E"; border.color: "#FFD700"; border.width: 1 }
                    Rectangle { width: 60; height: 35; color: "#FFCB66"; border.color: "#FFD700"; border.width: 1 }
                    Rectangle { width: 60; height: 35; color: "#F6EE24"; border.color: "#FFD700"; border.width: 1 }
                }

                // Системний статус
                Rectangle {
                    width: parent.width
                    height: 100
                    color: "#2a1a1a"
                    border.color: "#40E0D0"
                    border.width: 1
                    radius: 5

                    Column {
                        anchors.fill: parent
                        anchors.margins: 10
                        spacing: 5

                        Text {
                            text: "SYSTEM STATUS"
                            color: "#40E0D0"
                            font.pixelSize: 12
                            font.bold: true
                        }

                        Rectangle { width: parent.width; height: 3; color: "#00FF00" }
                        Rectangle { width: parent.width * 0.8; height: 3; color: "#FFFF00" }
                        Rectangle { width: parent.width * 0.6; height: 3; color: "#FF6600" }
                        Rectangle { width: parent.width * 0.9; height: 3; color: "#00FF00" }
                    }
                }
            }
        }

        // Центральна область - Головний дисплей
        Rectangle {
            id: mainDisplay
            anchors.left: klingonPanel.right
            anchors.top: headerPanel.bottom
            anchors.right: romulanPanel.left
            anchors.bottom: bottomPanel.top
            anchors.margins: 10
            color: "#0a1a1a"
            border.color: "#40E0D0"
            border.width: 2
            radius: 10

            Column {
                anchors.fill: parent
                anchors.margins: 20
                spacing: 15

                Text {
                    text: "MAIN DISPLAY - TACTICAL VIEW"
                    color: "#40E0D0"
                    font.pixelSize: 20
                    font.bold: true
                    anchors.horizontalCenter: parent.horizontalCenter
                }

                // Візуальний дисплей
                Rectangle {
                    width: parent.width
                    height: 200
                    color: "#001122"
                    border.color: "#00FF99"
                    border.width: 2
                    radius: 5

                    // Імітація радарного дисплея
                    Rectangle {
                        anchors.centerIn: parent
                        width: 150
                        height: 150
                        radius: 75
                        color: "transparent"
                        border.color: "#00FF99"
                        border.width: 2

                        // Концентричні кола
                        Rectangle {
                            anchors.centerIn: parent
                            width: 100; height: 100
                            radius: 50
                            color: "transparent"
                            border.color: "#00FF99"
                            border.width: 1
                        }

                        Rectangle {
                            anchors.centerIn: parent
                            width: 50; height: 50
                            radius: 25
                            color: "transparent"
                            border.color: "#00FF99"
                            border.width: 1
                        }

                        // Цільові маркери
                        Rectangle {
                            x: 60; y: 30
                            width: 8; height: 8
                            radius: 4
                            color: "#FF0000"
                        }

                        Rectangle {
                            x: 20; y: 80
                            width: 8; height: 8
                            radius: 4
                            color: "#FFFF00"
                        }

                        Rectangle {
                            x: 100; y: 100
                            width: 8; height: 8
                            radius: 4
                            color: "#00FF00"
                        }
                    }
                }

                // Панель інформації
                Rectangle {
                    width: parent.width
                    height: 120
                    color: "#1a1a1a"
                    border.color: "#FFD700"
                    border.width: 1
                    radius: 5

                    Grid {
                        anchors.fill: parent
                        anchors.margins: 15
                        columns: 2
                        spacing: 10

                        Column {
                            Text { text: "SHIELDS"; color: "#40E0D0"; font.bold: true }
                            Text { text: "100%"; color: "#00FF00"; font.pixelSize: 16 }
                            Rectangle { width: 100; height: 5; color: "#00FF00" }
                        }

                        Column {
                            Text { text: "WEAPONS"; color: "#40E0D0"; font.bold: true }
                            Text { text: "READY"; color: "#00FF00"; font.pixelSize: 16 }
                            Rectangle { width: 100; height: 5; color: "#00FF00" }
                        }

                        Column {
                            Text { text: "ENGINES"; color: "#40E0D0"; font.bold: true }
                            Text { text: "95%"; color: "#FFFF00"; font.pixelSize: 16 }
                            Rectangle { width: 95; height: 5; color: "#FFFF00" }
                        }

                        Column {
                            Text { text: "HULL"; color: "#40E0D0"; font.bold: true }
                            Text { text: "87%"; color: "#FFFF00"; font.pixelSize: 16 }
                            Rectangle { width: 87; height: 5; color: "#FFFF00" }
                        }
                    }
                }
            }
        }

        // Права панель - Ромуланські системи
        Rectangle {
            id: romulanPanel
            anchors.right: parent.right
            anchors.top: headerPanel.bottom
            anchors.bottom: parent.bottom
            width: 250
            color: "#0a1a1a"
            border.color: "#00FF99"
            border.width: 2

            Column {
                anchors.fill: parent
                anchors.margins: 10
                spacing: 10

                Text {
                    text: "🔻 ROMULAN SYSTEMS"
                    color: "#00FF99"
                    font.pixelSize: 16
                    font.bold: true
                }

                // Ромуланські кнопки (згенеровані)
                Column {
                    spacing: 5
                    
                    Rectangle { width: parent.width; height: 30; color: "#006666"; border.color: "#00FF99"; border.width: 1; radius: 3 }
                    Rectangle { width: parent.width; height: 30; color: "#00FF99"; border.color: "#00FF99"; border.width: 1; radius: 3 }
                    Rectangle { width: parent.width; height: 30; color: "#1C7736"; border.color: "#00FF99"; border.width: 1; radius: 3 }
                    Rectangle { width: parent.width; height: 30; color: "#99CC99"; border.color: "#00FF99"; border.width: 1; radius: 3 }
                }

                // Кардасіанські системи
                Text {
                    text: "🔶 CARDASSIAN SYSTEMS"
                    color: "#FFD700"
                    font.pixelSize: 16
                    font.bold: true
                }

                Column {
                    spacing: 5
                    
                    Rectangle { width: parent.width; height: 30; color: "#CC3300"; border.color: "#FFD700"; border.width: 1 }
                    Rectangle { width: parent.width; height: 30; color: "#FF4400"; border.color: "#FFD700"; border.width: 1 }
                    Rectangle { width: parent.width; height: 30; color: "#FF6600"; border.color: "#FFD700"; border.width: 1 }
                    Rectangle { width: parent.width; height: 30; color: "#FF9900"; border.color: "#FFD700"; border.width: 1 }
                }

                // Комунікаційна панель
                Rectangle {
                    width: parent.width
                    height: 80
                    color: "#1a1a1a"
                    border.color: "#40E0D0"
                    border.width: 1
                    radius: 5

                    Column {
                        anchors.fill: parent
                        anchors.margins: 10
                        spacing: 5

                        Text {
                            text: "COMMUNICATIONS"
                            color: "#40E0D0"
                            font.pixelSize: 12
                            font.bold: true
                        }

                        Rectangle { width: parent.width; height: 2; color: "#00FF00" }
                        Text { text: "CHANNEL OPEN"; color: "#00FF00"; font.pixelSize: 10 }
                        Text { text: "FREQUENCY: 247.3"; color: "#40E0D0"; font.pixelSize: 10 }
                    }
                }
            }
        }

        // Нижня панель - Кардасіанські системи
        Rectangle {
            id: bottomPanel
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            height: 120
            color: "#1a1a1a"
            border.color: "#FFD700"
            border.width: 2

            Row {
                anchors.fill: parent
                anchors.margins: 15
                spacing: 20

                // Лівий блок - статус
                Column {
                    width: 200
                    spacing: 5

                    Text {
                        text: "SYSTEM STATUS"
                        color: "#FFD700"
                        font.pixelSize: 14
                        font.bold: true
                    }

                    Row {
                        spacing: 10
                        Rectangle { width: 12; height: 12; radius: 6; color: "#00FF00" }
                        Text { text: "ONLINE"; color: "#00FF00"; font.pixelSize: 10 }
                    }

                    Row {
                        spacing: 10
                        Rectangle { width: 12; height: 12; radius: 6; color: "#FFFF00" }
                        Text { text: "WARNING"; color: "#FFFF00"; font.pixelSize: 10 }
                    }

                    Row {
                        spacing: 10
                        Rectangle { width: 12; height: 12; radius: 6; color: "#FF0000" }
                        Text { text: "CRITICAL"; color: "#FF0000"; font.pixelSize: 10 }
                    }
                }

                // Центральний блок - панелі (згенеровані)
                Column {
                    width: 400
                    spacing: 5

                    Text {
                        text: "MAIN CONTROL PANELS"
                        color: "#40E0D0"
                        font.pixelSize: 14
                        font.bold: true
                        anchors.horizontalCenter: parent.horizontalCenter
                    }

                    Row {
                        anchors.horizontalCenter: parent.horizontalCenter
                        spacing: 10
                        
                        Rectangle { width: 80; height: 40; color: "#1a1a1a"; border.color: "#40E0D0"; border.width: 2; radius: 5 }
                        Rectangle { width: 80; height: 40; color: "#2d1b1b"; border.color: "#CC0000"; border.width: 2; radius: 5 }
                        Rectangle { width: 80; height: 40; color: "#1b2d1b"; border.color: "#00FF99"; border.width: 2; radius: 5 }
                        Rectangle { width: 80; height: 40; color: "#2d2d1b"; border.color: "#FFD700"; border.width: 2; radius: 5 }
                    }
                }

                // Правий блок - час
                Column {
                    width: 150
                    spacing: 5

                    Text {
                        text: "STARDATE"
                        color: "#FFD700"
                        font.pixelSize: 14
                        font.bold: true
                    }

                    Text {
                        text: "58432.7"
                        color: "#40E0D0"
                        font.pixelSize: 16
                        font.bold: true
                    }

                    Text {
                        text: "TIME: 23:47:12"
                        color: "#00FF99"
                        font.pixelSize: 12
                    }
                }
            }
        }
    }
}
