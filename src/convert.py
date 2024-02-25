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
    for root, dirs, files in os.walk(input_folder):
        # Tentukan jalur folder output yang sesuai dengan struktur folder input
        relative_path = os.path.relpath(root, input_folder)
        current_output_folder = os.path.join(output_folder, relative_path)
        os.makedirs(current_output_folder, exist_ok=True)

        # Iterasi semua file dalam folder saat ini
        for file_name in files:
            input_path = os.path.join(root, file_name)
            output_path = os.path.join(current_output_folder, os.path.splitext(file_name)[0] + '.jpg')

            # Konversi gambar jika file merupakan file gambar
            if file_name.lower().endswith(('.png', '.jpeg', '.jpg', '.bmp', '.gif')):
                convert_image(input_path, output_path, quality, max_resolution)
                print(f'Converted: {file_name} -> {os.path.basename(output_path)}')