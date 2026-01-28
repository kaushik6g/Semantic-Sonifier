#!/usr/bin/env python3
"""
Test all imports to identify any remaining issues
"""

imports_to_test = [
    "src.utils.config",
    "src.utils.logging", 
    "src.models.base",
    "src.models.blip2_wrapper",
    "src.models.clip_mood_analyzer",
    "src.models.music_generator",
    "src.models.sonifier",
    "src.api.app"
]

print("Testing all imports...")

for import_path in imports_to_test:
    try:
        __import__(import_path)
        print(f"✓ {import_path}")
    except ImportError as e:
        print(f"✗ {import_path}: {e}")
    except Exception as e:
        print(f"⚠ {import_path}: {e}")

print("\nImport test completed!")
