import os
import subprocess

def convert_video(input_path, output_path, preset_file):
    """
    Konversi video menggunakan HandBrakeCLI dengan preset tertentu.

    :param input_path: Jalur file video input.
    :param output_path: Jalur file video output.
    :param preset_file: Jalur file preset untuk HandBrakeCLI.
    """
    try:
        # Perintah untuk menjalankan HandBrakeCLI
        command = [
            "HandBrakeCLI",
            "-i", input_path,
            "-o", output_path,
            "--preset-import-file", preset_file,
        ]

        # Jalankan perintah konversi video
        subprocess.run(command, check=True)
        print(f"Converted: {input_path.encode('utf-8').decode('utf-8')} -> {output_path.encode('utf-8').decode('utf-8')}")
    except subprocess.CalledProcessError as e:
        print(f"Error converting video {input_path}: {e}")

def batch_convert_videos(input_folder, output_folder, preset_file):
    """
    Konversi semua video dalam folder input ke folder output, termasuk subfolder.

    :param input_folder: Jalur folder input yang berisi video.
    :param output_folder: Jalur folder output untuk menyimpan video yang dikonversi.
    :param preset_file: Jalur file preset untuk HandBrakeCLI.
    """
    for root, dirs, files in os.walk(input_folder):
        # Tentukan jalur folder output yang sesuai dengan struktur folder input
        relative_path = os.path.relpath(root, input_folder)
        current_output_folder = os.path.join(output_folder, relative_path)
        os.makedirs(current_output_folder, exist_ok=True)

        # Iterasi semua file dalam folder saat ini
        for file_name in files:
            input_path = os.path.join(root, file_name)
            output_path = os.path.join(current_output_folder, os.path.splitext(file_name)[0] + '.mp4')

            # Konversi video jika file merupakan file video
            if file_name.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
                convert_video(input_path, output_path, preset_file)