"""Web application for uploading gym screenshots from mobile devices."""

import logging
import socket
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List

from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse, JSONResponse
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

def get_local_ip():
    """Get the local IP address of this machine."""
    try:
        # Use ifconfig to get actual network interfaces (works on macOS/Linux)
        result = subprocess.run(
            ["ifconfig"], 
            capture_output=True, 
            text=True, 
            timeout=2
        )
        
        # Parse ifconfig output for inet addresses
        for line in result.stdout.split('\n'):
            line = line.strip()
            if line.startswith('inet '):
                parts = line.split()
                if len(parts) >= 2:
                    ip = parts[1]
                    # Return first 192.168.x.x address found
                    if ip.startswith('192.168.'):
                        return ip
                    # Also accept 10.x.x.x or 172.16-31.x.x if no 192.168 found
                    if ip.startswith('10.') or ip.startswith('172.'):
                        # Store as fallback but keep looking for 192.168
                        if 'fallback_ip' not in locals():
                            fallback_ip = ip
        
        # Use fallback if we found one
        if 'fallback_ip' in locals():
            return fallback_ip
            
    except Exception:
        pass
    
    # Fallback to socket method
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "YOUR_LOCAL_IP"

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
    local_ip = get_local_ip()
    
    log.info(f"")
    log.info(f"🚀 Gym Screenshot Upload Server Started!")
    log.info(f"=" * 60)
    log.info(f"")
    log.info(f"📱 Open this URL on your iPhone:")
    log.info(f"   ➜  http://{local_ip}:{port}")
    log.info(f"")
    log.info(f"💾 Upload directory: {UPLOAD_DIR.absolute()}")
    log.info(f"")
    log.info(f"💡 Make sure your iPhone is on the same WiFi network!")
    log.info(f"")
    log.info(f"=" * 60)
    
    uvicorn.run(app, host=host, port=port, log_level="warning")

if __name__ == "__main__":
    start_server()
