import os
import shutil
import subprocess
from PIL import Image
from PIL import UnidentifiedImageError
from PIL import ImageFile
import ctypes
import piexif

kernel32 = ctypes.windll.kernel32
kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

ImageFile.LOAD_TRUNCATED_IMAGES = True

current_dir = os.path.dirname(os.path.abspath(__file__))

import os
import re

def sanitize_filename(filename):
    # Menghilangkan spasi di awal nama file
    filename = filename.lstrip()
    # Mengganti karakter ilegal dengan underscore
    filename = re.sub(r'[^a-zA-Z0-9_.-]', '_', filename)
    return filename

def convert_image(image_path, input_folder, output_folder, quality, resolution):
    try:
        img = Image.open(image_path)

        # Jika mode gambar bukan 'RGB', konversi ke 'RGB'
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # Pertahankan Rasio Aspek
        img.thumbnail(resolution)

        # Tentukan lokasi folder tujuan berdasarkan struktur folder asli
        relative_path = os.path.relpath(os.path.dirname(image_path), input_folder)
        destination_folder = os.path.join(output_folder, relative_path)
        os.makedirs(destination_folder, exist_ok=True)

        # Nama file baru untuk gambar yang dikonversi
        new_filename = os.path.join(destination_folder, os.path.splitext(os.path.basename(image_path))[0] + ".jpg")

        # Coba baca metadata EXIF dari gambar asli
        try:
            exif_data = piexif.load(img.info['exif'])
            # Konversi metadata EXIF kembali ke format binary
            exif_bytes = piexif.dump(exif_data)
            # Simpan gambar dengan kualitas yang berkurang dan metadata EXIF
            img.save(new_filename, "JPEG", optimize=True, quality=quality, exif=exif_bytes)
        except KeyError:
            # Jika tidak ada data EXIF, simpan gambar tanpa metadata EXIF
            img.save(new_filename, "JPEG", optimize=True, quality=quality)

        return new_filename
    except UnidentifiedImageError:
        print(f"Unidentified image error: Cannot process image {image_path}")
        return ""
    except IOError:
        print(f"IOError: Cannot process image {image_path}")
        return ""


def compress_video(video_path, input_folder, output_folder, preset_file):
    output_filename = os.path.basename(video_path).split('.')[0] + ".mp4"
    metadata_filename = os.path.join(os.path.dirname(video_path), os.path.basename(video_path).split('.')[0] + "_metadata.txt")

    # Ekstrak metadata dari video asli
    subprocess.run(f"ffmpeg -i \"{video_path}\" -map_metadata 0 -f ffmetadata \"{metadata_filename}\"", shell=True, capture_output=True)

    # Kompresi video menggunakan HandBrakeCLI
    command = f"HandBrakeCLI -i \"{video_path}\" -o \"{output_filename}\" --preset-import-file \"{preset_file}\" -Z \"H.265 NVEC 720p 35 Quality\" -e nvenc_h265"
    process = subprocess.run(command, shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
    if process.returncode != 0:
        print(f"HandBrakeCLI command failed for {video_path}. Return code: {process.returncode}, output: {process.stderr}")
        return ""

    # Tambahkan kembali metadata ke video yang dikompresi
    subprocess.run(f"ffmpeg -i \"{output_filename}\" -i \"{metadata_filename}\" -map_metadata 1 -codec copy \"{output_filename}.mp4\"", shell=True, capture_output=True)

    # Hapus file metadata sementara dan sementara output file
    os.remove(metadata_filename)
    os.remove(output_filename)

    # Menentukan lokasi output berdasarkan struktur asli
    relative_path = os.path.relpath(os.path.dirname(video_path), input_folder)
    destination_folder = os.path.join(output_folder, relative_path)
    os.makedirs(destination_folder, exist_ok=True)
    final_output_filename = os.path.join(destination_folder, os.path.basename(video_path).split('.')[0] + "_converted_with_metadata.mp4")

    # Pindahkan file video yang sudah dikonversi
    shutil.move(output_filename + "_with_metadata.mp4", final_output_filename)

    return final_output_filename

def batch_convert(input_folder, output_folder, quality, resolution, preset_file):
    for folder_name, _, file_names in os.walk(input_folder):
        for filename in file_names:
            file_path = os.path.join(folder_name, filename)
            if filename.endswith(('.mp4', '.mov', '.avi', '.mkv', '.MOV', '.MKV', '.MP4', '.AVI', '.TS', '.ts', '.m4v', '.M4V')):
                # Perhatikan penambahan input_folder sebagai parameter
                new_video_path = compress_video(file_path, input_folder, output_folder, preset_file)
                if new_video_path != "":
                    pass
            else:
                # Perhatikan penambahan input_folder sebagai parameter
                new_image_path = convert_image(file_path, input_folder, output_folder, quality, resolution)
                if new_image_path != "":
                    pass