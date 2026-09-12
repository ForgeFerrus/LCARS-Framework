import pytest
from lcars.engineering.alert_controller import EngineeringController
from lcars.system.alert import AlertLevel
from lcars.modules.mode_manager import SystemMode


def test_apply_alert_level_changes():
    ctrl = EngineeringController()
    # start green
    ctrl.apply_alert_level(AlertLevel.GREEN)
    assert ctrl.deflector.shield_level == 0
    assert ctrl.drive.mode == "standby"
    # yellow
    ctrl.apply_alert_level(AlertLevel.YELLOW)
    assert ctrl.deflector.shield_level == 50
    assert ctrl.drive.mode == "standby"
    # red
    ctrl.apply_alert_level(AlertLevel.RED)
    assert ctrl.deflector.shield_level == 100
    assert ctrl.drive.mode == "impulse"


def test_apply_system_mode_changes():
    ctrl = EngineeringController()
    ctrl.apply_system_mode(SystemMode.BATTLE)
    assert ctrl.deflector.shield_level == 200
    assert ctrl.drive.mode == "warp"
    ctrl.apply_system_mode(SystemMode.SCIENCE)
    assert ctrl.deflector.shield_level == 20
    assert ctrl.drive.mode == "standby"
