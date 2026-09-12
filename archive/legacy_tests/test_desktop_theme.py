import unittest
from unittest.mock import MagicMock, patch
import sys
from pathlib import Path

# Ensure the project root is in the Python path
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import QApplication

from lcars.ui.desktop import LCARSDesktop
from lcars.modules.config_manager import config_manager
from lcars.themes.palette import LCARSEra, FactionEra

class TestDesktopTheme(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication(sys.argv)

    def setUp(self):
        # Reset config before each test
        config_manager.configs['app'] = {}
        # Mock the BoardComputer and its dependencies to isolate the UI
        self.mock_computer = MagicMock()
        self.mock_computer.event_bus = MagicMock()
        self.mock_computer.sounds = MagicMock()
        
        # Patch get_computer to return our mock
        self.patcher = patch('lcars.ui.desktop.get_computer', return_value=self.mock_computer)
        self.mock_get_computer = self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def test_initial_theme_from_config(self):
        """Test if the desktop initializes with the theme from the config."""
        config_manager.set('app', 'era', '24th')
        config_manager.set('app', 'faction', 'KLINGON')

        desktop = LCARSDesktop()
        
        self.assertEqual(desktop.era, LCARSEra.LCARS_24TH)
        self.assertEqual(desktop.faction, FactionEra.KLINGON)
        
        # Clean up the created window
        desktop.close()

    def test_theme_change_via_config_watcher(self):
        """Test if the desktop theme changes when the config is updated."""
        config_manager.set('app', 'era', '25th')
        config_manager.set('app', 'faction', 'FEDERATION')

        # patch EngineeringView to avoid constructor signature errors during config callbacks
        with patch('lcars.ui.desktop.EngineeringView', new=MagicMock):
            desktop = LCARSDesktop()
            # Mock setup_desktop to verify it's called
            desktop.setup_desktop = MagicMock()

        # Act: Change the configuration
        config_manager.set('app', 'faction', 'ROMULAN')

        # Assert: Check if setup_desktop was called with the new faction
        desktop.setup_desktop.assert_called_with('ROMULAN', '25th')
        
        desktop.close()

    def test_show_settings_opens_system_control(self):
        """Test if show_settings opens the SystemControlCenter."""
        with patch('lcars.ui.desktop.EngineeringView', new=MagicMock):
            desktop = LCARSDesktop()
            desktop.show_system_control = MagicMock()
        
        # Act
        desktop.show_settings()
        
        # Assert
        desktop.show_system_control.assert_called_once()
        
        desktop.close()

    def test_alert_lock_screen_shows_on_red(self):
        """Red alert should display the lock screen and normal alert hide it."""
        with patch('lcars.ui.desktop.EngineeringView', new=MagicMock):
            desktop = LCARSDesktop()
            # ensure lock screen starts hidden
            self.assertFalse(desktop.lock_screen.isVisible())
            from lcars.system.alert import alert_system, AlertLevel
        # switch to red
        alert_system.set_level(AlertLevel.RED)
        self.assertTrue(desktop.lock_screen.isVisible())
        # back to normal
        alert_system.set_level(AlertLevel.NORMAL)
        self.assertFalse(desktop.lock_screen.isVisible())
        desktop.close()

    def test_language_configuration_applies(self):
        """Changing 'app.language' in config should update LocalizationSubsystem."""
        from lcars.system.localization import LOCALIZATION as Language
        config_manager.set('app', 'language', 'ua')
        desktop = LCARSDesktop()
        # desktop init should have set language according to config
        self.assertEqual(Language.get_language(), 'ua')
        # changing again via config triggers watcher
        config_manager.set('app', 'language', 'en')
        self.assertEqual(Language.get_language(), 'en')
        desktop.close()

if __name__ == '__main__':
    unittest.main()
