from ffmpeg import FFmpeg

def run_ffmpeg(input_file, output_file, settings):
    process = (
        FFmpeg()
        .option("y")
        .input(input_file)
        .output(output_file, settings)
    )
    process.execute()