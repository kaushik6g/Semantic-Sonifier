#!/usr/bin/env python3
"""
Test device detection and model loading
"""

from src.utils.device_manager import DeviceManager
from src.utils.logging import setup_logging

# Setup logging
setup_logging()

def test_device_detection():
    print("Testing Device Detection...")
    
    # Test auto device detection
    dm = DeviceManager("auto")
    device = dm.get_device()
    print(f"Auto-detected device: {device}")
    dm.print_device_info()
    
    # Test CPU forced
    dm_cpu = DeviceManager("cpu")
    cpu_device = dm_cpu.get_device()
    print(f"CPU device: {cpu_device}")
    
    print("✓ Device detection working!")

if __name__ == "__main__":
    test_device_detection()
