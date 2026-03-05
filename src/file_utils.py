import os


def collect_files(input_folder, extensions):
    """
    Walk through input_folder recursively and collect all files matching
    the given extensions.

    :param input_folder: Root folder to search.
    :param extensions: Tuple of file extensions to match (e.g. ('.png', '.jpg')).
    :return: List of absolute file paths.
    """
    return [
        os.path.join(root, file)
        for root, dirs, files in os.walk(input_folder)
        for file in files
        if file.lower().endswith(extensions)
    ]


def prepare_output_path(input_path, input_folder, output_folder, new_ext):
    """
    Build the output file path mirroring the input folder structure,
    creating intermediate directories as needed.

    :param input_path: Absolute path of the source file.
    :param input_folder: Root input folder.
    :param output_folder: Root output folder.
    :param new_ext: New file extension including dot (e.g. '.jpg').
    :return: Absolute path for the output file.
    """
    relative_path = os.path.relpath(os.path.dirname(input_path), input_folder)
    current_output_folder = os.path.join(output_folder, relative_path)
    os.makedirs(current_output_folder, exist_ok=True)
    file_name = os.path.basename(input_path)
    return os.path.join(current_output_folder, os.path.splitext(file_name)[0] + new_ext)
