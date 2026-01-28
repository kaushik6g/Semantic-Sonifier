"""
BLIP-2 Model Wrapper for Image Captioning
WHY: Professional interface with error handling, logging, and configuration
"""

import torch
from transformers import Blip2Processor, Blip2ForConditionalGeneration
from typing import Optional, List
import warnings

from .base import BaseModel
from src.utils.config import config
from src.utils.logging import TimingLogger

class BLIP2Model(BaseModel):
    """
    Professional wrapper for BLIP-2 image captioning
    Handles loading, processing, and error recovery
    """
    
    def __init__(self, device: Optional[str] = None):
        super().__init__("BLIP-2", device)
        self.max_length = 100
        self.num_beams = 5
        
    def load_model(self):
        """Load BLIP-2 model and processor with professional error handling"""
        with TimingLogger(f"Loading {self.model_name}", self.logger):
            try:
                # Suppress unnecessary warnings
                warnings.filterwarnings("ignore", message=".*padding_mask.*")
                
                self.processor = Blip2Processor.from_pretrained(config.models.blip2_model)
                self.model = Blip2ForConditionalGeneration.from_pretrained(
                    config.models.blip2_model,
                    torch_dtype=torch.float16,
                    device_map=self.device
                )
                
                self.logger.info(f"✓ {self.model_name} loaded successfully")
                self.logger.debug(f"Model device: {self.model.device}")
                self.logger.debug(f"Model dtype: {self.model.dtype}")
                
            except Exception as e:
                self.logger.error(f"Failed to load {self.model_name}: {e}")
                raise
    
    def process(self, image_path: str, max_length: Optional[int] = None) -> str:
        """
        Generate caption for image with comprehensive error handling
        
        Args:
            image_path: Path to input image
            max_length: Maximum caption length
            
        Returns:
            Generated caption string
        """
        from PIL import Image, UnidentifiedImageError
        
        max_length = max_length or self.max_length
        
        try:
            # Load and validate image
            with TimingLogger("Image loading", self.logger):
                try:
                    image = Image.open(image_path)
                    if image.mode != 'RGB':
                        image = image.convert('RGB')
                    self.logger.debug(f"Image loaded: {image.size}, mode: {image.mode}")
                except UnidentifiedImageError:
                    self.logger.error(f"Cannot identify image file: {image_path}")
                    return "an image"
                except Exception as e:
                    self.logger.error(f"Error loading image {image_path}: {e}")
                    return "an image"
            
            # Process image
            with TimingLogger("BLIP-2 processing", self.logger):
                inputs = self.processor(
                    images=image, 
                    return_tensors="pt"
                ).to(self.model.device, torch.float16)
                
                # Generate caption
                with torch.no_grad():
                    generated_ids = self.model.generate(
                        **inputs,
                        max_length=max_length,
                        num_beams=self.num_beams,
                        early_stopping=True,
                        do_sample=False  # Deterministic for reproducibility
                    )
                
                # Decode caption
                caption = self.processor.batch_decode(
                    generated_ids, 
                    skip_special_tokens=True
                )[0].strip()
                
                self.logger.info(f"Generated caption: '{caption}'")
                return caption
                
        except RuntimeError as e:
            if "out of memory" in str(e):
                self.logger.error(f"GPU out of memory for {self.model_name}")
                torch.cuda.empty_cache()
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error in {self.model_name}: {e}")
            return "an image"
    
    def batch_process(self, image_paths: List[str]) -> List[str]:
        """Process multiple images (for efficiency)"""
        captions = []
        for image_path in image_paths:
            caption = self.process(image_path)
            captions.append(caption)
        return captions
