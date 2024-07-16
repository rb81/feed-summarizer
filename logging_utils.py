import logging
import sys
from logging.handlers import RotatingFileHandler

def setup_logging(log_file='app.log', console_level=logging.INFO, file_level=logging.DEBUG):
    # Create a custom logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Create handlers
    c_handler = logging.StreamHandler(sys.stdout)
    f_handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5)
    c_handler.setLevel(console_level)
    f_handler.setLevel(file_level)

    # Create formatters and add it to handlers
    c_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    c_handler.setFormatter(c_format)
    f_handler.setFormatter(f_format)

    # Add handlers to the logger
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)

    return logger