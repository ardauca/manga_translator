# app/utils/logger.py - Logging Konfigürasyonu

import logging
import sys

def setup_logger(name: str, level=logging.INFO):
    """Logger setup"""
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    
    # Format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    
    if not logger.handlers:
        logger.addHandler(handler)
    
    return logger

# Application logger
app_logger = setup_logger('manga_translator')
