import QtQuick 2.15

Rectangle {
    id: root
    width: 140; height: 50
    property string text: "KLINGON"
    property color btnColor: "#660000"
    color: btnColor

    signal clicked()

    Text {
        id: t
        text: root.text
        anchors.centerIn: parent
        color: "white"
        font.bold: true
        font.pixelSize: 14
    }

    MouseArea {
        anchors.fill: parent
        onClicked: {
            console.log("KlingonButton clicked: " + root.text)
            if (typeof con !== 'undefined' && con) con.button_clicked(root.text)
            clicked()
        }
    }
}
