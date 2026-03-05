import os
import re
import subprocess
from file_utils import collect_files, prepare_output_path
from console import print_success, print_error

VIDEO_EXTENSIONS = ('.mp4', '.avi', '.mov', '.mkv')

HANDBRAKE_PROGRESS_RE = re.compile(r"Encoding:.*?(\d+\.\d+)\s*%")
HANDBRAKE_ETA_RE = re.compile(r"ETA\s+(\d+h\d+m\d+s)")


def extract_metadata(input_path, metadata_file):
    command = [
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream_tags=creation_time",
        "-of", "default=nw=1:nk=1", input_path
    ]
    with open(metadata_file, "w") as file:
        subprocess.run(command, stdout=file, check=True, creationflags=subprocess.CREATE_NO_WINDOW)


def apply_metadata(metadata_file, output_video_path):
    with open(metadata_file, "r") as file:
        creation_time = file.readline().strip()

    command = [
        "ffmpeg", "-i", output_video_path, "-c", "copy",
        "-metadata", f"creation_time={creation_time}", "-y",
        output_video_path + "_temp.mp4"
    ]
    subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW)
    os.remove(output_video_path)
    os.rename(output_video_path + "_temp.mp4", output_video_path)


HANDBRAKE_STATS_RE = re.compile(r"(\d+\.\d+\s*fps).*?(ETA\s+\d+h\d+m\d+s)")

def convert_video_with_progress(input_path, output_path, preset_file,
                                status_callback=None, detail_progress_callback=None, stats_callback=None):
    metadata_file = os.path.splitext(input_path)[0] + ".txt"
    file_name = os.path.basename(input_path)

    try:
        extract_metadata(input_path, metadata_file)

        command = [
            "HandBrakeCLI", "-i", input_path, "-o", output_path,
            "--preset-import-file", preset_file,
        ]

        process = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            universal_newlines=True, bufsize=1,
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        buffer = ""
        for char in iter(lambda: process.stdout.read(1), ""):
            if char == "\r" or char == "\n":
                if buffer.strip():
                    match = HANDBRAKE_PROGRESS_RE.search(buffer)
                    if match:
                        percent = float(match.group(1)) / 100.0
                        if detail_progress_callback:
                            detail_progress_callback(percent)
                            
                        stats_match = HANDBRAKE_STATS_RE.search(buffer)
                        if stats_match and stats_callback:
                            fps = stats_match.group(1)
                            eta = stats_match.group(2)
                            stats_callback(f"{fps} | {eta}")

                        if status_callback:
                            status_callback(f"Encoding {file_name}")
                buffer = ""
            else:
                buffer += char

        process.wait()
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, command)

        if detail_progress_callback:
            detail_progress_callback(1.0)
        if stats_callback:
            stats_callback("Completed")

        apply_metadata(metadata_file, output_path)
        os.remove(metadata_file)

    except subprocess.CalledProcessError as e:
        print_error(f"Error converting video {input_path}: {e}")
        if status_callback:
            status_callback(f"Error converting {file_name}")


def batch_convert_videos(input_folder, output_folder, preset_file,
                         status_callback=None, progress_callback=None, detail_progress_callback=None, stats_callback=None):
    """
    Konversi semua video dalam folder input ke folder output.
    """
    video_files = collect_files(input_folder, VIDEO_EXTENSIONS)
    total_videos = len(video_files)

    if total_videos == 0:
        if status_callback:
            status_callback("No videos to convert.")
        print_success("No videos to convert.")
        return

    for i, input_path in enumerate(video_files, start=1):
        output_path = prepare_output_path(input_path, input_folder, output_folder, '.mp4')

        convert_video_with_progress(
            input_path, output_path, preset_file,
            status_callback, detail_progress_callback, stats_callback
        )
        print_success(f"Successfully converted: {os.path.basename(input_path)}")

        if progress_callback:
            progress_callback(i / total_videos)

    if status_callback:
        status_callback(f"Converted {total_videos} videos.")
    print_success(f"Converted {total_videos} videos.")
