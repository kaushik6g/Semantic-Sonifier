#!/usr/bin/env python3
"""
Test the configuration system
"""

from src.utils.config import config, save_config

print("Testing Configuration System...")
print(f"Project: {config.project_name} v{config.version}")
print(f"BLIP-2 Model: {config.models.blip2_model}")
print(f"MusicGen Model: {config.models.musicgen_model}")
print(f"Audio Sample Rate: {config.audio.sample_rate}")
print(f"Mood Tags: {config.models.mood_tags[:5]}...")

# Save configuration to file
save_config("test_config.yaml")
print("✓ Configuration saved to test_config.yaml")

# Test loading
from src.utils.config import load_config
loaded_config = load_config("test_config.yaml")
print("✓ Configuration loaded successfully")
