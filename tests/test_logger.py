import os
import unittest
import logging
from utils.logger import setup_logger

class TestLogger(unittest.TestCase):
    def test_logger_creation(self):
        logger = setup_logger("test_logger", "test.log")
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.name, "test_logger")
        
        # Write a test log
        logger.info("This is a test log message.")
        
        # Check if log file was created
        log_path = os.path.join("logs", "test.log")
        self.assertTrue(os.path.exists(log_path))

if __name__ == '__main__':
    unittest.main()
