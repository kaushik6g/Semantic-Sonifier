"""
Main Semantic Sonifier Class - The Core Orchestrator
WHY: Ties all components together with professional pipeline management
"""

from typing import Dict, Any, Optional, Tuple
import numpy as np
from pathlib import Path

from .blip2_wrapper import BLIP2Model
from .clip_mood_analyzer import CLIPMoodAnalyzer
from .music_generator import MusicGenerator
from .base import PipelineComponent
from src.utils.config import config
from src.utils.logging import logger, TimingLogger

class ImageAnalyzer(PipelineComponent):
    """Pipeline component for comprehensive image analysis"""
    
    def __init__(self):
        super().__init__("ImageAnalyzer")
        self.blip_model = None
        self.clip_analyzer = None
    
    def process(self, image_path: str) -> Dict[str, Any]:
        """
        Comprehensive image analysis combining BLIP-2 and CLIP
        
        Returns:
            Dictionary with caption, mood, and analysis metadata
        """
        self.logger.info(f"Analyzing image: {image_path}")
        
        # Initialize models if needed
        if self.blip_model is None:
            self.blip_model = BLIP2Model()
            self.blip_model.load_model()
        
        if self.clip_analyzer is None:
            self.clip_analyzer = CLIPMoodAnalyzer()
            self.clip_analyzer.load_model()
        
        # Get image understanding
        caption = self.blip_model.process(image_path)
        primary_mood, mood_scores = self.clip_analyzer.process(image_path)
        
        return {
            'caption': caption,
            'primary_mood': primary_mood,
            'mood_scores': mood_scores,
            'image_path': image_path
        }
    
    def unload_models(self):
        """Unload models to free memory"""
        if self.blip_model:
            self.blip_model.unload_model()
        if self.clip_analyzer:
            self.clip_analyzer.unload_model()

class MusicOrchestrator(PipelineComponent):
    """Pipeline component for intelligent music generation"""
    
    def __init__(self):
        super().__init__("MusicOrchestrator")
        self.music_generator = None
    
    def process(self, analysis_result: Dict[str, Any], duration: Optional[int] = None) -> Dict[str, Any]:
        """
        Generate music based on image analysis with intelligent prompt engineering
        
        Returns:
            Dictionary with audio and generation metadata
        """
        self.logger.info("Orchestrating music generation...")
        
        if self.music_generator is None:
            self.music_generator = MusicGenerator()
            self.music_generator.load_model()
        
        # Intelligent prompt engineering - THIS IS OUR SECRET SAUCE
        prompt = self._create_intelligent_prompt(
            analysis_result['caption'],
            analysis_result['primary_mood'],
            analysis_result['mood_scores']
        )
        
        # Generate music
        audio_array, sample_rate = self.music_generator.generate_with_emotion(
            prompt=prompt,
            mood=analysis_result['primary_mood'],
            duration=duration
        )
        
        return {
            'audio_array': audio_array,
            'sample_rate': sample_rate,
            'prompt_used': prompt,
            'duration_seconds': len(audio_array) / sample_rate
        }
    
    def _create_intelligent_prompt(self, caption: str, primary_mood: str, mood_scores: Dict) -> str:
        """
        Create intelligent music prompt using our custom rules
        This is where the magic happens!
        """
        # Base structure
        prompt_parts = [f"A {primary_mood} piece of music for {caption}"]
        
        # Enhanced mood context based on confidence
        top_moods = list(mood_scores.keys())[:2]  # Top 2 moods
        if len(top_moods) > 1 and mood_scores[top_moods[1]] > 0.2:
            prompt_parts.append(f"with elements of {top_moods[1]}")
        
        # Genre/instrument hints based on content and mood
        genre_hint = self._get_genre_hint(caption, primary_mood)
        if genre_hint:
            prompt_parts.append(genre_hint)
        
        final_prompt = ", ".join(prompt_parts)
        self.logger.debug(f"Intelligent prompt created: {final_prompt}")
        
        return final_prompt
    
    def _get_genre_hint(self, caption: str, mood: str) -> str:
        """Add intelligent genre/instrument hints based on content"""
        caption_lower = caption.lower()
        mood_lower = mood.lower()
        
        # Nature scenes
        if any(word in caption_lower for word in ['forest', 'mountain', 'ocean', 'river', 'nature']):
            if mood_lower in ['peaceful', 'serene', 'calm']:
                return "ambient pads and gentle flutes"
            elif mood_lower in ['dramatic', 'intense']:
                return "epic orchestral strings and horns"
        
        # Urban scenes
        if any(word in caption_lower for word in ['city', 'building', 'street', 'urban']):
            if mood_lower in ['energetic', 'chaotic']:
                return "electronic beats and synth bass"
            elif mood_lower in ['melancholic', 'somber']:
                return "slow piano and distant city sounds"
        
        # People/portraits
        if any(word in caption_lower for word in ['person', 'people', 'portrait', 'face']):
            if mood_lower in ['happy', 'joyful']:
                return "upbeat acoustic guitar and light percussion"
            elif mood_lower in ['mysterious', 'dreamy']:
                return "ethereal vocals and reverbed textures"
        
        return ""

class SemanticSonifier:
    """
    Main Semantic Sonifier Class
    Professional orchestrator that converts images to music with emotional intelligence
    """
    
    def __init__(self):
        self.logger = logger.getChild("SemanticSonifier")
        self.image_analyzer = ImageAnalyzer()
        self.music_orchestrator = MusicOrchestrator()
        self._is_initialized = False
    
    def initialize(self):
        """Initialize all components"""
        if not self._is_initialized:
            self.logger.info("Initializing Semantic Sonifier...")
            # Models will be loaded on-demand to save memory
            self._is_initialized = True
            self.logger.info("✓ Semantic Sonifier initialized")
    
    def process_image(self, image_path: str, duration: Optional[int] = None) -> Dict[str, Any]:
        """
        Main pipeline: Convert image to music with emotional intelligence
        
        Args:
            image_path: Path to input image
            duration: Duration of generated music in seconds
            
        Returns:
            Complete processing results including audio and metadata
        """
        self.initialize()
        
        with TimingLogger("Semantic Sonification", self.logger):
            # Validate input
            if not Path(image_path).exists():
                raise FileNotFoundError(f"Image not found: {image_path}")
            
            # Step 1: Analyze image
            analysis_result = self.image_analyzer.safe_process(image_path)
            
            # Step 2: Generate music
            music_result = self.music_orchestrator.safe_process(
                analysis_result, 
                duration or config.audio.default_duration
            )
            
            # Combine results
            final_result = {**analysis_result, **music_result}
            
            self.logger.info(
                f"Successfully generated {final_result['duration_seconds']:.1f}s "
                f"of {analysis_result['primary_mood']} music for: {analysis_result['caption']}"
            )
            
            return final_result
    
    def batch_process(self, image_paths: list, duration: Optional[int] = None) -> list:
        """Process multiple images"""
        results = []
        for image_path in image_paths:
            try:
                result = self.process_image(image_path, duration)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Failed to process {image_path}: {e}")
                results.append(None)
        return results
    
    def unload_models(self):
        """Unload all models to free memory"""
        self.image_analyzer.unload_models()
        if self.music_orchestrator.music_generator:
            self.music_orchestrator.music_generator.unload_model()
        self.logger.info("All models unloaded")
    
    def __enter__(self):
        """Context manager support"""
        self.initialize()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager cleanup"""
        self.unload_models()
