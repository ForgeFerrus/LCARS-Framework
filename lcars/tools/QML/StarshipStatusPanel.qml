import QtQuick
import QtQuick.Controls
import QtQuick.Effects

Rectangle {
    id: root
    width: 400
    height: 200
    color: "#000000"
    border.color: "#ff9c00"
    border.width: 2
    radius: 10
    
    // LCARS кольори
    readonly property color lcars_orange: "#ff9c00"
    readonly property color lcars_purple: "#cc99cc"
    readonly property color lcars_red: "#cc6666"
    readonly property color lcars_green: "#66cc66"
    
    // Стани систем
    property real shieldsLevel: 0.75
    property real weaponsLevel: 0.60
    property real enginesLevel: 0.90
    property real hullIntegrity: 0.85
    
    // Заголовок панелі
    Text {
        id: title
        text: "STARSHIP STATUS"
        anchors.top: parent.top
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.topMargin: 10
        color: lcars_orange
        font.bold: true
        font.pixelSize: 18
        font.family: "Arial"
    }
    
        
    // Контейнер для індикаторів
    Row {
        anchors.centerIn: parent
        spacing: 30
        
        // Індикатор щитів
        Column {
            spacing: 5
            
            Text {
                text: "SHIELDS"
                color: lcars_orange
                font.bold: true
                font.pixelSize: 12
                anchors.horizontalCenter: parent.horizontalCenter
            }
            
            Rectangle {
                width: 60
                height: 80
                color: "transparent"
                border.color: lcars_orange
                border.width: 2
                
                Rectangle {
                    id: shieldsBar
                    width: parent.width - 4
                    height: parent.height * root.shieldsLevel
                    anchors.bottom: parent.bottom
                    anchors.horizontalCenter: parent.horizontalCenter
                    color: lcars_green
                    
                    Behavior on height {
                        NumberAnimation { duration: 500; easing.type: Easing.OutQuad }
                    }
                }
                
                Text {
                    text: Math.round(root.shieldsLevel * 100) + "%"
                    anchors.centerIn: parent
                    color: "white"
                    font.bold: true
                    font.pixelSize: 14
                }
            }
        }
        
        // Індикатор зброї
        Column {
            spacing: 5
            
            Text {
                text: "WEAPONS"
                color: lcars_red
                font.bold: true
                font.pixelSize: 12
                anchors.horizontalCenter: parent.horizontalCenter
            }
            
            Rectangle {
                width: 60
                height: 80
                color: "transparent"
                border.color: lcars_red
                border.width: 2
                
                Rectangle {
                    id: weaponsBar
                    width: parent.width - 4
                    height: parent.height * root.weaponsLevel
                    anchors.bottom: parent.bottom
                    anchors.horizontalCenter: parent.horizontalCenter
                    color: lcars_red
                    
                    Behavior on height {
                        NumberAnimation { duration: 500; easing.type: Easing.OutQuad }
                    }
                }
                
                Text {
                    text: Math.round(root.weaponsLevel * 100) + "%"
                    anchors.centerIn: parent
                    color: "white"
                    font.bold: true
                    font.pixelSize: 14
                }
            }
        }
        
        // Індикатор двигунів
        Column {
            spacing: 5
            
            Text {
                text: "ENGINES"
                color: lcars_purple
                font.bold: true
                font.pixelSize: 12
                anchors.horizontalCenter: parent.horizontalCenter
            }
            
            Rectangle {
                width: 60
                height: 80
                color: "transparent"
                border.color: lcars_purple
                border.width: 2
                
                Rectangle {
                    id: enginesBar
                    width: parent.width - 4
                    height: parent.height * root.enginesLevel
                    anchors.bottom: parent.bottom
                    anchors.horizontalCenter: parent.horizontalCenter
                    color: lcars_purple
                    
                    Behavior on height {
                        NumberAnimation { duration: 500; easing.type: Easing.OutQuad }
                    }
                }
                
                Text {
                    text: Math.round(root.enginesLevel * 100) + "%"
                    anchors.centerIn: parent
                    color: "white"
                    font.bold: true
                    font.pixelSize: 14
                }
            }
        }
        
        // Індикатор цілісності корпусу
        Column {
            spacing: 5
            
            Text {
                text: "HULL"
                color: lcars_green
                font.bold: true
                font.pixelSize: 12
                anchors.horizontalCenter: parent.horizontalCenter
            }
            
            Rectangle {
                width: 60
                height: 80
                color: "transparent"
                border.color: lcars_green
                border.width: 2
                
                Rectangle {
                    id: hullBar
                    width: parent.width - 4
                    height: parent.height * root.hullIntegrity
                    anchors.bottom: parent.bottom
                    anchors.horizontalCenter: parent.horizontalCenter
                    color: root.hullIntegrity > 0.5 ? lcars_green : lcars_red
                    
                    Behavior on height {
                        NumberAnimation { duration: 500; easing.type: Easing.OutQuad }
                    }
                }
                
                Text {
                    text: Math.round(root.hullIntegrity * 100) + "%"
                    anchors.centerIn: parent
                    color: "white"
                    font.bold: true
                    font.pixelSize: 14
                }
            }
        }
    }
    
    // Анімація мерехтіння для критичних станів
    Timer {
        interval: 1000
        running: root.hullIntegrity < 0.3 || root.shieldsLevel < 0.2
        repeat: true
        onTriggered: {
            root.border.color = root.border.color === lcars_red ? lcars_orange : lcars_red
        }
    }
    
    // Функції для оновлення станів
    function updateShields(level) {
        shieldsLevel = Math.max(0, Math.min(1, level))
    }
    
    function updateWeapons(level) {
        weaponsLevel = Math.max(0, Math.min(1, level))
    }
    
    function updateEngines(level) {
        enginesLevel = Math.max(0, Math.min(1, level))
    }
    
    function updateHull(level) {
        hullIntegrity = Math.max(0, Math.min(1, level))
    }
    
    // Симуляція битви
    function simulateBattle() {
        var battleTimer = Qt.createQmlObject('import QtQuick; Timer { interval: 2000; repeat: true }', root)
        battleTimer.triggered.connect(function() {
            updateShields(Math.random())
            updateWeapons(Math.random())
            updateEngines(Math.random() * 0.5 + 0.5)
            updateHull(Math.random() * 0.4 + 0.6)
        })
        battleTimer.start()
        return battleTimer
    }
}
