import os
import shutil
import sys
from natsort import natsorted

def get_files_from_subfolders(parent_folder):
    all_files = []
    for root, dirs, files in os.walk(parent_folder):
        dirs[:] = natsorted(dirs)
        for j, file_name in enumerate(natsorted(files), start=1):
            file_path = os.path.join(root, file_name)
            all_files.append((file_path, os.path.relpath(root, parent_folder), j))
    return all_files

def move_and_rename_files(parent_folder, files):
    for file_path, rel_path, j in files:
        i = rel_path.replace(os.sep, '_')
        new_file_path = os.path.join(parent_folder, f'{i}_{j}' + os.path.splitext(file_path)[1])
        shutil.move(file_path, new_file_path)

def remove_empty_subfolders(parent_folder):
    for root, dirs, files in os.walk(parent_folder, topdown=False):
        for dir in natsorted(dirs):
            dir_path = os.path.join(root, dir)
            if os.path.isdir(dir_path) and not os.listdir(dir_path):
                os.rmdir(dir_path)

def reorganize_files(input_folder):
    for folder in natsorted(os.listdir(input_folder)):
        folder_path = os.path.join(input_folder, folder)
        if os.path.isdir(folder_path):
            files = get_files_from_subfolders(folder_path)
            move_and_rename_files(folder_path, files)
            remove_empty_subfolders(folder_path)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_folder = sys.argv[1]
        reorganize_files(input_folder)
        print("File Moving Complete!")
    else:
        print("Please provide the input folder path as an argument.")
