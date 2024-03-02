from PIL import Image
import os
import piexif

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

        # Coba ekstrak metadata EXIF, jika tidak ada, set ke None
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
    image_files = [os.path.join(r, file) for r, d, files in os.walk(input_folder) for file in files if file.lower().endswith(('.png', '.jpeg', '.jpg', '.bmp', '.gif'))]
    total_images = len(image_files)
    converted_images = 0
    for input_path in image_files:
        converted_images += 1
        relative_path = os.path.relpath(os.path.dirname(input_path), input_folder)
        current_output_folder = os.path.join(output_folder, relative_path)
        os.makedirs(current_output_folder, exist_ok=True)
        file_name = os.path.basename(input_path)
        output_path = os.path.join(current_output_folder, os.path.splitext(file_name)[0] + '.jpg')
        convert_image(input_path, output_path, quality, max_resolution)
        print(f'Converted images {converted_images} of {total_images} images: {file_name} -> {os.path.basename(output_path)}')