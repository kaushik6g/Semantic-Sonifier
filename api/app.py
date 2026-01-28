"""
FastAPI Backend for Semantic Sonifier Web Interface
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os
import uuid
from pathlib import Path
import numpy as np

from src.models.sonifier import SemanticSonifier
from src.utils.logging import logger, setup_logging

# Setup logging
setup_logging()

app = FastAPI(
    title="Semantic Sonifier API",
    description="AI system that converts images to music",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create directories
UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("outputs/web_audio")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

class SonifierService:
    def __init__(self):
        self.sonifier = None
    
    def get_sonifier(self):
        if self.sonifier is None:
            self.sonifier = SemanticSonifier()
            self.sonifier.initialize()
        return self.sonifier
    
    async def process_image(self, image_file: UploadFile, duration: int = 10):
        try:
            # Generate unique filename
            file_id = str(uuid.uuid4())
            image_path = UPLOAD_DIR / f"{file_id}_{image_file.filename}"
            audio_path = OUTPUT_DIR / f"{file_id}_generated.wav"
            
            # Save uploaded file
            with open(image_path, "wb") as buffer:
                content = await image_file.read()
                buffer.write(content)
            
            logger.info(f"Processing image: {image_file.filename}")
            
            # Process with semantic sonifier
            sonifier = self.get_sonifier()
            result = sonifier.process_image(str(image_path), duration)
            
            # Save audio file
            import scipy.io.wavfile as wavfile
            audio_normalized = result['audio_array'] / np.max(np.abs(result['audio_array']))
            wavfile.write(audio_path, result['sample_rate'], audio_normalized)
            
            # Cleanup uploaded image
            image_path.unlink()
            
            return {
                "success": True,
                "caption": result['caption'],
                "mood": result['primary_mood'],
                "prompt": result['prompt_used'],
                "duration": result['duration_seconds'],
                "audio_file": audio_path.name,
                "file_id": file_id
            }
            
        except Exception as e:
            logger.error(f"Processing failed: {e}")
            raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

# Global service instance
sonifier_service = SonifierService()

@app.get("/")
async def root():
    return {
        "message": "Semantic Sonifier API",
        "version": "1.0.0"
    }

@app.post("/process")
async def process_image(
    image: UploadFile = File(...),
    duration: int = 10
):
    allowed_types = ["image/jpeg", "image/png", "image/jpg"]
    if image.content_type not in allowed_types:
        raise HTTPException(
            status_code=400, 
            detail=f"File type {image.content_type} not supported. Use JPEG or PNG."
        )
    
    if duration < 1 or duration > 30:
        raise HTTPException(
            status_code=400,
            detail="Duration must be between 1 and 30 seconds"
        )
    
    return await sonifier_service.process_image(image, duration)

@app.get("/audio/{file_id}")
async def get_audio(file_id: str):
    audio_path = OUTPUT_DIR / f"{file_id}_generated.wav"
    
    if not audio_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    return FileResponse(
        path=audio_path,
        media_type='audio/wav',
        filename=f"sonified_{file_id}.wav"
    )

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "semantic_sonifier"}
