from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path

from videoConverter.videoProcessing import processVideo

app = FastAPI()

VIDEO_EXTENSIONS = {"mp4", "mov", "mkv", "avi", "webm", "m4v", "flv", "vob", "mts", "m2ts", "mpg", "mpeg", "mxf", "ts", "h264", "hevc", "yuv"}
IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "bmp", "tiff", "jxr", "svg", "webp", "heic", "avif", "jxl"}
SUPPORTED_EXTENSIONS = VIDEO_EXTENSIONS.union(IMAGE_EXTENSIONS)

class ConvertRequest(BaseModel):
    input_file: str
    extended: bool # True for extended codec support


@app.post("/convert")
def convert(request: ConvertRequest):

    input_path = Path(request.input_file)

    # Validate file exists
    if not input_path.is_file():
        raise HTTPException(
            status_code=400, 
            detail="Input file does not exist"
            )
    
    # Validate file extension
    ext = input_path.suffix[1:].lower()  # Get extension without dot

    if ext not in SUPPORTED_EXTENSIONS: ### update this to support images as well once the image processing is implemented
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: .{ext}"
            )
    
    output_name = input_path.stem  # Get filename without extension

    if ext in VIDEO_EXTENSIONS:
        processVideo(
            request.input_file, 
            output_name, 
            request.extended
        )
    elif ext in IMAGE_EXTENSIONS:
        print("Image handling is not yet implemented") # Placeholder for image processing function
        pass
    
    
    return {"status": "done"}