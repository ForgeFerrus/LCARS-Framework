import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Shapes

ApplicationWindow {
    visible: true
    width: 1280
    height: 720
    color: "#000000"
    title: "KLINGON EMPIRE - AUTHENTIC INTERFACE"
    flags: Qt.FramelessWindowHint
    
    // Клінгонська палітра
    readonly property color k_red: "#8B0000"
    readonly property color k_dark: "#1A0000"
    readonly property color k_gold: "#B8860B"
    readonly property color k_bronze: "#CD7F32"
    readonly property color k_steel: "#434343"
    readonly property color k_blood: "#660000"
    
    Rectangle {
        id: mainContainer
        anchors.fill: parent
        color: k_dark
        
        // Клінгонський символ зверху
        Shape {
            id: klingonEmblem
            width: 120
            height: 120
            anchors.top: parent.top
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.topMargin: 20
            
            ShapePath {
                fillColor: k_gold
                strokeColor: k_bronze
                strokeWidth: 4
                
                // Справжній клінгонський символ
                PathSvg {
                    path: "M 60,20 L 80,40 L 75,60 L 60,80 L 45,60 L 40,40 Z
                           M 60,35 L 70,45 L 67,55 L 60,65 L 53,55 L 50,45 Z
                           M 60,45 L 65,50 L 63,55 L 60,60 L 57,55 L 55,50 Z"
                }
            }
        }
        
        // Клінгонський текст - tlhIngan Hol
        Text {
            id: klingonTitle
            text: "tlhIngan wo'"
            anchors.top: klingonEmblem.bottom
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.topMargin: 10
            color: k_gold
            font.bold: true
            font.pixelSize: 32
            font.family: "Arial"
        }
        
        Text {
            text: "Klingon Empire"
            anchors.top: klingonTitle.bottom
            anchors.horizontalCenter: parent.horizontalCenter
            color: k_bronze
            font.pixelSize: 18
        }
        
        // Основна панель управління
        Rectangle {
            id: controlPanel
            width: parent.width - 100
            height: 400
            anchors.centerIn: parent
            color: Qt.rgba(k_red.r, k_red.g, k_red.b, 0.2)
            border.color: k_gold
            border.width: 3
            radius: 15
            
            // Клінгонські кнопки у формі трикутників
            Row {
                anchors.centerIn: parent
                spacing: 40
                
                // Бойова станція
                Column {
                    spacing: 20
                    
                    Shape {
                        width: 100
                        height: 80
                        ShapePath {
                            fillColor: k_blood
                            strokeColor: k_gold
                            strokeWidth: 2
                            
                            PathSvg {
                                path: "M 50,10 L 90,70 L 10,70 Z"
                            }
                        }
                        
                        Text {
                            text: "batlh"
                            anchors.centerIn: parent
                            color: k_gold
                            font.bold: true
                            font.pixelSize: 14
                        }
                        
                        MouseArea {
                            anchors.fill: parent
                            onClicked: {
                                console.log("Honor station activated!")
                                parent.parent.children[1].color = k_gold
                            }
                        }
                    }
                    
                    Shape {
                        width: 100
                        height: 80
                        ShapePath {
                            fillColor: k_blood
                            strokeColor: k_gold
                            strokeWidth: 2
                            
                            PathSvg {
                                path: "M 50,10 L 90,70 L 10,70 Z"
                            }
                        }
                        
                        Text {
                            text: "may'"
                            anchors.centerIn: parent
                            color: k_gold
                            font.bold: true
                            font.pixelSize: 14
                        }
                    }
                }
                
                // Сенсорна станція
                Column {
                    spacing: 20
                    
                    Shape {
                        width: 100
                        height: 80
                        ShapePath {
                            fillColor: k_blood
                            strokeColor: k_gold
                            strokeWidth: 2
                            
                            PathSvg {
                                path: "M 50,10 L 90,70 L 10,70 Z"
                            }
                        }
                        
                        Text {
                            text: "ghu"
                            anchors.centerIn: parent
                            color: k_gold
                            font.bold: true
                            font.pixelSize: 14
                        }
                    }
                    
                    Shape {
                        width: 100
                        height: 80
                        ShapePath {
                            fillColor: k_blood
                            strokeColor: k_gold
                            strokeWidth: 2
                            
                            PathSvg {
                                path: "M 50,10 L 90,70 L 10,70 Z"
                            }
                        }
                        
                        Text {
                            text: "Duj"
                            anchors.centerIn: parent
                            color: k_gold
                            font.bold: true
                            font.pixelSize: 14
                        }
                    }
                }
                
                // Комунікаційна станція
                Column {
                    spacing: 20
                    
                    Shape {
                        width: 100
                        height: 80
                        ShapePath {
                            fillColor: k_blood
                            strokeColor: k_gold
                            strokeWidth: 2
                            
                            PathSvg {
                                path: "M 50,10 L 90,70 L 10,70 Z"
                            }
                        }
                        
                        Text {
                            text: "Qum"
                            anchors.centerIn: parent
                            color: k_gold
                            font.bold: true
                            font.pixelSize: 14
                        }
                    }
                    
                    Shape {
                        width: 100
                        height: 80
                        ShapePath {
                            fillColor: k_blood
                            strokeColor: k_gold
                            strokeWidth: 2
                            
                            PathSvg {
                                path: "M 50,10 L 90,70 L 10,70 Z"
                            }
                        }
                        
                        Text {
                            text: "mang"
                            anchors.centerIn: parent
                            color: k_gold
                            font.bold: true
                            font.pixelSize: 14
                        }
                    }
                }
                
                // Інженерна станція
                Column {
                    spacing: 20
                    
                    Shape {
                        width: 100
                        height: 80
                        ShapePath {
                            fillColor: k_blood
                            strokeColor: k_gold
                            strokeWidth: 2
                            
                            PathSvg {
                                path: "M 50,10 L 90,70 L 10,70 Z"
                            }
                        }
                        
                        Text {
                            text: "cha'"
                            anchors.centerIn: parent
                            color: k_gold
                            font.bold: true
                            font.pixelSize: 14
                        }
                    }
                    
                    Shape {
                        width: 100
                        height: 80
                        ShapePath {
                            fillColor: k_blood
                            strokeColor: k_gold
                            strokeWidth: 2
                            
                            PathSvg {
                                path: "M 50,10 L 90,70 L 10,70 Z"
                            }
                        }
                        
                        Text {
                            text: "HoS"
                            anchors.centerIn: parent
                            color: k_gold
                            font.bold: true
                            font.pixelSize: 14
                        }
                    }
                }
            }
        }
        
        // Клінгонський статусний дисплей
        Rectangle {
            id: statusDisplay
            width: parent.width - 200
            height: 80
            anchors.bottom: parent.bottom
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.bottomMargin: 50
            color: Qt.rgba(k_dark.r, k_dark.g, k_dark.b, 0.8)
            border.color: k_gold
            border.width: 2
            
            Row {
                anchors.centerIn: parent
                spacing: 30
                
                Column {
                    Text {
                        text: "SHIP STATUS"
                        color: k_gold
                        font.bold: true
                        font.pixelSize: 12
                    }
                    Text {
                        text: "IKV Bortas"
                        color: k_bronze
                        font.pixelSize: 10
                    }
                }
                
                Column {
                    Text {
                        text: "SHIELDS"
                        color: k_gold
                        font.bold: true
                        font.pixelSize: 12
                    }
                    Rectangle {
                        width: 80
                        height: 10
                        color: k_dark
                        border.color: k_gold
                        border.width: 1
                        
                        Rectangle {
                            width: parent.width * 0.8
                            height: parent.height
                            color: k_gold
                        }
                    }
                }
                
                Column {
                    Text {
                        text: "WEAPONS"
                        color: k_gold
                        font.bold: true
                        font.pixelSize: 12
                    }
                    Rectangle {
                        width: 80
                        height: 10
                        color: k_dark
                        border.color: k_gold
                        border.width: 1
                        
                        Rectangle {
                            width: parent.width * 0.9
                            height: parent.height
                            color: k_gold
                        }
                    }
                }
                
                Column {
                    Text {
                        text: "POWER"
                        color: k_gold
                        font.bold: true
                        font.pixelSize: 12
                    }
                    Rectangle {
                        width: 80
                        height: 10
                        color: k_dark
                        border.color: k_gold
                        border.width: 1
                        
                        Rectangle {
                            width: parent.width * 0.7
                            height: parent.height
                            color: k_gold
                        }
                    }
                }
            }
        }
        
        // Кнопка виходу
        Rectangle {
            width: 100
            height: 30
            anchors.bottom: parent.bottom
            anchors.right: parent.right
            anchors.margins: 20
            color: k_blood
            border.color: k_gold
            border.width: 2
            
            Text {
                text: "majQa'"
                anchors.centerIn: parent
                color: k_gold
                font.bold: true
                font.pixelSize: 12
            }
            
            MouseArea {
                anchors.fill: parent
                onClicked: Qt.quit()
            }
        }
    }
}
