import os
import shutil
from PIL import Image

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
        return None

def batch_convert(quality, resolution, preset_file):
    for foldername in os.listdir(current_dir):
        folder_path = os.path.join(current_dir, foldername)

        # ensure the path is a directory
        if os.path.isdir(folder_path):
            new_folder_path = folder_path + ' [converted]'
            os.makedirs(new_folder_path, exist_ok=True)

            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)
                if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    new_image_path = convert_image(file_path, quality, resolution)
                    if new_image_path is not None:
                        os.replace(new_image_path, os.path.join(new_folder_path, filename))
                elif filename.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')):
                    new_video_path = compress_video(file_path, preset_file)
                    os.replace(new_video_path, os.path.join(new_folder_path, filename))

# Change these values as needed
quality = 90
resolution = (2000, 2000)
batch_convert(quality, resolution)
