import os
import re
import subprocess
from file_utils import collect_files, prepare_output_path
from console import console, print_success, print_error
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, MofNCompleteColumn, TimeRemainingColumn, TaskProgressColumn

VIDEO_EXTENSIONS = ('.mp4', '.avi', '.mov', '.mkv')

# Regex to parse HandBrakeCLI progress output:
#   "Encoding: task 1 of 1, 45.67 % (23.45 fps, avg 22.10 fps, ETA 00h02m30s)"
HANDBRAKE_PROGRESS_RE = re.compile(r"Encoding:.*?(\d+\.\d+)\s*%")
HANDBRAKE_ETA_RE = re.compile(r"ETA\s+(\d+h\d+m\d+s)")


def extract_metadata(input_path, metadata_file):
    """
    Ekstrak metadata "media created" dari video input dan simpan ke file txt.
    """
    command = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream_tags=creation_time",
        "-of", "default=nw=1:nk=1",
        input_path
    ]
    with open(metadata_file, "w") as file:
        subprocess.run(command, stdout=file, check=True)


def apply_metadata(metadata_file, output_video_path):
    """
    Terapkan metadata "media created" dari file txt ke video output.
    """
    with open(metadata_file, "r") as file:
        creation_time = file.readline().strip()

    command = [
        "ffmpeg",
        "-i", output_video_path,
        "-c", "copy",
        "-metadata", f"creation_time={creation_time}",
        "-y",
        output_video_path + "_temp.mp4"
    ]
    subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

    os.remove(output_video_path)
    os.rename(output_video_path + "_temp.mp4", output_video_path)


def convert_video_with_progress(input_path, output_path, preset_file, progress, file_task):
    """
    Konversi video menggunakan HandBrakeCLI, parsing real-time progress dari stdout.
    """
    metadata_file = os.path.splitext(input_path)[0] + ".txt"

    try:
        # Ekstrak metadata dari video asli
        extract_metadata(input_path, metadata_file)

        # Konversi video — capture stdout for progress
        command = [
            "HandBrakeCLI",
            "-i", input_path,
            "-o", output_path,
            "--preset-import-file", preset_file,
        ]

        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1,
        )

        # Read output character by character to handle \r updates
        buffer = ""
        for char in iter(lambda: process.stdout.read(1), ""):
            if char == "\r" or char == "\n":
                if buffer.strip():
                    match = HANDBRAKE_PROGRESS_RE.search(buffer)
                    if match:
                        percent = float(match.group(1))
                        # Extract ETA if available
                        eta_match = HANDBRAKE_ETA_RE.search(buffer)
                        eta_str = f" • ETA {eta_match.group(1)}" if eta_match else ""
                        file_name = os.path.basename(input_path)
                        progress.update(
                            file_task,
                            completed=percent,
                            description=f"  ┗ [cyan]{file_name}[/cyan]{eta_str}",
                        )
                buffer = ""
            else:
                buffer += char

        process.wait()
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, command)

        # Mark file progress as complete
        progress.update(file_task, completed=100)

        # Terapkan metadata ke video yang dikonversi
        apply_metadata(metadata_file, output_path)

        # Hapus file metadata sementara
        os.remove(metadata_file)

    except subprocess.CalledProcessError as e:
        print_error(f"Error converting video {input_path}: {e}")


def batch_convert_videos(input_folder, output_folder, preset_file):
    """
    Konversi semua video dalam folder input ke folder output, termasuk subfolder.

    :param input_folder: Jalur folder input yang berisi video.
    :param output_folder: Jalur folder output untuk menyimpan video yang dikonversi.
    :param preset_file: Jalur file preset untuk HandBrakeCLI.
    """
    video_files = collect_files(input_folder, VIDEO_EXTENSIONS)
    total_videos = len(video_files)

    if total_videos == 0:
        print_success("No videos to convert.")
        return

    with Progress(
        SpinnerColumn(),
        TextColumn("{task.description}"),
        BarColumn(bar_width=30),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        overall_task = progress.add_task(
            f"[bold blue]Converting videos", total=total_videos
        )

        for input_path in video_files:
            output_path = prepare_output_path(input_path, input_folder, output_folder, '.mp4')
            file_name = os.path.basename(input_path)

            # Sub-task for per-file percentage
            file_task = progress.add_task(
                f"  ┗ [cyan]{file_name}[/cyan]", total=100
            )

            convert_video_with_progress(input_path, output_path, preset_file, progress, file_task)

            # Clean up file sub-task and advance overall
            progress.remove_task(file_task)
            progress.update(overall_task, advance=1)

    print_success(f"Converted {total_videos} videos.")
