"""
Test superuser permission system for Discord Knowledge Bot.
"""

import os
import unittest
from unittest.mock import Mock, patch
from utils.permissions import is_superuser, has_permission, get_superuser_id

class TestSuperuserPermissions(unittest.TestCase):
    """Test cases for superuser permission system."""
    
    def setUp(self):
        """Set up test environment."""
        # Clear any existing environment variables
        if 'SUPERUSER_DISCORD_ID' in os.environ:
            del os.environ['SUPERUSER_DISCORD_ID']
    
    def test_get_superuser_id_not_set(self):
        """Test get_superuser_id when not configured."""
        superuser_id = get_superuser_id()
        self.assertIsNone(superuser_id)
    
    def test_get_superuser_id_set(self):
        """Test get_superuser_id when configured."""
        test_id = "123456789"
        os.environ['SUPERUSER_DISCORD_ID'] = test_id
        superuser_id = get_superuser_id()
        self.assertEqual(superuser_id, test_id)
    
    def test_is_superuser_not_configured(self):
        """Test is_superuser when no superuser is configured."""
        result = is_superuser(123456789)
        self.assertFalse(result)
    
    def test_is_superuser_matches(self):
        """Test is_superuser when user ID matches."""
        test_id = "123456789"
        os.environ['SUPERUSER_DISCORD_ID'] = test_id
        result = is_superuser(123456789)
        self.assertTrue(result)
    
    def test_is_superuser_no_match(self):
        """Test is_superuser when user ID doesn't match."""
        test_id = "123456789"
        os.environ['SUPERUSER_DISCORD_ID'] = test_id
        result = is_superuser(987654321)
        self.assertFalse(result)
    
    def test_is_superuser_invalid_format(self):
        """Test is_superuser with invalid superuser ID format."""
        os.environ['SUPERUSER_DISCORD_ID'] = "invalid_id"
        result = is_superuser(123456789)
        self.assertFalse(result)
    
    def test_has_permission_superuser(self):
        """Test has_permission for superuser."""
        test_id = "123456789"
        os.environ['SUPERUSER_DISCORD_ID'] = test_id
        
        # Mock guild permissions
        mock_permissions = Mock()
        mock_permissions.administrator = False
        
        result = has_permission(123456789, mock_permissions, "administrator")
        self.assertTrue(result)
    
    def test_has_permission_administrator(self):
        """Test has_permission for regular administrator."""
        # No superuser configured
        mock_permissions = Mock()
        mock_permissions.administrator = True
        
        result = has_permission(123456789, mock_permissions, "administrator")
        self.assertTrue(result)
    
    def test_has_permission_no_permission(self):
        """Test has_permission for user without permission."""
        # No superuser configured
        mock_permissions = Mock()
        mock_permissions.administrator = False
        
        result = has_permission(123456789, mock_permissions, "administrator")
        self.assertFalse(result)
    
    def test_has_permission_unknown_permission(self):
        """Test has_permission with unknown permission."""
        mock_permissions = Mock()
        # Mock doesn't have the unknown permission attribute
        del mock_permissions.unknown_permission
        
        result = has_permission(123456789, mock_permissions, "unknown_permission")
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main() 