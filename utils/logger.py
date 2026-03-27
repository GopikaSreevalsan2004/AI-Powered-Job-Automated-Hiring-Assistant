import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logger(name, log_file="app.log", level=logging.INFO):
    """
    Function to setup as many loggers as you want for different functionalities.
    """
    formatter = logging.Formatter('%(asctime)s %(levelname)s [%(name)s]: %(message)s')

    # Create logs directory if it doesn't exist
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_path = os.path.join(log_dir, log_file)
    
    handler = RotatingFileHandler(log_path, maxBytes=5000000, backupCount=5)
    handler.setFormatter(formatter)
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    if not logger.handlers:
        logger.addHandler(handler)
        logger.addHandler(console_handler)

    return logger

# Default logger for utility functions
logger = setup_logger("system_utils")
