"""
LCARS Alert System Tests
=========================
Comprehensive tests for lcars.system.alert module
"""

import pytest
from unittest.mock import Mock
from lcars.system.alert import AlertLevel, AlertSystem, getSystemVersion


class TestAlertLevel:
    """Test suite for AlertLevel enum"""
    
    def test_alert_level_values(self):
        """Test that AlertLevel has correct values"""
        assert AlertLevel.GREEN == 0
        assert AlertLevel.YELLOW == 1
        assert AlertLevel.RED == 2
    
    def test_alert_level_is_enum(self):
        """Test that AlertLevel is an IntEnum"""
        from enum import IntEnum
        assert issubclass(AlertLevel, IntEnum)
    
    def test_alert_level_comparison(self):
        """Test that AlertLevel values can be compared"""
        assert AlertLevel.GREEN < AlertLevel.YELLOW
        assert AlertLevel.YELLOW < AlertLevel.RED
        assert AlertLevel.GREEN < AlertLevel.RED
    
    def test_alert_level_iteration(self):
        """Test that AlertLevel can be iterated"""
        levels = [AlertLevel.GREEN, AlertLevel.YELLOW, AlertLevel.RED]
        for level in levels:
            assert level in AlertLevel


class TestAlertSystemBasic:
    """Test basic AlertSystem functionality"""
    
    def test_alert_system_creation(self):
        """Test that AlertSystem can be instantiated"""
        alert_sys = AlertSystem()
        assert alert_sys is not None
        assert isinstance(alert_sys, AlertSystem)
    
    def test_initial_state(self):
        """Test initial alert state"""
        alert_sys = AlertSystem()
        # Default state before Init
        assert hasattr(alert_sys, 'Level')
    
    def test_init_without_parameters(self):
        """Test Init without parameters"""
        alert_sys = AlertSystem()
        alert_sys.Init()
        
        assert alert_sys.Level == AlertLevel.GREEN
        assert alert_sys.EventBus is None
        assert alert_sys.Controller is None
    
    def test_init_with_event_bus(self, mock_event_bus):
        """Test Init with EventBus"""
        alert_sys = AlertSystem()
        alert_sys.Init(EventBus=mock_event_bus)
        
        assert alert_sys.EventBus == mock_event_bus
    
    def test_init_with_controller(self):
        """Test Init with Controller"""
        mock_controller = Mock()
        alert_sys = AlertSystem()
        alert_sys.Init(Controller=mock_controller)
        
        assert alert_sys.Controller == mock_controller
    
    def test_init_with_both_parameters(self, mock_event_bus):
        """Test Init with both EventBus and Controller"""
        mock_controller = Mock()
        alert_sys = AlertSystem()
        alert_sys.Init(EventBus=mock_event_bus, Controller=mock_controller)
        
        assert alert_sys.EventBus == mock_event_bus
        assert alert_sys.Controller == mock_controller


class TestAlertSystemLevelManagement:
    """Test alert level management"""
    
    def test_initial_level_is_green(self):
        """Test that initial level is GREEN"""
        alert_sys = AlertSystem()
        alert_sys.Init()
        
        assert alert_sys.Level == AlertLevel.GREEN
    
    def test_set_level_to_yellow(self):
        """Test setting level to YELLOW"""
        alert_sys = AlertSystem()
        alert_sys.Init()
        
        alert_sys.SetLevel(AlertLevel.YELLOW)
        assert alert_sys.Level == AlertLevel.YELLOW
    
    def test_set_level_to_red(self):
        """Test setting level to RED"""
        alert_sys = AlertSystem()
        alert_sys.Init()
        
        alert_sys.SetLevel(AlertLevel.RED)
        assert alert_sys.Level == AlertLevel.RED
    
    def test_set_level_back_to_green(self):
        """Test setting level back to GREEN"""
        alert_sys = AlertSystem()
        alert_sys.Init()
        
        alert_sys.SetLevel(AlertLevel.RED)
        alert_sys.SetLevel(AlertLevel.GREEN)
        assert alert_sys.Level == AlertLevel.GREEN
    
    def test_set_same_level_no_change(self, mock_event_bus):
        """Test that setting same level doesn't trigger events"""
        alert_sys = AlertSystem()
        alert_sys.Init(EventBus=mock_event_bus)
        
        alert_sys.SetLevel(AlertLevel.GREEN)  # Same as initial
        
        # Should not emit event since level didn't change
        assert len(mock_event_bus.events) == 0
    
    def test_set_level_with_invalid_type(self):
        """Test SetLevel with invalid type"""
        alert_sys = AlertSystem()
        alert_sys.Init()
        
        # Should handle non-AlertLevel values gracefully
        alert_sys.SetLevel("invalid")
        # Level should remain unchanged
        assert alert_sys.Level == AlertLevel.GREEN


class TestAlertSystemEventBusIntegration:
    """Test EventBus integration"""
    
    def test_level_change_emits_event(self, mock_event_bus):
        """Test that level change emits event"""
        alert_sys = AlertSystem()
        alert_sys.Init(EventBus=mock_event_bus)
        
        alert_sys.SetLevel(AlertLevel.YELLOW)
        
        assert len(mock_event_bus.events) == 1
        event_name, event_data = mock_event_bus.events[0]
        assert event_name == "CHANGED"
        assert event_data["level"] == "YELLOW"
    
    def test_multiple_level_changes(self, mock_event_bus):
        """Test multiple level changes"""
        alert_sys = AlertSystem()
        alert_sys.Init(EventBus=mock_event_bus)
        
        alert_sys.SetLevel(AlertLevel.YELLOW)
        alert_sys.SetLevel(AlertLevel.RED)
        alert_sys.SetLevel(AlertLevel.GREEN)
        
        assert len(mock_event_bus.events) == 3
        
        # Check event sequence
        events = [e[1]["level"] for e in mock_event_bus.events]
        assert events == ["YELLOW", "RED", "GREEN"]


class TestAlertSystemControllerIntegration:
    """Test Controller integration"""
    
    def test_level_change_calls_controller(self):
        """Test that level change calls Controller.ApplyLevel"""
        mock_controller = Mock()
        alert_sys = AlertSystem()
        alert_sys.Init(Controller=mock_controller)
        
        alert_sys.SetLevel(AlertLevel.YELLOW)
        
        mock_controller.ApplyLevel.assert_called_once_with(AlertLevel.YELLOW)
    
    def test_multiple_controller_calls(self):
        """Test multiple controller calls"""
        mock_controller = Mock()
        alert_sys = AlertSystem()
        alert_sys.Init(Controller=mock_controller)
        
        alert_sys.SetLevel(AlertLevel.YELLOW)
        alert_sys.SetLevel(AlertLevel.RED)
        
        assert mock_controller.ApplyLevel.call_count == 2
        
        # Check call arguments
        calls = mock_controller.ApplyLevel.call_args_list
        assert calls[0][0][0] == AlertLevel.YELLOW
        assert calls[1][0][0] == AlertLevel.RED


class TestAlertSystemLevelCycling:
    """Test level cycling functionality"""
    
    def test_cycle_level_from_green(self):
        """Test cycling from GREEN to YELLOW"""
        alert_sys = AlertSystem()
        alert_sys.Init()
        
        new_level = alert_sys.CycleLevel()
        assert new_level == AlertLevel.YELLOW
        assert alert_sys.Level == AlertLevel.YELLOW
    
    def test_cycle_level_from_yellow(self):
        """Test cycling from YELLOW to RED"""
        alert_sys = AlertSystem()
        alert_sys.Init()
        alert_sys.SetLevel(AlertLevel.YELLOW)
        
        new_level = alert_sys.CycleLevel()
        assert new_level == AlertLevel.RED
        assert alert_sys.Level == AlertLevel.RED
    
    def test_cycle_level_from_red(self):
        """Test cycling from RED to GREEN"""
        alert_sys = AlertSystem()
        alert_sys.Init()
        alert_sys.SetLevel(AlertLevel.RED)
        
        new_level = alert_sys.CycleLevel()
        assert new_level == AlertLevel.GREEN
        assert alert_sys.Level == AlertLevel.GREEN
    
    def test_full_cycle_sequence(self):
        """Test full cycle sequence GREEN -> YELLOW -> RED -> GREEN"""
        alert_sys = AlertSystem()
        alert_sys.Init()
        
        levels = []
        for _ in range(3):
            alert_sys.CycleLevel()
            levels.append(alert_sys.Level)
        
        assert levels == [AlertLevel.YELLOW, AlertLevel.RED, AlertLevel.GREEN]


class TestAlertSystemLevelAdjustment:
    """Test level adjustment methods"""
    
    def test_raise_level_from_green(self):
        """Test raising level from GREEN to YELLOW"""
        alert_sys = AlertSystem()
        alert_sys.Init()
        
        alert_sys.RaiseLevel()
        assert alert_sys.Level == AlertLevel.YELLOW
    
    def test_raise_level_from_yellow(self):
        """Test raising level from YELLOW to RED"""
        alert_sys = AlertSystem()
        alert_sys.Init()
        alert_sys.SetLevel(AlertLevel.YELLOW)
        
        alert_sys.RaiseLevel()
        assert alert_sys.Level == AlertLevel.RED
    
    def test_raise_level_from_red(self):
        """Test raising level from RED (should stay RED)"""
        alert_sys = AlertSystem()
        alert_sys.Init()
        alert_sys.SetLevel(AlertLevel.RED)
        
        alert_sys.RaiseLevel()
        assert alert_sys.Level == AlertLevel.RED
    
    def test_lower_level_from_red(self):
        """Test lowering level from RED to YELLOW"""
        alert_sys = AlertSystem()
        alert_sys.Init()
        alert_sys.SetLevel(AlertLevel.RED)
        
        alert_sys.LowerLevel()
        assert alert_sys.Level == AlertLevel.YELLOW
    
    def test_lower_level_from_yellow(self):
        """Test lowering level from YELLOW to GREEN"""
        alert_sys = AlertSystem()
        alert_sys.Init()
        alert_sys.SetLevel(AlertLevel.YELLOW)
        
        alert_sys.LowerLevel()
        assert alert_sys.Level == AlertLevel.GREEN
    
    def test_lower_level_from_green(self):
        """Test lowering level from GREEN (should stay GREEN)"""
        alert_sys = AlertSystem()
        alert_sys.Init()
        
        alert_sys.LowerLevel()
        assert alert_sys.Level == AlertLevel.GREEN


class TestAlertSystemQueryMethods:
    """Test query methods"""
    
    def test_is_level_with_matching_level(self):
        """Test IsLevel with matching level"""
        alert_sys = AlertSystem()
        alert_sys.Init()
        
        assert alert_sys.IsLevel(AlertLevel.GREEN) is True
    
    def test_is_level_with_non_matching_level(self):
        """Test IsLevel with non-matching level"""
        alert_sys = AlertSystem()
        alert_sys.Init()
        
        assert alert_sys.IsLevel(AlertLevel.YELLOW) is False
    
    def test_is_level_after_change(self):
        """Test IsLevel after level change"""
        alert_sys = AlertSystem()
        alert_sys.Init()
        
        alert_sys.SetLevel(AlertLevel.RED)
        assert alert_sys.IsLevel(AlertLevel.RED) is True
        assert alert_sys.IsLevel(AlertLevel.GREEN) is False
    
    def test_is_alert_with_green(self):
        """Test IsAlert with GREEN level"""
        alert_sys = AlertSystem()
        alert_sys.Init()
        
        assert alert_sys.IsAlert() is False
    
    def test_is_alert_with_yellow(self):
        """Test IsAlert with YELLOW level"""
        alert_sys = AlertSystem()
        alert_sys.Init()
        alert_sys.SetLevel(AlertLevel.YELLOW)
        
        assert alert_sys.IsAlert() is True
    
    def test_is_alert_with_red(self):
        """Test IsAlert with RED level"""
        alert_sys = AlertSystem()
        alert_sys.Init()
        alert_sys.SetLevel(AlertLevel.RED)
        
        assert alert_sys.IsAlert() is True


class TestAlertSystemVersion:
    """Test version function"""
    
    def test_get_system_version(self):
        """Test that getSystemVersion returns valid version"""
        version = getSystemVersion()
        assert isinstance(version, str)
        assert len(version) > 0


@pytest.mark.unit
class TestAlertSystemEdgeCases:
    """Edge case tests for AlertSystem"""
    
    def test_multiple_init_calls(self, mock_event_bus):
        """Test multiple Init calls"""
        alert_sys = AlertSystem()
        alert_sys.Init(EventBus=mock_event_bus)
        alert_sys.Init(EventBus=mock_event_bus)
        
        # Should handle gracefully
        assert alert_sys.EventBus == mock_event_bus
    
    def test_rapid_level_changes(self, mock_event_bus):
        """Test rapid level changes"""
        alert_sys = AlertSystem()
        alert_sys.Init(EventBus=mock_event_bus)
        
        # Rapid changes
        for _ in range(10):
            alert_sys.SetLevel(AlertLevel.RED)
            alert_sys.SetLevel(AlertLevel.GREEN)
        
        # Should handle without errors
        assert alert_sys.Level == AlertLevel.GREEN


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])