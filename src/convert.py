import os
import shutil
import subprocess
from PIL import Image
from PIL import UnidentifiedImageError
from PIL import ImageFile
import ctypes
import winsound
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

def convert_image(image_path, quality, resolution):
    try:
        img = Image.open(image_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        img.thumbnail(resolution)
        
        # Membersihkan nama file
        sanitized_filename = sanitize_filename(os.path.basename(image_path))
        new_filename = os.path.join(os.path.dirname(image_path), sanitized_filename.split('.')[0] + "_converted.jpg")

        try:
            exif_data = piexif.load(img.info['exif'])
            exif_bytes = piexif.dump(exif_data)
            img.save(new_filename, "JPEG", optimize=True, quality=quality, exif=exif_bytes)
        except KeyError:
            img.save(new_filename, "JPEG", optimize=True, quality=quality)

        return new_filename
    except UnidentifiedImageError:
        print(f"Unidentified image error: Cannot process image {image_path}")
        return ""
    except IOError:
        print(f"IOError: Cannot process image {image_path}")
        return ""
    except Exception as e:
        print(f"Error: {e} - Cannot process image {image_path}")
        return ""

def compress_video(video_path, preset_file):
    output_filename = video_path.split('.')[0] + "_converted.mp4"
    metadata_filename = video_path.split('.')[0] + "_metadata.txt"

    # Ekstrak metadata dari video asli
    subprocess.run(f"ffmpeg -i \"{video_path}\" -map_metadata 0 -f ffmetadata \"{metadata_filename}\"", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Kompresi video menggunakan HandBrakeCLI
    command = f"HandBrakeCLI -i \"{video_path}\" -o \"{output_filename}\" --preset-import-file \"{preset_file}\" -Z \"H.265 NVEC 720p 35 Quality\" -e nvenc_h265"
    process = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8', errors='ignore')
    print(process.stdout)  # Cetak output dari HandBrakeCLI

    if process.returncode != 0:
        print(f"HandBrakeCLI command failed for {video_path}. Return code: {process.returncode}, output: {process.stderr}")
        return ""

    # Tambahkan kembali metadata ke video yang dikompresi
    subprocess.run(f"ffmpeg -i \"{output_filename}\" -i \"{metadata_filename}\" -map_metadata 1 -codec copy \"{output_filename}_with_metadata.mp4\"", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Hapus file metadata sementara
    os.remove(metadata_filename)
    
    os.remove(output_filename)

    return output_filename + "_with_metadata.mp4"


def batch_convert(input_folder, output_folder, quality, resolution, preset_file):
    for folder_name, _, file_names in os.walk(input_folder):
        for filename in file_names:
            file_path = os.path.join(folder_name, filename)
            if filename.endswith(('.mp4', '.mov', '.avi', '.mkv', '.MOV', '.MKV', '.MP4', '.AVI', '.TS', '.ts', '.m4v', '.M4V')):
                new_video_path = compress_video(file_path, preset_file)
                if new_video_path != "":
                    # Tentukan lokasi folder tujuan berdasarkan struktur folder asli
                    relative_path = os.path.relpath(folder_name, input_folder)
                    destination_folder = os.path.join(output_folder, relative_path)
                    os.makedirs(destination_folder, exist_ok=True)
                    shutil.move(new_video_path, os.path.join(destination_folder, os.path.basename(new_video_path)))
            else:
                new_image_path = convert_image(file_path, quality, resolution)
                if new_image_path != "":
                    # Tentukan lokasi folder tujuan berdasarkan struktur folder asli
                    relative_path = os.path.relpath(folder_name, input_folder)
                    destination_folder = os.path.join(output_folder, relative_path)
                    os.makedirs(destination_folder, exist_ok=True)
                    shutil.move(new_image_path, os.path.join(destination_folder, os.path.basename(new_image_path)))



# Change these values as needed
# quality = 80
# resolution = (2000, 2000)
# preset_file = "NVEC-35.json"
# batch_convert(quality, resolution, preset_file)

# print(f"All conversion finished, playing sound files now")
# for i in range(10):
#     winsound.PlaySound('Complete.wav', winsound.SND_FILENAME)