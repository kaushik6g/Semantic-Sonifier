#!/usr/bin/env python3
"""
Test the professional logging system
"""

from src.utils.logging import logger, TimingLogger

def test_logging():
    print("Testing Professional Logging System...")
    
    # Test different log levels
    logger.debug("This is a DEBUG message - detailed info")
    logger.info("This is an INFO message - general info")
    logger.warning("This is a WARNING message - something concerning")
    logger.error("This is an ERROR message - something went wrong")
    
    # Test timing logger
    with TimingLogger("Test Operation") as timer:
        logger.info("Doing some work...")
        import time
        time.sleep(0.1)  # Simulate work
        timer.checkpoint("Halfway done")
        time.sleep(0.1)
    
    print("✓ Logging system working! Check 'logs/semantic_sonifier.log'")

if __name__ == "__main__":
    test_logging()
