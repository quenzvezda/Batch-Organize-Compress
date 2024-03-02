import os
import subprocess
import sys

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

    # Ganti nama file sementara ke nama file asli'
    os.remove(output_video_path)
    os.rename(output_video_path + "_temp.mp4", output_video_path)

def convert_video(input_path, output_path, preset_file):
    """
    Konversi video menggunakan HandBrakeCLI dengan preset tertentu dan salin metadata.
    """
    # Tentukan jalur file metadata
    metadata_file = os.path.splitext(input_path)[0] + ".txt"
    
    try:
        # Ekstrak metadata dari video asli
        extract_metadata(input_path, metadata_file)
        
        # Konversi video menggunakan HandBrakeCLI
        command = [
            "HandBrakeCLI",
            "-i", input_path,
            "-o", output_path,
            "--preset-import-file", preset_file,
        ]
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT) 
        
        # Terapkan metadata ke video yang dikonversi
        apply_metadata(metadata_file, output_path)
        
        # Hapus file metadata
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
    video_files = [os.path.join(r, file) for r, d, files in os.walk(input_folder) for file in files if file.lower().endswith(('.mp4', '.avi', '.mov', '.mkv'))]
    total_videos = len(video_files)
    converted_videos = 0
    for input_path in video_files:
        converted_videos += 1
        relative_path = os.path.relpath(os.path.dirname(input_path), input_folder)
        current_output_folder = os.path.join(output_folder, relative_path)
        os.makedirs(current_output_folder, exist_ok=True)
        file_name = os.path.basename(input_path)
        output_path = os.path.join(current_output_folder, os.path.splitext(file_name)[0] + '.mp4')
        convert_video(input_path, output_path, preset_file)
        print(f'Converted {converted_videos}/{total_videos} videos: {file_name} -> {os.path.basename(output_path)}')