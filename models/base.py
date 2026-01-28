"""
Base Model Architecture for Semantic Sonifier
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import torch

from src.utils.logging import logger, TimingLogger
from src.utils.config import config
from src.utils.device_manager import DeviceManager

class BaseModel(ABC):
    """Abstract base class for all AI models"""
    
    def __init__(self, model_name: str, device: Optional[str] = None):
        self.model_name = model_name
        
        # Resolve device using DeviceManager
        device_preference = device or config.models.device
        device_manager = DeviceManager(device_preference)
        self.device = device_manager.get_device()
        
        self.model = None
        self.processor = None
        self.logger = logger.getChild(self.__class__.__name__)
        
        self.logger.info(f"Initialized {model_name} on device: {self.device}")
        
    @abstractmethod
    def load_model(self):
        """Load the model and processor - to be implemented by subclasses"""
        pass
    
    @abstractmethod
    def process(self, *args, **kwargs) -> Any:
        """Process input - to be implemented by subclasses"""
        pass
    
    def to_device(self, inputs: Dict) -> Dict:
        """Move inputs to appropriate device"""
        if hasattr(self, 'device') and self.device:
            return {k: v.to(self.device) if hasattr(v, 'to') else v 
                   for k, v in inputs.items()}
        return inputs
    
    def unload_model(self):
        """Unload model to free memory"""
        if self.model is not None:
            del self.model
            self.model = None
        if self.processor is not None:
            del self.processor
            self.processor = None
        
        # Clear memory based on device type
        if self.device == 'cuda' and torch.cuda.is_available():
            torch.cuda.empty_cache()
        elif self.device == 'mps' and hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            torch.mps.empty_cache()
            
        self.logger.info(f"Unloaded model: {self.model_name}")
    
    def __enter__(self):
        """Context manager support"""
        if self.model is None:
            self.load_model()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager cleanup"""
        self.unload_model()

class PipelineComponent:
    """Base class for pipeline components with error handling"""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logger.getChild(name)
    
    def safe_process(self, *args, **kwargs) -> Any:
        """
        Process with comprehensive error handling and logging
        """
        try:
            with TimingLogger(f"{self.name}.process", self.logger):
                result = self.process(*args, **kwargs)
                self.logger.debug(f"Successfully processed: {self.name}")
                return result
                
        except Exception as e:
            self.logger.error(f"Failed in {self.name}: {str(e)}", exc_info=True)
            raise
    
    @abstractmethod
    def process(self, *args, **kwargs) -> Any:
        """Main processing method - to be implemented by subclasses"""
        pass
