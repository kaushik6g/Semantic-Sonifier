#!/usr/bin/env python3
"""
Test individual AI model components
"""

import sys
import os

# Add test image path
TEST_IMAGE = "src/data/test_images/test_image.jpg"  # You'll need to add an actual image

def test_individual_models():
    print("Testing Individual AI Models...")
    
    # Test BLIP-2
    try:
        from src.models.blip2_wrapper import BLIP2Model
        print("✓ BLIP2Model imported")
        
        with BLIP2Model() as blip:
            if os.path.exists(TEST_IMAGE):
                caption = blip.process(TEST_IMAGE)
                print(f"✓ BLIP-2 Caption: {caption}")
            else:
                print("⚠  No test image found - skipping caption test")
                
    except Exception as e:
        print(f"✗ BLIP-2 test failed: {e}")
    
    # Test CLIP Mood Analyzer
    try:
        from src.models.clip_mood_analyzer import CLIPMoodAnalyzer
        print("✓ CLIPMoodAnalyzer imported")
        
        with CLIPMoodAnalyzer() as clip:
            if os.path.exists(TEST_IMAGE):
                mood, scores = clip.process(TEST_IMAGE)
                print(f"✓ CLIP Mood: {mood}")
                print(f"✓ Mood Scores: {scores}")
            else:
                print("⚠  No test image found - skipping mood test")
                
    except Exception as e:
        print(f"✗ CLIP test failed: {e}")
    
    # Test Music Generator
    try:
        from src.models.music_generator import MusicGenerator
        print("✓ MusicGenerator imported")
        
        with MusicGenerator() as music_gen:
            # Test with simple prompt
            audio, sr = music_gen.process("A calm piano melody", duration=3)
            print(f"✓ MusicGen generated audio: {len(audio)} samples at {sr}Hz")
            
    except Exception as e:
        print(f"✗ MusicGen test failed: {e}")
    
    print("\\nIndividual model tests completed!")

if __name__ == "__main__":
    test_individual_models()
