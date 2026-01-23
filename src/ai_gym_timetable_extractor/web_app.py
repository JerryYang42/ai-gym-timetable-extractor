"""Web application for uploading gym screenshots from mobile devices."""

import os
import logging
from pathlib import Path
from datetime import datetime
from typing import List

from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Gym Screenshot Uploader")

# Setup directories
UPLOAD_DIR = Path("data/img")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

TEMPLATES_DIR = Path(__file__).parent / "templates"
TEMPLATES_DIR.mkdir(exist_ok=True)

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

@app.get("/", response_class=HTMLResponse)
async def upload_page(request: Request):
    """Main upload page optimized for mobile."""
    return templates.TemplateResponse("upload.html", {"request": request})

@app.post("/upload")
async def upload_photos(files: List[UploadFile] = File(...)):
    """Handle photo uploads from mobile device.
    
    Args:
        files: List of uploaded image files
        
    Returns:
        JSON response with upload results
    """
    uploaded_files = []
    errors = []
    
    for file in files:
        try:
            # Validate file type
            if not file.content_type or not file.content_type.startswith('image/'):
                errors.append(f"{file.filename}: Not an image file")
                continue
            
            # Generate unique filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            original_name = file.filename or "screenshot.jpg"
            ext = Path(original_name).suffix or ".jpg"
            new_filename = f"gym_{timestamp}{ext}"
            
            # Save file
            save_path = UPLOAD_DIR / new_filename
            content = await file.read()
            
            with open(save_path, "wb") as f:
                f.write(content)
            
            uploaded_files.append({
                "original": original_name,
                "saved_as": new_filename,
                "size": len(content)
            })
            log.info(f"✓ Uploaded: {new_filename} ({len(content)} bytes)")
            
        except Exception as e:
            error_msg = f"{file.filename}: {str(e)}"
            errors.append(error_msg)
            log.error(f"✗ Upload failed: {error_msg}")
    
    return JSONResponse({
        "success": len(uploaded_files),
        "failed": len(errors),
        "files": uploaded_files,
        "errors": errors
    })

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "upload_dir": str(UPLOAD_DIR.absolute()),
        "total_files": len(list(UPLOAD_DIR.glob("*")))
    }

def start_server(host: str = "0.0.0.0", port: int = 8000):
    """Start the web upload server.
    
    Args:
        host: Host to bind to (0.0.0.0 for all interfaces)
        port: Port number
    """
    log.info(f"🚀 Starting Gym Screenshot Upload Server")
    log.info(f"📱 Open on your iPhone: http://YOUR_LOCAL_IP:{port}")
    log.info(f"💾 Upload directory: {UPLOAD_DIR.absolute()}")
    log.info(f"")
    log.info(f"To find your local IP:")
    log.info(f"  Mac: ifconfig | grep 'inet ' | grep -v 127.0.0.1")
    log.info(f"  Or: System Preferences → Network")
    
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    start_server()