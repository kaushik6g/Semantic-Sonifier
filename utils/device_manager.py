"""
Device Management for Semantic Sonifier
WHY: Handle different hardware (CPU, GPU, MPS for Apple Silicon) properly
"""

import torch
import logging

# Create logger directly to avoid circular imports
logger = logging.getLogger("semantic_sonifier.DeviceManager")

class DeviceManager:
    """Manage device detection and allocation for AI models"""
    
    def __init__(self, device_preference="auto"):
        self.device_preference = device_preference
        self.available_devices = self._detect_available_devices()
        self.preferred_device = self._select_preferred_device()
        
    def _detect_available_devices(self) -> dict:
        """Detect available computing devices"""
        devices = {}
        
        # Check CUDA (NVIDIA GPU)
        devices['cuda'] = torch.cuda.is_available()
        if devices['cuda']:
            devices['cuda_count'] = torch.cuda.device_count()
            devices['cuda_name'] = torch.cuda.get_device_name(0)
        
        # Check MPS (Apple Silicon GPU)
        devices['mps'] = hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()
        
        # CPU is always available
        devices['cpu'] = True
        
        return devices
    
    def _select_preferred_device(self) -> str:
        """Select the best available device"""
        if self.available_devices.get('cuda', False):
            device = "cuda"
            logger.info(f"Using CUDA device: {self.available_devices['cuda_name']}")
        elif self.available_devices.get('mps', False):
            device = "mps"
            logger.info("Using Apple Silicon MPS device")
        else:
            device = "cpu"
            logger.info("Using CPU device")
        
        return device
    
    def get_device(self) -> str:
        """Get the appropriate device based on preference and availability"""
        if self.device_preference == "auto":
            return self.preferred_device
        elif self.device_preference in self.available_devices and self.available_devices[self.device_preference]:
            return self.device_preference
        else:
            logger.warning(f"Requested device '{self.device_preference}' not available, using '{self.preferred_device}'")
            return self.preferred_device
    
    def print_device_info(self):
        """Print detailed device information"""
        logger.info("=== Device Information ===")
        logger.info(f"Preferred device: {self.preferred_device}")
        logger.info("Available devices:")
        for device, available in self.available_devices.items():
            if available and device != 'cpu':  # CPU is always True
                if device == 'cuda':
                    logger.info(f"  - CUDA: {self.available_devices['cuda_name']} (Count: {self.available_devices['cuda_count']})")
                elif device == 'mps':
                    logger.info(f"  - MPS: Apple Silicon GPU")
        logger.info("==========================")
