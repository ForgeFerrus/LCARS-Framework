"""
LCARS Security System Tests
============================
Comprehensive tests for lcars.system.security module
"""

import pytest
from lcars.modules.security import AuthManager, getSystemVersion


class TestAuthManager:
    """Test suite for AuthManager class"""
    
    def test_auth_manager_creation(self):
        """Test that AuthManager can be instantiated"""
        auth = AuthManager()
        assert auth is not None
        assert isinstance(auth, AuthManager)
    
    def test_initial_state(self):
        """Test initial authentication state"""
        auth = AuthManager()
        assert auth.Authenticated is False
        assert auth.CurrentUser is None
        assert auth.SessionToken is None
    
    def test_is_authenticated_default(self):
        """Test that default authentication state is False"""
        auth = AuthManager()
        assert auth.IsAuthenticated() is False
    
    def test_get_current_user_default(self):
        """Test that default current user is None"""
        auth = AuthManager()
        assert auth.GetCurrentUser() is None
    
    def test_get_session_token_default(self):
        """Test that default session token is None"""
        auth = AuthManager()
        assert auth.GetSessionToken() is None
    
    def test_state_attributes_mutable(self):
        """Test that state attributes can be modified"""
        auth = AuthManager()
        auth.Authenticated = True
        auth.CurrentUser = "test_user"
        auth.SessionToken = "test_token"
        
        assert auth.Authenticated is True
        assert auth.CurrentUser == "test_user"
        assert auth.SessionToken == "test_token"
    
    def test_is_authenticated_after_change(self):
        """Test IsAuthenticated reflects state changes"""
        auth = AuthManager()
        assert auth.IsAuthenticated() is False
        
        auth.Authenticated = True
        assert auth.IsAuthenticated() is True


class TestSecurityModule:
    """Test suite for security module functions"""
    
    def test_get_system_version(self):
        """Test that getSystemVersion returns a string"""
        version = getSystemVersion()
        assert isinstance(version, str)
        assert len(version) > 0
    
    def test_module_imports(self):
        """Test that security module can be imported"""
        import lcars.modules.security as security
        assert hasattr(security, 'AuthManager')
        assert hasattr(security, 'getSystemVersion')
    
    def test_public_exports(self):
        """Test that public exports are available"""
        import lcars.modules.security as security
        assert 'AuthManager' in security.PublicExports
        assert 'getSystemVersion' in security.PublicExports


class TestSecurityIntegration:
    """Integration tests for security system"""
    
    def test_security_with_mock_user(self):
        """Test authentication flow with mock user"""
        auth = AuthManager()
        
        # Simulate user login
        auth.Authenticated = True
        auth.CurrentUser = "Captain"
        auth.SessionToken = "secure_token_123"
        
        assert auth.IsAuthenticated()
        assert auth.GetCurrentUser() == "Captain"
        assert auth.GetSessionToken() == "secure_token_123"
    
    def test_security_state_reset(self):
        """Test that security state can be reset"""
        auth = AuthManager()
        
        # Set authenticated state
        auth.Authenticated = True
        auth.CurrentUser = "User1"
        auth.SessionToken = "token1"
        
        # Reset state
        auth.Authenticated = False
        auth.CurrentUser = None
        auth.SessionToken = None
        
        assert auth.IsAuthenticated() is False
        assert auth.GetCurrentUser() is None
        assert auth.GetSessionToken() is None
    
    def test_multiple_auth_managers(self):
        """Test that multiple AuthManager instances can coexist"""
        auth1 = AuthManager()
        auth2 = AuthManager()
        
        auth1.Authenticated = True
        auth1.CurrentUser = "User1"
        
        auth2.Authenticated = True
        auth2.CurrentUser = "User2"
        
        assert auth1.GetCurrentUser() == "User1"
        assert auth2.GetCurrentUser() == "User2"
        assert auth1 is not auth2


@pytest.mark.unit
class TestSecurityEdgeCases:
    """Edge case tests for security system"""
    
    def test_empty_user_handling(self):
        """Test handling of empty user strings"""
        auth = AuthManager()
        auth.CurrentUser = ""
        assert auth.GetCurrentUser() == ""
    
    def test_none_vs_empty_string(self):
        """Test difference between None and empty string"""
        auth = AuthManager()
        assert auth.GetCurrentUser() is None
        
        auth.CurrentUser = ""
        assert auth.GetCurrentUser() == ""
        assert auth.GetCurrentUser() is not None


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])
