import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Shapes
import QtQuick.Layouts
import QtQuick.Particles
import QtQuick.Effects

ApplicationWindow {
    visible: true
    width: 1400
    height: 900
    color: "#000000"
    title: "IKV BORTAS - ADVANCED KLINGON INTERFACE"
    flags: Qt.FramelessWindowHint
    
    // Клінгонська палітра
    readonly property color k_red: "#660000"
    readonly property color k_dark: "#1A0000"
    readonly property color k_gold: "#FFD700"
    readonly property color k_bronze: "#CD7F32"
    readonly property color k_steel: "#434343"
    readonly property color k_blood: "#8B0000"
    
    // Анімації мерехтіння
    Timer {
        interval: 2000
        running: true
        repeat: true
        onTriggered: {
            flickerAnimation.start()
        }
    }
    
    SequentialAnimation {
        id: flickerAnimation
        PropertyAnimation { target: mainContainer; property: "opacity"; to: 0.95; duration: 100 }
        PropertyAnimation { target: mainContainer; property: "opacity"; to: 1.0; duration: 100 }
    }
    
    // Головний контейнер з градієнтом
    Rectangle {
        id: mainContainer
        anchors.fill: parent
        color: k_dark
        
        // Градієнтний фон
        gradient: Gradient {
            GradientStop { position: 0.0; color: "#0A0000" }
            GradientStop { position: 0.5; color: "#1A0000" }
            GradientStop { position: 1.0; color: "#0A0000" }
        }
        
        // Енергетичні ефекти - анімовані точки
        Repeater {
            model: 20
            Rectangle {
                width: 3
                height: 3
                radius: 1.5
                color: k_gold
                opacity: 0.6
                
                x: Math.random() * parent.width
                y: Math.random() * parent.height
                
                SequentialAnimation {
                    running: true
                    loops: Animation.Infinite
                    
                    PropertyAnimation {
                        target: parent
                        property: "opacity"
                        to: 0.2
                        duration: 1000 + Math.random() * 2000
                    }
                    
                    PropertyAnimation {
                        target: parent
                        property: "opacity"
                        to: 0.8
                        duration: 1000 + Math.random() * 2000
                    }
                }
                
                NumberAnimation on x {
                    from: Math.random() * parent.width
                    to: Math.random() * parent.width
                    duration: 5000 + Math.random() * 5000
                    loops: Animation.Infinite
                }
                
                NumberAnimation on y {
                    from: Math.random() * parent.height
                    to: Math.random() * parent.height
                    duration: 5000 + Math.random() * 5000
                    loops: Animation.Infinite
                }
            }
        }
        
        // Верхній хедер з анімацією
        Rectangle {
            id: header
            width: parent.width
            height: 100
            color: k_red
            anchors.top: parent.top
            
            // Анімований клінгонський символ
            Shape {
                width: 80
                height: 80
                anchors.left: parent.left
                anchors.verticalCenter: parent.verticalCenter
                anchors.leftMargin: 30
                
                ShapePath {
                    id: klingonSymbol
                    fillColor: k_gold
                    strokeColor: k_bronze
                    strokeWidth: 3
                    
                    PathSvg {
                        path: "M 40,10 L 65,30 L 60,55 L 40,75 L 20,55 L 15,30 Z"
                    }
                }
                
                SequentialAnimation {
                    running: true
                    loops: Animation.Infinite
                    PropertyAnimation {
                        target: klingonSymbol
                        property: "fillColor"
                        to: k_bronze
                        duration: 1000
                    }
                    PropertyAnimation {
                        target: klingonSymbol
                        property: "fillColor"
                        to: k_gold
                        duration: 1000
                    }
                }
            }
            
            // Анімований заголовок
            Text {
                text: "KLINGON HIGH COMMAND"
                anchors.left: parent.left
                anchors.verticalCenter: parent.verticalCenter
                anchors.leftMargin: 140
                color: k_gold
                font.bold: true
                font.pixelSize: 32
                font.family: "Arial Black"
                
                SequentialAnimation {
                    running: true
                    loops: Animation.Infinite
                    PropertyAnimation {
                        target: parent
                        property: "color"
                        to: k_bronze
                        duration: 1500
                    }
                    PropertyAnimation {
                        target: parent
                        property: "color"
                        to: k_gold
                        duration: 1500
                    }
                }
            }
            
            // Статус корабля з анімацією
            Column {
                anchors.right: parent.right
                anchors.verticalCenter: parent.verticalCenter
                anchors.rightMargin: 30
                spacing: 5
                
                Text {
                    text: "IKV BORTAS"
                    color: k_gold
                    font.bold: true
                    font.pixelSize: 24
                }
                
                Text {
                    text: "BATTLE CRUISER"
                    color: k_bronze
                    font.pixelSize: 16
                }
                
                Rectangle {
                    width: 200
                    height: 8
                    color: k_dark
                    border.color: k_gold
                    border.width: 1
                    
                    Rectangle {
                        width: parent.width * 0.8
                        height: parent.height
                        color: k_gold
                        
                        SequentialAnimation {
                            running: true
                            loops: Animation.Infinite
                            PropertyAnimation {
                                target: parent
                                property: "width"
                                to: parent.parent.width * 0.6
                                duration: 2000
                            }
                            PropertyAnimation {
                                target: parent
                                property: "width"
                                to: parent.parent.width * 0.9
                                duration: 2000
                            }
                        }
                    }
                }
            }
        }
        
        // Основна область з трьома колонками
        RowLayout {
            anchors.fill: parent
            anchors.topMargin: 100
            anchors.bottomMargin: 80
            spacing: 5
            
            // Ліва панель - Зброя
            Rectangle {
                Layout.preferredWidth: 300
                Layout.fillHeight: true
                color: Qt.rgba(k_red.r, k_red.g, k_red.b, 0.3)
                border.color: k_gold
                border.width: 2
                radius: 10
                
                Column {
                    anchors.fill: parent
                    anchors.margins: 15
                    spacing: 20
                    
                    Text {
                        text: "⚔️ WEAPONS SYSTEMS"
                        color: k_gold
                        font.bold: true
                        font.pixelSize: 20
                        anchors.horizontalCenter: parent.horizontalCenter
                    }
                    
                    // Фазери з анімацією
                    Rectangle {
                        width: parent.width
                        height: 80
                        color: k_dark
                        border.color: k_gold
                        border.width: 2
                        radius: 5
                        
                        Column {
                            anchors.centerIn: parent
                            spacing: 10
                            
                            Text {
                                text: "PHASER BANKS"
                                color: k_gold
                                font.bold: true
                                font.pixelSize: 16
                            }
                            
                            Rectangle {
                                width: 200
                                height: 20
                                color: k_dark
                                border.color: k_gold
                                border.width: 1
                                
                                Rectangle {
                                    id: phaserBar
                                    width: parent.width * 0.7
                                    height: parent.height
                                    color: k_gold
                                    
                                    SequentialAnimation {
                                        running: true
                                        loops: Animation.Infinite
                                        PropertyAnimation {
                                            target: phaserBar
                                            property: "width"
                                            to: parent.width * 0.9
                                            duration: 1500
                                        }
                                        PropertyAnimation {
                                            target: phaserBar
                                            property: "width"
                                            to: parent.width * 0.5
                                            duration: 1500
                                        }
                                    }
                                }
                            }
                        }
                        
                        MouseArea {
                            anchors.fill: parent
                            onClicked: {
                                console.log("🔫 PHASERS FIRING!")
                                phaserFireAnimation.start()
                            }
                        }
                        
                        SequentialAnimation {
                            id: phaserFireAnimation
                            PropertyAnimation {
                                target: parent
                                property: "color"
                                to: k_blood
                                duration: 100
                            }
                            PropertyAnimation {
                                target: parent
                                property: "color"
                                to: k_dark
                                duration: 100
                            }
                        }
                    }
                    
                    // Торпеди
                    Rectangle {
                        width: parent.width
                        height: 80
                        color: k_dark
                        border.color: k_gold
                        border.width: 2
                        radius: 5
                        
                        Column {
                            anchors.centerIn: parent
                            spacing: 10
                            
                            Text {
                                text: "PHOTON TORPEDOES"
                                color: k_gold
                                font.bold: true
                                font.pixelSize: 16
                            }
                            
                            Row {
                                anchors.horizontalCenter: parent.horizontalCenter
                                spacing: 5
                                
                                Repeater {
                                    model: 6
                                    Rectangle {
                                        width: 20
                                        height: 20
                                        radius: 10
                                        color: index < 4 ? k_gold : k_steel
                                        border.color: k_bronze
                                        border.width: 1
                                    }
                                }
                            }
                        }
                        
                        MouseArea {
                            anchors.fill: parent
                            onClicked: {
                                console.log("🚀 TORPEDOES LAUNCHED!")
                                torpedoFireAnimation.start()
                            }
                        }
                        
                        SequentialAnimation {
                            id: torpedoFireAnimation
                            PropertyAnimation {
                                target: parent
                                property: "color"
                                to: k_blood
                                duration: 200
                            }
                            PropertyAnimation {
                                target: parent
                                property: "color"
                                to: k_dark
                                duration: 200
                            }
                        }
                    }
                    
                    // Дисраптор
                    Rectangle {
                        width: parent.width
                        height: 80
                        color: k_dark
                        border.color: k_gold
                        border.width: 2
                        radius: 5
                        
                        Text {
                            text: "DISRUPTOR CANNON"
                            color: k_gold
                            font.bold: true
                            font.pixelSize: 16
                            anchors.centerIn: parent
                        }
                        
                        MouseArea {
                            anchors.fill: parent
                            onClicked: {
                                console.log("⚡ DISRUPTOR CHARGING!")
                            }
                        }
                    }
                }
            }
            
            // Центральна панель - Тактика
            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                color: Qt.rgba(k_dark.r, k_dark.g, k_dark.b, 0.5)
                border.color: k_gold
                border.width: 2
                radius: 10
                
                Column {
                    anchors.fill: parent
                    anchors.margins: 20
                    spacing: 20
                    
                    Text {
                        text: "🎯 TACTICAL DISPLAY"
                        color: k_gold
                        font.bold: true
                        font.pixelSize: 24
                        anchors.horizontalCenter: parent.horizontalCenter
                    }
                    
                    // Радарний дисплей
                    Rectangle {
                        width: 400
                        height: 400
                        color: k_dark
                        border.color: k_gold
                        border.width: 3
                        radius: 200
                        anchors.horizontalCenter: parent.horizontalCenter
                        
                        // Концентричні кола
                        Repeater {
                            model: 4
                            Rectangle {
                                width: 400 - index * 80
                                height: 400 - index * 80
                                color: "transparent"
                                border.color: k_gold
                                border.width: 1
                                radius: (400 - index * 80) / 2
                                anchors.centerIn: parent
                            }
                        }
                        
                        // Лінії перехрестя
                        Rectangle {
                            width: 400
                            height: 1
                            color: k_gold
                            anchors.centerIn: parent
                        }
                        
                        Rectangle {
                            width: 1
                            height: 400
                            color: k_gold
                            anchors.centerIn: parent
                        }
                        
                        // Анімовані цілі
                        Repeater {
                            model: 3
                            Rectangle {
                                width: 15
                                height: 15
                                radius: 7.5
                                color: k_blood
                                border.color: k_gold
                                border.width: 2
                                
                                SequentialAnimation {
                                    running: true
                                    loops: Animation.Infinite
                                    PropertyAnimation {
                                        target: parent
                                        property: "color"
                                        to: k_gold
                                        duration: 500
                                    }
                                    PropertyAnimation {
                                        target: parent
                                        property: "color"
                                        to: k_blood
                                        duration: 500
                                    }
                                }
                                
                                // Рухомі цілі
                                NumberAnimation on x {
                                    from: 100
                                    to: 300
                                    duration: 3000 + index * 1000
                                    loops: Animation.Infinite
                                }
                                
                                NumberAnimation on y {
                                    from: 100 + index * 50
                                    to: 300 - index * 50
                                    duration: 2500 + index * 800
                                    loops: Animation.Infinite
                                }
                            }
                        }
                    }
                    
                    // Інформаційна панель
                    Rectangle {
                        width: parent.width
                        height: 100
                        color: Qt.rgba(k_red.r, k_red.g, k_red.b, 0.3)
                        border.color: k_gold
                        border.width: 2
                        radius: 5
                        
                        GridLayout {
                            anchors.fill: parent
                            anchors.margins: 10
                            columns: 3
                            columnSpacing: 20
                            rowSpacing: 10
                            
                            Text {
                                text: "ENEMY SHIPS:"
                                color: k_gold
                                font.bold: true
                                font.pixelSize: 14
                            }
                            
                            Text {
                                text: "3"
                                color: k_blood
                                font.bold: true
                                font.pixelSize: 14
                            }
                            
                            Text {
                                text: "HOSTILE"
                                color: k_blood
                                font.pixelSize: 12
                            }
                            
                            Text {
                                text: "DISTANCE:"
                                color: k_gold
                                font.bold: true
                                font.pixelSize: 14
                            }
                            
                            Text {
                                text: "45,000 KM"
                                color: k_bronze
                                font.pixelSize: 14
                            }
                            
                            Text {
                                text: "CLOSING"
                                color: k_blood
                                font.pixelSize: 12
                            }
                            
                            Text {
                                text: "THREAT LEVEL:"
                                color: k_gold
                                font.bold: true
                                font.pixelSize: 14
                            }
                            
                            Text {
                                text: "CRITICAL"
                                color: k_blood
                                font.bold: true
                                font.pixelSize: 14
                            }
                            
                            Text {
                                text: "⚠️ ALERT"
                                color: k_blood
                                font.pixelSize: 12
                            }
                        }
                    }
                }
            }
            
            // Права панель - Системи
            Rectangle {
                Layout.preferredWidth: 300
                Layout.fillHeight: true
                color: Qt.rgba(k_red.r, k_red.g, k_red.b, 0.3)
                border.color: k_gold
                border.width: 2
                radius: 10
                
                Column {
                    anchors.fill: parent
                    anchors.margins: 15
                    spacing: 20
                    
                    Text {
                        text: "🛡️ SHIP SYSTEMS"
                        color: k_gold
                        font.bold: true
                        font.pixelSize: 20
                        anchors.horizontalCenter: parent.horizontalCenter
                    }
                    
                    // Щити
                    Rectangle {
                        width: parent.width
                        height: 60
                        color: k_dark
                        border.color: k_gold
                        border.width: 2
                        radius: 5
                        
                        Column {
                            anchors.centerIn: parent
                            spacing: 5
                            
                            Text {
                                text: "SHIELDS"
                                color: k_gold
                                font.bold: true
                                font.pixelSize: 14
                            }
                            
                            Rectangle {
                                width: 200
                                height: 15
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
                    }
                    
                    // Двигуни
                    Rectangle {
                        width: parent.width
                        height: 60
                        color: k_dark
                        border.color: k_gold
                        border.width: 2
                        radius: 5
                        
                        Column {
                            anchors.centerIn: parent
                            spacing: 5
                            
                            Text {
                                text: "WARP ENGINES"
                                color: k_gold
                                font.bold: true
                                font.pixelSize: 14
                            }
                            
                            Rectangle {
                                width: 200
                                height: 15
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
                    }
                    
                    // Маскуючий пристрій
                    Rectangle {
                        width: parent.width
                        height: 80
                        color: k_dark
                        border.color: k_gold
                        border.width: 2
                        radius: 5
                        
                        Column {
                            anchors.centerIn: parent
                            spacing: 10
                            
                            Text {
                                text: "CLOAKING DEVICE"
                                color: k_gold
                                font.bold: true
                                font.pixelSize: 14
                            }
                            
                            Rectangle {
                                width: 120
                                height: 30
                                color: k_steel
                                border.color: k_gold
                                border.width: 2
                                radius: 5
                                
                                Text {
                                    text: "ENGAGE"
                                    color: k_gold
                                    font.bold: true
                                    font.pixelSize: 12
                                    anchors.centerIn: parent
                                }
                                
                                MouseArea {
                                    anchors.fill: parent
                                    onClicked: {
                                        console.log("👻 CLOAKING DEVICE ENGAGED!")
                                        parent.color = k_gold
                                        parent.children[0].color = k_dark
                                    }
                                }
                            }
                        }
                    }
                    
                    // Комунікації
                    Rectangle {
                        width: parent.width
                        height: 60
                        color: k_dark
                        border.color: k_gold
                        border.width: 2
                        radius: 5
                        
                        Text {
                            text: "SUBSPACE COMM"
                            color: k_gold
                            font.bold: true
                            font.pixelSize: 14
                            anchors.centerIn: parent
                        }
                    }
                }
            }
        }
        
        // Нижня панель управління
        Rectangle {
            width: parent.width
            height: 80
            color: k_red
            anchors.bottom: parent.bottom
            border.color: k_gold
            border.width: 2
            
            Row {
                anchors.centerIn: parent
                spacing: 30
                
                Repeater {
                    model: ["RED ALERT", "POWER", "COMMS", "CLOAK", "EXIT"]
                    
                    Rectangle {
                        width: 120
                        height: 40
                        color: k_dark
                        border.color: k_gold
                        border.width: 2
                        radius: 5
                        
                        Text {
                            text: modelData
                            color: k_gold
                            font.bold: true
                            font.pixelSize: 12
                            anchors.centerIn: parent
                        }
                        
                        MouseArea {
                            anchors.fill: parent
                            hoverEnabled: true
                            
                            onEntered: {
                                parent.color = k_gold
                                parent.children[0].color = k_dark
                            }
                            
                            onExited: {
                                parent.color = k_dark
                                parent.children[0].color = k_gold
                            }
                            
                            onClicked: {
                                if (modelData === "EXIT") {
                                    Qt.quit()
                                } else {
                                    console.log(`${modelData} ACTIVATED!`)
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
