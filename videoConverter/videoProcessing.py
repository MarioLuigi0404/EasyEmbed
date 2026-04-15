import asyncio
from videoConverter.ffmpegRunner import run_ffmpeg
from videoConverter.utils import get_stream_info
import json

with open("videoConverter/transcode_config.json", "r") as config_file:
    config = json.load(config_file)

def processVideo(input_file, file_name, is_extended=False):

    v_codec, a_codec = get_stream_info(input_file)

    video_settings = choose_video_settings(v_codec, is_extended)
    audio_settings = choose_audio_settings(a_codec, is_extended)

    settings = merge_settings(video_settings, audio_settings)

    run_ffmpeg(input_file, f"uploads/{file_name}.mp4", settings)


def choose_video_settings(codec, is_extended):
    if is_extended and codec in config["extended_codecs"]["video"]:
        print(f"Video codec '{codec}' is in the extended list. Using remux settings.")
        return config["video_remux"]
    elif codec in config["safe_codecs"]["video"]:
        print(f"Video codec '{codec}' is in the safe list. Using remux settings.")
        return config["video_remux"]
    print(f"Video codec '{codec}' is not supported. Using transcode settings.")
    return config["video_transcode"]


def choose_audio_settings(codec, is_extended):
    if is_extended and codec in config["extended_codecs"]["audio"]:
        print(f"Audio codec '{codec}' is in the extended list. Using remux settings.")
        return config["audio_remux"]
    elif codec in config["safe_codecs"]["audio"]:
        print(f"Audio codec '{codec}' is in the safe list. Using remux settings.")
        return config["audio_remux"]
    print(f"Audio codec '{codec}' is not supported. Using transcode settings.")
    return config["audio_transcode"]

def merge_settings(video_settings, audio_settings):
    settings = {}
    settings.update(video_settings)
    settings.update(audio_settings)
    return settings