"""
Professional Logging System for Semantic Sonifier
WHY: Debugging, monitoring, and maintaining production systems
"""

import logging
import logging.handlers
import os
from pathlib import Path
from .config import config

def setup_logging(
    name: str = "semantic_sonifier",
    log_level: str = "INFO",
    log_dir: str = "logs",
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Set up professional logging with file rotation and console output
    
    Args:
        name: Logger name
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_dir: Directory to store log files
        max_bytes: Maximum log file size before rotation
        backup_count: Number of backup files to keep
    """
    
    # Create logs directory
    Path(log_dir).mkdir(exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Log format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File Handler with rotation
    log_file = Path(log_dir) / f"{name}.log"
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)  # File gets all levels
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    logger.info(f"Logging initialized for {name} at level {log_level}")
    logger.info(f"Log files stored in: {log_dir}")
    
    return logger

# Global logger instance
logger = setup_logging()

class TimingLogger:
    """Utility class for timing operations with logging"""
    
    def __init__(self, operation_name: str, logger: logging.Logger = None):
        self.operation_name = operation_name
        self.logger = logger or logging.getLogger("semantic_sonifier")
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        self.logger.info(f"Starting: {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = time.time() - self.start_time
        if exc_type is None:
            self.logger.info(f"Completed: {self.operation_name} in {elapsed:.2f}s")
        else:
            self.logger.error(f"Failed: {self.operation_name} after {elapsed:.2f}s - {exc_val}")
    
    def checkpoint(self, checkpoint_name: str):
        """Log a checkpoint with timing"""
        elapsed = time.time() - self.start_time
        self.logger.debug(f"Checkpoint '{checkpoint_name}': {elapsed:.2f}s")

# Import time for TimingLogger
import time
