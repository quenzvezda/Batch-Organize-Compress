import os
import shutil
import subprocess
from PIL import Image

current_dir = os.path.dirname(os.path.abspath(__file__))

def convert_image(image_path, quality, resolution):
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

def compress_video(video_path, preset_file):
    output_filename = video_path.split('.')[0] + "_converted.mp4"
    command = f"HandBrakeCLI -i \"{video_path}\" -o \"{output_filename}\" --preset-import-file \"{preset_file}\" -Z \"H.265 NVEC 720p 35 Quality\" -e nvenc_h265"
    subprocess.run(command, shell=True)
    return output_filename

def batch_convert(quality, resolution, preset_file):
    for foldername in os.listdir(current_dir):
        folder_path = os.path.join(current_dir, foldername)

        # ensure the path is a directory
        if os.path.isdir(folder_path):
            new_folder_path = folder_path + ' [Converted]'
            os.makedirs(new_folder_path, exist_ok=True)

            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.webp')):
                    new_image_path = convert_image(file_path, quality, resolution)
                    os.replace(new_image_path, os.path.join(new_folder_path, filename))
                elif filename.lower().endswith(('.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv', '.wmv', '.mkv')):
                    new_video_path = compress_video(file_path, preset_file)
                    os.replace(new_video_path, os.path.join(new_folder_path, filename))

# Change these values as needed
quality = 90
resolution = (2000, 2000)
preset_file = "NVEC-35.json"
batch_convert(quality, resolution, preset_file)
