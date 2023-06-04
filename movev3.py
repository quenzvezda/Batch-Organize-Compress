import os
import shutil
from natsort import natsorted

# fungsi untuk mendapatkan semua file dalam subfolder dan sub-subfolder
def get_files_from_subfolders(parent_folder):
    all_files = []
    for root, dirs, files in os.walk(parent_folder):
        dirs[:] = natsorted(dirs)
        for j, file_name in enumerate(natsorted(files), start=1):
            file_path = os.path.join(root, file_name)
            all_files.append((file_path, os.path.relpath(root, parent_folder), j))
    return all_files

# fungsi untuk memindahkan dan mengubah nama file
def move_and_rename_files(parent_folder, files):
    for file_path, rel_path, j in files:
        i = rel_path.replace(os.sep, '_')
        new_file_path = os.path.join(parent_folder, f'{i}_{j}' + os.path.splitext(file_path)[1])
        shutil.move(file_path, new_file_path)

# fungsi untuk menghapus subfolder kosong
def remove_empty_subfolders(parent_folder):
    for root, dirs, files in os.walk(parent_folder, topdown=False):
        for dir in natsorted(dirs):
            dir_path = os.path.join(root, dir)
            if os.path.isdir(dir_path) and not os.listdir(dir_path):
                os.rmdir(dir_path)

# fungsi utama
def main():
    for folder in natsorted(os.listdir('.')):
        if os.path.isdir(folder):
            files = get_files_from_subfolders(folder)
            move_and_rename_files(folder, files)
            remove_empty_subfolders(folder)

if __name__ == "__main__":
    main()

print("File Moving Complete!")