from PIL import Image
import os
from file_utils import collect_files, prepare_output_path

IMAGE_EXTENSIONS = ('.png', '.jpeg', '.jpg', '.bmp', '.gif')


def convert_image(input_path, output_path, quality, max_resolution):
    """
    Konversi gambar ke format JPG dengan kualitas tertentu, mempertahankan aspek rasio,
    dan mempertahankan metadata EXIF.

    :param input_path: Jalur file gambar input.
    :param output_path: Jalur file gambar output.
    :param quality: Kualitas gambar output (0-100).
    :param max_resolution: Resolusi maksimum gambar output (lebar atau tinggi maksimum).
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
        print(f"Error processing image {input_path}: {e}")


def batch_convert_images(input_folder, output_folder, quality, max_resolution):
    """
    Konversi semua gambar dalam folder input ke folder output, termasuk subfolder,
    sambil mempertahankan aspect ratio.

    :param input_folder: Jalur folder input yang berisi gambar.
    :param output_folder: Jalur folder output untuk menyimpan gambar yang dikonversi.
    :param quality: Kualitas gambar output (0-100).
    :param max_resolution: Resolusi maksimum gambar output (lebar atau tinggi).
    """
    image_files = collect_files(input_folder, IMAGE_EXTENSIONS)
    total_images = len(image_files)

    for i, input_path in enumerate(image_files, start=1):
        output_path = prepare_output_path(input_path, input_folder, output_folder, '.jpg')
        convert_image(input_path, output_path, quality, max_resolution)
        file_name = os.path.basename(input_path)
        print(f'Converted {i}/{total_images} images: {file_name} -> {os.path.basename(output_path)}')