"""
Configuration Management for Semantic Sonifier
"""

import os
from dataclasses import dataclass
from typing import Dict, List, Optional
import yaml

@dataclass
class ModelConfig:
    """Configuration for AI models"""
    blip2_model: str = "Salesforce/blip2-opt-2.7b"
    clip_model: str = "openai/clip-vit-base-patch32"
    musicgen_model: str = "facebook/musicgen-small"
    device: str = "auto"
    torch_dtype: str = "float16"
    
    # Mood analysis
    mood_tags: tuple = (
        "serene", "happy", "melancholic", "energetic", "peaceful", 
        "chaotic", "mysterious", "romantic", "dramatic", "calm",
        "joyful", "somber", "intense", "light", "dark", "dreamy"
    )

@dataclass
class AudioConfig:
    """Configuration for audio generation"""
    sample_rate: int = 32000
    default_duration: int = 10
    max_duration: int = 30
    output_format: str = "wav"

@dataclass
class EvaluationConfig:
    """Configuration for evaluation metrics"""
    clap_model: str = "laion/clap-htsat-unfused"
    emotion_models: Dict = None
    
    def __post_init__(self):
        if self.emotion_models is None:
            self.emotion_models = {
                "image": "miccunifi/emotic",
                "audio": "music-emotion"
            }

@dataclass
class ProjectConfig:
    """Main configuration class"""
    project_name: str = "semantic-sonifier"
    version: str = "0.1.0"
    models: ModelConfig = None
    audio: AudioConfig = None
    evaluation: EvaluationConfig = None
    
    def __post_init__(self):
        if self.models is None:
            self.models = ModelConfig()
        if self.audio is None:
            self.audio = AudioConfig()
        if self.evaluation is None:
            self.evaluation = EvaluationConfig()
    
    @classmethod
    def from_yaml(cls, config_path: str) -> 'ProjectConfig':
        """Load configuration from YAML file"""
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config_dict = yaml.safe_load(f)
            return cls(**config_dict)
        else:
            return cls()

# Global configuration instance
config = ProjectConfig()

def save_config(config_path: str = "config.yaml"):
    """Save current configuration to YAML file"""
    config_dict = {
        'project_name': config.project_name,
        'version': config.version,
        'models': {
            'blip2_model': config.models.blip2_model,
            'clip_model': config.models.clip_model,
            'musicgen_model': config.models.musicgen_model,
            'device': config.models.device,
            'torch_dtype': config.models.torch_dtype,
            'mood_tags': list(config.models.mood_tags)
        },
        'audio': {
            'sample_rate': config.audio.sample_rate,
            'default_duration': config.audio.default_duration,
            'max_duration': config.audio.max_duration,
            'output_format': config.audio.output_format
        }
    }
    
    with open(config_path, 'w') as f:
        yaml.dump(config_dict, f, default_flow_style=False)
    
    print(f"Configuration saved to {config_path}")

def load_config(config_path: str = "config.yaml"):
    """Load configuration from YAML file"""
    global config
    config = ProjectConfig.from_yaml(config_path)
    return config
