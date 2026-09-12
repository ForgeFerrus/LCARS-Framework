import QtQuick 2.15

Rectangle {
    id: root
    width: 80; height: 35
    property alias label: labelText.text
    property color btnColor: "#cc99cc"
    color: btnColor

    signal clicked()

    Text {
        id: labelText
        text: ""
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
            console.log("Clicked: " + labelText.text)
            if (typeof con !== 'undefined' && con) con.button_clicked(labelText.text)
            clicked()
        }
        onPressed: root.color = "white"
        onReleased: root.color = root.btnColor
    }
}
