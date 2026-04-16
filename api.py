from fastapi import FastAPI, Form, HTTPException, Header, UploadFile, File
import shutil
from pydantic import BaseModel
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
import uuid
import threading
from fastapi.staticfiles import StaticFiles

from videoConverter.videoProcessing import processVideo

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/media", StaticFiles(directory="processed"), name="media")

jobs = {}  # In-memory job store for tracking processing status

VIDEO_EXTENSIONS = {"mp4", "mov", "mkv", "avi", "webm", "m4v", "flv", "vob", "mts", "m2ts", "mpg", "mpeg", "mxf", "ts", "h264", "hevc", "yuv"}
IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "bmp", "tiff", "jxr", "svg", "webp", "heic", "avif", "jxl"}
SUPPORTED_EXTENSIONS = VIDEO_EXTENSIONS.union(IMAGE_EXTENSIONS)
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR = Path("processed") # I think I hardcoded this in the video processing function, may need to refactor to use this variable instead
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
async def upload_file(file: UploadFile = File(...), extended: bool = Form(False)):

    #get file extension
    file_ext = file.filename.split(".")[-1].lower()

    # Validate file type
    if file_ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type: .{file_ext}"
            )

    file_path = UPLOAD_DIR / file.filename

    job_id = str(uuid.uuid4())  # Generate unique job ID

    # Save uploaded file to disk
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Prepare request for processing
    processRequest = ConvertRequest(
        input_file=str(file_path),
        extended=extended
    )

    #init job state
    jobs[job_id] = {
        "staus": "queued",
        "progress": 0,
        "output": None
    }

    #start background processing thread
    threading.Thread(
        target=process_job,
        args=(job_id, processRequest, file_path)
    ).start()

    return {
        "job_id": job_id,
        }


# process job handling
def process_job(job_id: str, processRequest: ConvertRequest, file_path: Path):
    try:
        jobs[job_id]["status"] = "processing"
        jobs[job_id]["progress"] = 50

        # Call processing function
        convert(processRequest)
    
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["progress"] = 100

        # Delete original file after processing
        file_path.unlink(missing_ok=True)
    
    except Exception as e:
        jobs[job_id]["status"] = "error"
        jobs[job_id]["error"] = str(e)


@app.get("/status/{job_id}")
def get_status(job_id: str):
    return jobs.get(job_id, {"status": "not_found"})


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

def cleanup_uploads():
    for file in UPLOAD_DIR.glob("*"):
        try:
            file.unlink()
        except Exception as e:
            print(f"Failed to delete {file}: {e}")

@app.on_event("startup")
def startup_cleanup():
    print("Cleaning upload folder...")
    cleanup_uploads()

@app.get("/files")
def list_files():
    files = []
    for file in OUTPUT_DIR.glob("*"):
        files.append(file.name)
    return {"files": files}