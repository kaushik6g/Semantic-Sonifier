#!/usr/bin/env python3
"""
Test script to verify package installation
"""

def test_imports():
    try:
        import src
        print("✓ src package imported successfully")
        print(f"  Version: {src.__version__}")
        print(f"  Author: {src.__author__}")
        
        # Test subpackage imports
        import src.models
        import src.utils
        import src.data
        import src.evaluation
        print("✓ All subpackages imported successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing Semantic Sonifier package installation...")
    success = test_imports()
    if success:
        print("\n🎉 ALL TESTS PASSED! Package is ready for development.")
    else:
        print("\n❌ Some tests failed.")
