"""
CLIP-based Mood and Aesthetic Analyzer
WHY: Professional emotion analysis with configurable mood tags
"""

import torch
from transformers import CLIPProcessor, CLIPModel
from typing import List, Tuple, Dict, Optional
import numpy as np

from .base import BaseModel
from src.utils.config import config
from src.utils.logging import TimingLogger

class CLIPMoodAnalyzer(BaseModel):
    """
    Professional mood and aesthetic analysis using CLIP
    Classifies images into emotional and aesthetic categories
    """
    
    def __init__(self, device: Optional[str] = None):
        super().__init__("CLIP-Mood-Analyzer", device)
        self.mood_tags = config.models.mood_tags
        
    def load_model(self):
        """Load CLIP model and processor"""
        with TimingLogger(f"Loading {self.model_name}", self.logger):
            self.processor = CLIPProcessor.from_pretrained(config.models.clip_model)
            self.model = CLIPModel.from_pretrained(config.models.clip_model)
            
            if self.device != "auto":
                self.model = self.model.to(self.device)
                
            self.logger.info(f"✓ {self.model_name} loaded with {len(self.mood_tags)} mood tags")
    
    def process(self, image_path: str, top_k: int = 3) -> Tuple[str, Dict]:
        """
        Analyze image mood and aesthetic qualities
        
        Args:
            image_path: Path to input image
            top_k: Number of top moods to return
            
        Returns:
            Tuple of (primary_mood, mood_scores_dict)
        """
        from PIL import Image
        
        try:
            # Load image
            with TimingLogger("Image loading for mood analysis", self.logger):
                image = Image.open(image_path)
                if image.mode != 'RGB':
                    image = image.convert('RGB')
            
            # Process with CLIP
            with TimingLogger("CLIP mood analysis", self.logger):
                inputs = self.processor(
                    text=list(self.mood_tags),
                    images=image,
                    return_tensors="pt",
                    padding=True
                )
                
                # Move to device
                inputs = self.to_device(inputs)
                
                # Get model outputs
                with torch.no_grad():
                    outputs = self.model(**inputs)
                
                # Calculate similarities
                logits_per_image = outputs.logits_per_image
                probs = logits_per_image.softmax(dim=1)
                
                # Get top moods
                top_probs, top_indices = torch.topk(probs[0], top_k)
                
                # Create results
                mood_scores = {}
                for prob, idx in zip(top_probs, top_indices):
                    mood = self.mood_tags[idx]
                    mood_scores[mood] = prob.item()
                
                primary_mood = self.mood_tags[top_indices[0]]
                
                self.logger.info(f"Detected mood: {primary_mood} (confidence: {top_probs[0]:.3f})")
                self.logger.debug(f"Top {top_k} moods: {mood_scores}")
                
                return primary_mood, mood_scores
                
        except Exception as e:
            self.logger.error(f"Mood analysis failed for {image_path}: {e}")
            return "neutral", {"neutral": 1.0}
    
    def get_emotion_vector(self, image_path: str) -> np.ndarray:
        """
        Get emotional embedding vector for advanced emotion analysis
        Useful for emotion consistency metrics later
        """
        from PIL import Image
        
        try:
            image = Image.open(image_path)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            inputs = self.processor(images=image, return_tensors="pt")
            inputs = self.to_device(inputs)
            
            with torch.no_grad():
                image_features = self.model.get_image_features(**inputs)
            
            # Normalize features
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)
            
            return image_features.cpu().numpy()[0]
            
        except Exception as e:
            self.logger.error(f"Emotion vector extraction failed: {e}")
            return np.zeros(512)  # Default CLIP feature size
