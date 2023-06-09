import os
import shutil
import subprocess
from PIL import Image
from PIL import UnidentifiedImageError
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
import ctypes

kernel32 = ctypes.windll.kernel32
kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

current_dir = os.path.dirname(os.path.abspath(__file__))

def convert_image(image_path, quality, resolution):
    try:
        img = Image.open(image_path)

        # If the image mode is not 'RGB', convert it to 'RGB'
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # Preserve Aspect Ratio (height to width ratio of image is preserved)
        img.thumbnail(resolution)

        # Save the image with reduced quality
        new_filename = image_path.split('.')[0] + "_converted.jpg"
        img.save(new_filename, "JPEG", optimize=True, quality=quality)
        return new_filename
    except UnidentifiedImageError:
        print(f"Unidentified image error: Cannot process image {image_path}")
        return ""
    except IOError:
        print(f"IOError: Cannot process image {image_path}")
        return ""

def compress_video(video_path, preset_file):
    output_filename = video_path.split('.')[0] + "_converted.mp4"
    command = f"HandBrakeCLI -i \"{video_path}\" -o \"{output_filename}\" --preset-import-file \"{preset_file}\" -Z \"H.265 NVEC 720p 35 Quality\" -e nvenc_h265"

    process = subprocess.run(command, shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
    if process.returncode != 0:
        print(f"HandBrakeCLI command failed for {video_path}. Return code: {process.returncode}, output: {process.stderr}")
        return ""
    return output_filename

def batch_convert(quality, resolution, preset_file):
    for folder_name, _, file_names in os.walk("."):
        for filename in file_names:
            file_path = os.path.join(folder_name, filename)
            if filename.endswith(('.mp4', '.mov', '.avi', '.mkv', '.MOV', '.MKV', '.MP4', '.AVI', '.TS', '.ts')):
                new_video_path = compress_video(file_path, preset_file)
                if new_video_path == "":
                    print(f"Skipping corrupted file in compress_video: {filename}")
                    continue
                new_folder_path = folder_name + " [converted]"
                if not os.path.exists(new_folder_path):
                    os.makedirs(new_folder_path)
                os.replace(new_video_path, os.path.join(new_folder_path, filename))
                print(f"\033[92mVideo Compress Success: {filename}\033[0m")
            else:
                new_image_path = convert_image(file_path, quality, resolution)
                if new_image_path == "":
                    print(f"Skipping corrupted file in convert_image: {filename}")
                    continue
                new_folder_path = folder_name + " [converted]"
                if not os.path.exists(new_folder_path):
                    os.makedirs(new_folder_path)
                os.replace(new_image_path, os.path.join(new_folder_path, filename))

# Change these values as needed
quality = 90
resolution = (2000, 2000)
preset_file = "NVEC-35.json"
batch_convert(quality, resolution, preset_file)
