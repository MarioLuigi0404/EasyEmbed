import subprocess
import json

def get_stream_info(input_file):
    video = subprocess.run(
        [
            "ffprobe",
            "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=codec_name",
            "-of", "default=noprint_wrappers=1:nokey=1",
            input_file
        ],
        capture_output=True,
        text=True
    ).stdout.strip()

    audio = subprocess.run(
        [
            "ffprobe",
            "-v", "error",
            "-select_streams", "a:0",
            "-show_entries", "stream=codec_name",
            "-of", "default=noprint_wrappers=1:nokey=1",
            input_file
        ],
        capture_output=True,
        text=True
    ).stdout.strip()

    return video, audio