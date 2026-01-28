#!/usr/bin/env python3
"""
Demo script for Semantic Sonifier
"""

import argparse
from pathlib import Path
import sys

def main():
    parser = argparse.ArgumentParser(description="Semantic Sonifier - Convert images to music")
    parser.add_argument("image_path", help="Path to input image")
    parser.add_argument("--duration", type=int, default=10, help="Duration of generated music in seconds")
    parser.add_argument("--output", "-o", help="Output audio file path")
    
    args = parser.parse_args()
    
    # Validate input
    if not Path(args.image_path).exists():
        print(f"Error: Image not found: {args.image_path}")
        sys.exit(1)
    
    try:
        from src.models.sonifier import SemanticSonifier
        from src.utils.logging import logger
        
        print("🚀 Starting Semantic Sonifier...")
        print(f"Input: {args.image_path}")
        print(f"Duration: {args.duration}s")
        
        with SemanticSonifier() as sonifier:
            result = sonifier.process_image(args.image_path, args.duration)
            
            print(f"\\n🎨 Image Analysis:")
            print(f"   Caption: {result['caption']}")
            print(f"   Mood: {result['primary_mood']}")
            print(f"   Prompt: {result['prompt_used']}")
            
            # Determine output path
            if args.output:
                output_path = Path(args.output)
            else:
                output_dir = Path("outputs/audio")
                output_dir.mkdir(parents=True, exist_ok=True)
                input_stem = Path(args.image_path).stem
                output_path = output_dir / f"{input_stem}_sonified.wav"
            
            # Save audio
            from scipy.io import wavfile
            import numpy as np
            
            audio_normalized = result['audio_array'] / np.max(np.abs(result['audio_array']))
            wavfile.write(output_path, result['sample_rate'], audio_normalized)
            
            print(f"\\n🎵 Generated {result['duration_seconds']:.1f}s of music")
            print(f"💾 Saved to: {output_path}")
            print("\\n✅ Done!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
