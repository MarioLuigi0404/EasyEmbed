import asyncio
from videoConverter.videoProcessing import processVideo

def main():
    input_file = input("Enter the path to the input video file: ").strip()
    file_name = input("Enter the name for the output video file (no extension): ").strip()
    extended_input = input("Use extended codec list? (y/n): ").strip().lower()

    is_extended = extended_input == 'y'

        # Transcode the video
    processVideo(input_file, file_name, is_extended)
    print(f"Processed video saved as {file_name}.mp4")

if __name__ == "__main__":
    main()