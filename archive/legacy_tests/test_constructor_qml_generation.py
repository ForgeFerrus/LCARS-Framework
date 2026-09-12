import unittest
from unittest.mock import patch, MagicMock

from PyQt6.QtWidgets import QApplication, QColorDialog, QInputDialog
from PyQt6.QtGui import QColor

from lcars.engineering.constructor import InterfaceConstructor


def ensure_qapp():
    app = QApplication.instance()
    if not app:
        app = QApplication([])
    return app


class TestConstructorQLGenerator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ensure_qapp()

    def setUp(self):
        # create constructor instance without parent
        self.const = InterfaceConstructor()

    @patch('lcars.engineering.constructor.LcarsComponentFactory')
    @patch('lcars.engineering.constructor.QColorDialog')
    @patch('lcars.engineering.constructor.QInputDialog')
    def test_qml_button_runs_factory(self, mock_input, mock_color, mock_factory):
        # prepare dialog returns
        mock_input.getItem.return_value = ("button", True)
        mock_input.getText.side_effect = [("testname", True), ("HELLO", True)]
        dummy_color = QColor("#123456")
        mock_color.getColor.return_value = dummy_color

        # factory instance mock
        instance = MagicMock()
        instance.templates = {"button": ""}
        instance.generate_component.return_value = "path/to/testname.qml"
        mock_factory.return_value = instance

        # call method
        self.const.open_qml_generator()

        instance.generate_component.assert_called_once_with(
            component_type="button",
            name="testname",
            image_path="",
            color="#123456",
            text="HELLO"
        )

    @patch('lcars.engineering.constructor.QInputDialog')
    def test_qml_cancel_early(self, mock_input):
        # user cancels type selection
        mock_input.getItem.return_value = ("", False)
        # should not raise
        self.const.open_qml_generator()


if __name__ == '__main__':
    unittest.main()
