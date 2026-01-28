"""
Professional MusicGen Wrapper for Music Generation
WHY: High-quality music generation with proper audio handling
"""

import torch
from transformers import AutoProcessor, MusicgenForConditionalGeneration
import numpy as np
from typing import Optional, Tuple

from .base import BaseModel
from src.utils.config import config
from src.utils.logging import TimingLogger

class MusicGenerator(BaseModel):
    """
    Professional wrapper for MusicGen text-to-music generation
    Handles audio generation, formatting, and quality control
    """
    
    def __init__(self, device: Optional[str] = None):
        super().__init__("MusicGen", device)
        self.sample_rate = config.audio.sample_rate
        self.default_duration = config.audio.default_duration
        
    def load_model(self):
        """Load MusicGen model and processor"""
        with TimingLogger(f"Loading {self.model_name}", self.logger):
            self.processor = AutoProcessor.from_pretrained(config.models.musicgen_model)
            self.model = MusicgenForConditionalGeneration.from_pretrained(
                config.models.musicgen_model
            )
            
            if self.device != "auto":
                self.model = self.model.to(self.device)
                
            self.logger.info(f"✓ {self.model_name} loaded with sample rate {self.sample_rate}")
    
    def process(self, prompt: str, duration: Optional[int] = None) -> Tuple[np.ndarray, int]:
        """
        Generate music from text prompt
        
        Args:
            prompt: Text description for music generation
            duration: Duration in seconds
            
        Returns:
            Tuple of (audio_array, sample_rate)
        """
        duration = duration or self.default_duration
        
        try:
            with TimingLogger(f"Music generation: '{prompt}'", self.logger):
                # Validate duration
                if duration > config.audio.max_duration:
                    self.logger.warning(f"Duration {duration}s exceeds max {config.audio.max_duration}s")
                    duration = config.audio.max_duration
                
                # Calculate tokens for duration (approximate)
                max_new_tokens = int(duration * 50)  # Rough conversion
                
                # Prepare inputs
                inputs = self.processor(
                    text=[prompt],
                    padding=True,
                    return_tensors="pt",
                )
                
                inputs = self.to_device(inputs)
                
                # Generate audio
                with torch.no_grad():
                    audio_values = self.model.generate(
                        **inputs,
                        max_new_tokens=max_new_tokens,
                        do_sample=True,  # Creative variation
                        temperature=0.8,  # Balance creativity/consistency
                    )
                
                # Extract audio
                audio_array = audio_values[0, 0].cpu().numpy().astype(np.float32)
                
                self.logger.info(f"Generated {len(audio_array)/self.sample_rate:.1f}s audio for: '{prompt}'")
                
                return audio_array, self.sample_rate
                
        except RuntimeError as e:
            if "out of memory" in str(e):
                self.logger.error("GPU out of memory during music generation")
                torch.cuda.empty_cache()
                # Try with smaller duration
                if duration > 5:
                    self.logger.info("Retrying with shorter duration")
                    return self.process(prompt, duration // 2)
            raise
            
        except Exception as e:
            self.logger.error(f"Music generation failed: {e}")
            raise
    
    def normalize_audio(self, audio_array: np.ndarray) -> np.ndarray:
        """Normalize audio to prevent clipping"""
        max_val = np.max(np.abs(audio_array))
        if max_val > 0:
            return audio_array / max_val
        return audio_array
    
    def generate_with_emotion(self, prompt: str, mood: str, duration: Optional[int] = None) -> Tuple[np.ndarray, int]:
        """
        Enhanced generation with emotional context
        """
        enhanced_prompt = f"A {mood} piece of music, {prompt}"
        self.logger.debug(f"Enhanced prompt with emotion: {enhanced_prompt}")
        
        return self.process(enhanced_prompt, duration)
