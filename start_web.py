#!/usr/bin/env python3
"""
Start the Streamlit web interface
"""

import subprocess
import sys

def main():
    print("🌐 Starting Semantic Sonifier Web Interface...")
    print("📱 Open: http://localhost:8501")
    subprocess.run([sys.executable, "-m", "streamlit", "run", "src/web/app.py"])
    
if __name__ == "__main__":
    main()
