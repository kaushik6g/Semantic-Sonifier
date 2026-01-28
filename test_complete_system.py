#!/usr/bin/env python3
"""
Test the complete Semantic Sonifier system
"""

import sys
import os
from pathlib import Path

def test_complete_system():
    print("Testing Complete Semantic Sonifier System...")
    
    # Create test image directory if it doesn't exist
    test_image_dir = Path("src/data/test_images")
    test_image_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if we have any test images
    test_images = list(test_image_dir.glob("*.jpg")) + list(test_image_dir.glob("*.png"))
    
    if not test_images:
        print("⚠  No test images found in src/data/test_images/")
        print("Please add some test images to continue testing")
        return
    
    try:
        from src.models.sonifier import SemanticSonifier
        print("✓ SemanticSonifier imported successfully")
        
        # Test the complete pipeline
        with SemanticSonifier() as sonifier:
            print("✓ Semantic Sonifier initialized")
            
            for i, image_path in enumerate(test_images[:2]):  # Test first 2 images
                print(f"\\n--- Processing Image {i+1}: {image_path.name} ---")
                
                try:
                    result = sonifier.process_image(str(image_path), duration=5)
                    
                    print(f"✓ Caption: {result['caption']}")
                    print(f"✓ Mood: {result['primary_mood']}")
                    print(f"✓ Prompt: {result['prompt_used']}")
                    print(f"✓ Audio: {len(result['audio_array'])} samples at {result['sample_rate']}Hz")
                    print(f"✓ Duration: {result['duration_seconds']:.1f}s")
                    
                    # Save the audio
                    output_dir = Path("outputs/audio")
                    output_dir.mkdir(parents=True, exist_ok=True)
                    
                    output_file = output_dir / f"{image_path.stem}_generated.wav"
                    
                    # Save as WAV file
                    from scipy.io import wavfile
                    audio_normalized = result['audio_array'] / np.max(np.abs(result['audio_array']))
                    wavfile.write(output_file, result['sample_rate'], audio_normalized)
                    
                    print(f"✓ Audio saved: {output_file}")
                    
                except Exception as e:
                    print(f"✗ Failed to process {image_path.name}: {e}")
        
        print("\\n🎉 Complete system test finished!")
        
    except Exception as e:
        print(f"✗ System test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_complete_system()
