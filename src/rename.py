import os
from natsort import natsorted

def rename_files(parent_folder):
    for folder_name in natsorted(os.listdir(parent_folder)):
        folder_path = os.path.join(parent_folder, folder_name)
        if os.path.isdir(folder_path):
            counter = 1
            for filename in natsorted(os.listdir(folder_path)):
                file_path = os.path.join(folder_path, filename)
                if os.path.isfile(file_path):
                    new_name = f"{folder_name} {counter}{os.path.splitext(filename)[1]}"
                    new_path = os.path.join(folder_path, new_name)
                    os.rename(file_path, new_path)
                    counter += 1
    print("File renaming complete!")

if __name__ == "__main__":
    parent_folder = os.path.dirname(os.path.abspath(__file__))
    rename_files(parent_folder)
