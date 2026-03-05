import os
import subprocess
from file_utils import collect_files, prepare_output_path

VIDEO_EXTENSIONS = ('.mp4', '.avi', '.mov', '.mkv')


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


def convert_video(input_path, output_path, preset_file):
    """
    Konversi video menggunakan HandBrakeCLI dengan preset tertentu dan salin metadata.
    """
    metadata_file = os.path.splitext(input_path)[0] + ".txt"

    try:
        extract_metadata(input_path, metadata_file)

        command = [
            "HandBrakeCLI",
            "-i", input_path,
            "-o", output_path,
            "--preset-import-file", preset_file,
        ]
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

        apply_metadata(metadata_file, output_path)

        os.remove(metadata_file)

        print(f"Converted: {os.path.basename(input_path)} -> {os.path.basename(output_path)}")
    except subprocess.CalledProcessError as e:
        print(f"Error converting video {input_path}: {e}")


def batch_convert_videos(input_folder, output_folder, preset_file):
    """
    Konversi semua video dalam folder input ke folder output, termasuk subfolder.

    :param input_folder: Jalur folder input yang berisi video.
    :param output_folder: Jalur folder output untuk menyimpan video yang dikonversi.
    :param preset_file: Jalur file preset untuk HandBrakeCLI.
    """
    video_files = collect_files(input_folder, VIDEO_EXTENSIONS)
    total_videos = len(video_files)

    for i, input_path in enumerate(video_files, start=1):
        output_path = prepare_output_path(input_path, input_folder, output_folder, '.mp4')
        convert_video(input_path, output_path, preset_file)
        file_name = os.path.basename(input_path)
        print(f'Converted {i}/{total_videos} videos: {file_name} -> {os.path.basename(output_path)}')
