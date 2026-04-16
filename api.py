from fastapi import FastAPI, HTTPException, Header, UploadFile, File
import shutil
from pydantic import BaseModel
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware

from videoConverter.videoProcessing import processVideo

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


VIDEO_EXTENSIONS = {"mp4", "mov", "mkv", "avi", "webm", "m4v", "flv", "vob", "mts", "m2ts", "mpg", "mpeg", "mxf", "ts", "h264", "hevc", "yuv"}
IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "bmp", "tiff", "jxr", "svg", "webp", "heic", "avif", "jxl"}
SUPPORTED_EXTENSIONS = VIDEO_EXTENSIONS.union(IMAGE_EXTENSIONS)
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR = Path("processed")
OUTPUT_DIR.mkdir(exist_ok=True)

USER = { # Placeholder user for authentication testing
    "username": "admin",
    "password": "changeme"
}



class loginRequest(BaseModel):
    username: str
    password: str

@app.post("/login")
def login(request: loginRequest):
    if request.username == USER["username"] and request.password == USER["password"]:
        return {"token": "secret-token"}  # placeholder
    else:
        raise HTTPException(
            status_code=401, 
            detail="Invalid username or password"
            )



@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):

    #get file extension
    file_ext = file.filename.split(".")[-1].lower()

    # Validate file type
    if file_ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type: .{file_ext}"
            )

    # Save uploaded file to disk
    file_path = UPLOAD_DIR / file.filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Prepare request for processing
    processRequest = ConvertRequest(
        input_file=str(file_path),
        extended=False
    )

    # Call processing function
    convert(processRequest)

    # Delete original file after processing
    file_path.unlink(missing_ok=True)

    return {
        "filename": file.filename, 
        "status": "uploaded and processed"
        }



class ConvertRequest(BaseModel):
    input_file: str
    extended: bool # True for extended codec support


@app.post("/convert")
def convert(request: ConvertRequest):

    input_path = Path(request.input_file)
   
    # Get file extension
    ext = input_path.suffix[1:].lower()  # Get extension without dot
    
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