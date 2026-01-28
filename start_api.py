#!/usr/bin/env python3
"""
Start the FastAPI server
"""

import uvicorn

if __name__ == "__main__":
    print("🚀 Starting Semantic Sonifier API Server...")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🛑 Press Ctrl+C to stop the server")
    
    uvicorn.run(
        "src.api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes
        log_level="info"
    )
