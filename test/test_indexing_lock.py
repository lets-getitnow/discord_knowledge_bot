#!/usr/bin/env python3
"""
Test script to verify the indexing lock mechanism works properly.
Tests that only one indexing operation can run at a time.
"""

import asyncio
import unittest
from unittest.mock import Mock, patch, AsyncMock
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from bot.main import DiscordKnowledgeBot


class TestIndexingLock(unittest.TestCase):
    """Test cases for the indexing lock mechanism."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock the config to avoid loading real config
        with patch('bot.main.config', {
            'bot': {'prefix': '!'},
            'chromadb': {
                'persist_directory': './test_data',
                'collection_name': 'test_collection'
            }
        }):
            # Mock the external dependencies
            with patch('bot.main.ChromaStorage'), \
                 patch('bot.main.MessageCollector'), \
                 patch('bot.main.AIInterface'), \
                 patch('bot.main.ContextBuilder'):
                
                self.bot = DiscordKnowledgeBot()

    def test_initial_state(self):
        """Test that bot starts with no indexing in progress."""
        self.assertFalse(self.bot.is_indexing)
        self.assertFalse(self.bot.indexing_lock.locked())
        self.assertFalse(self.bot.is_indexing_in_progress())

    async def test_single_indexing_operation(self):
        """Test that a single indexing operation works correctly."""
        # Mock the guild
        mock_guild = Mock()
        mock_guild.id = 12345
        mock_guild.name = "Test Guild"
        
        with patch.object(self.bot, 'get_guild', return_value=mock_guild), \
             patch.object(self.bot, '_index_server', new_callable=AsyncMock) as mock_index:
            
            # Start indexing
            success, message = await self.bot.start_indexing(12345)
            
            # Verify it completed successfully
            self.assertTrue(success)
            self.assertEqual(message, "Indexing completed successfully")
            mock_index.assert_called_once_with(mock_guild)
            
            # Verify lock is released
            self.assertFalse(self.bot.is_indexing)
            self.assertFalse(self.bot.indexing_lock.locked())
            self.assertFalse(self.bot.is_indexing_in_progress())

    async def test_concurrent_indexing_blocked(self):
        """Test that concurrent indexing operations are blocked."""
        # Mock the guild
        mock_guild = Mock()
        mock_guild.id = 12345
        mock_guild.name = "Test Guild"
        
        # Create a future that we can control to simulate a long-running operation
        indexing_future = asyncio.Future()
        
        async def long_running_index(guild):
            await indexing_future
        
        with patch.object(self.bot, 'get_guild', return_value=mock_guild), \
             patch.object(self.bot, '_index_server', side_effect=long_running_index):
            
            # Start first indexing operation (won't complete until we set the future)
            task1 = asyncio.create_task(self.bot.start_indexing(12345))
            
            # Give it a moment to start
            await asyncio.sleep(0.01)
            
            # Verify first operation is in progress
            self.assertTrue(self.bot.is_indexing_in_progress())
            
            # Try to start second indexing operation
            success2, message2 = await self.bot.start_indexing(12345)
            
            # Verify second operation was blocked
            self.assertFalse(success2)
            self.assertEqual(message2, "Indexing already in progress")
            
            # Complete the first operation
            indexing_future.set_result(None)
            success1, message1 = await task1
            
            # Verify first operation completed successfully
            self.assertTrue(success1)
            self.assertEqual(message1, "Indexing completed successfully")
            
            # Verify lock is now released
            self.assertFalse(self.bot.is_indexing_in_progress())

    async def test_exception_releases_lock(self):
        """Test that exceptions in indexing operations properly release the lock."""
        # Mock the guild
        mock_guild = Mock()
        mock_guild.id = 12345
        mock_guild.name = "Test Guild"
        
        async def failing_index(guild):
            raise Exception("Simulated indexing failure")
        
        with patch.object(self.bot, 'get_guild', return_value=mock_guild), \
             patch.object(self.bot, '_index_server', side_effect=failing_index):
            
            # Start indexing operation that will fail
            success, message = await self.bot.start_indexing(12345)
            
            # Verify it failed
            self.assertFalse(success)
            self.assertIn("Indexing failed", message)
            
            # Verify lock is released despite the exception
            self.assertFalse(self.bot.is_indexing)
            self.assertFalse(self.bot.indexing_lock.locked())
            self.assertFalse(self.bot.is_indexing_in_progress())

    async def test_lock_check_before_acquisition(self):
        """Test that lock check happens before attempting acquisition."""
        # Mock the guild
        mock_guild = Mock()
        mock_guild.id = 12345
        mock_guild.name = "Test Guild"
        
        # Manually acquire the lock to simulate another operation
        await self.bot.indexing_lock.acquire()
        
        try:
            # Try to start indexing
            success, message = await self.bot.start_indexing(12345)
            
            # Verify it was blocked immediately
            self.assertFalse(success)
            self.assertEqual(message, "Indexing already in progress")
            
        finally:
            # Release the lock
            self.bot.indexing_lock.release()

    def test_status_reporting(self):
        """Test that indexing status is reported correctly."""
        status = self.bot.get_indexing_status()
        
        expected_status = {
            'is_indexing': False,
            'lock_acquired': False,
            'progress': {}
        }
        
        self.assertEqual(status, expected_status)


async def run_async_tests():
    """Run the async test methods."""
    test_instance = TestIndexingLock()
    test_instance.setUp()
    
    print("Running indexing lock tests...")
    
    # Test single operation
    print("✓ Testing single indexing operation...")
    await test_instance.test_single_indexing_operation()
    
    # Test concurrent blocking
    print("✓ Testing concurrent indexing is blocked...")
    await test_instance.test_concurrent_indexing_blocked()
    
    # Test exception handling
    print("✓ Testing exception releases lock...")
    await test_instance.test_exception_releases_lock()
    
    # Test lock check
    print("✓ Testing lock check before acquisition...")
    await test_instance.test_lock_check_before_acquisition()
    
    print("✅ All async tests passed!")


def main():
    """Run all tests."""
    # Run sync tests
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # Run async tests
    asyncio.run(run_async_tests())


if __name__ == "__main__":
    main()