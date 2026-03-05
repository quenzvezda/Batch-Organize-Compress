from PIL import Image
import os
from file_utils import collect_files, prepare_output_path
from console import print_success, print_error

IMAGE_EXTENSIONS = ('.png', '.jpeg', '.jpg', '.bmp', '.gif')


def convert_image(input_path, output_path, quality, max_resolution):
    """
    Konversi gambar ke format JPG dengan kualitas tertentu, mempertahankan aspek rasio,
    dan mempertahankan metadata EXIF.
    """
    try:
        img = Image.open(input_path)
        exif_data = img.info.get('exif', None)

        if img.mode != 'RGB':
            img = img.convert('RGB')

        img.thumbnail(max_resolution)

        save_args = {'format': 'JPEG', 'quality': quality, 'optimize': True}
        if exif_data:
            save_args['exif'] = exif_data

        img.save(output_path, **save_args)
    except Exception as e:
        print_error(f"Error processing image {input_path}: {e}")


def batch_convert_images(input_folder, output_folder, quality, max_resolution,
                         status_callback=None, progress_callback=None):
    """
    Konversi semua gambar dalam folder input ke folder output.
    """
    image_files = collect_files(input_folder, IMAGE_EXTENSIONS)
    total_images = len(image_files)

    if total_images == 0:
        if status_callback:
            status_callback("No images to convert.")
        print_success("No images to convert.")
        return

    for i, input_path in enumerate(image_files, start=1):
        file_name = os.path.basename(input_path)
        if status_callback:
            status_callback(f"Converting image: {file_name}")

        output_path = prepare_output_path(input_path, input_folder, output_folder, '.jpg')
        convert_image(input_path, output_path, quality, max_resolution)
        print_success(f"Successfully converted: {file_name}")

        if progress_callback:
            progress_callback(i / total_images)

    if status_callback:
        status_callback(f"Converted {total_images} images.")
    print_success(f"Converted {total_images} images.")