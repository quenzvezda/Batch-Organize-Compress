import os
import tkinter as tk
import winsound
import shutil
import threading
from tkinter import filedialog
from move import reorganize_files
from rename import rename_files
from src.convert import batch_convert_images
from convertVideo import batch_convert_videos
import json

def open_input_folder():
    folder_path = filedialog.askdirectory(initialdir=input_folder_path)
    if folder_path:  # Periksa apakah pengguna tidak membatalkan dialog
        normalized_path = os.path.normpath(folder_path)
        input_folder_entry.delete(0, tk.END)
        input_folder_entry.insert(0, normalized_path)

def open_output_folder():
    folder_path = filedialog.askdirectory(initialdir=output_folder_path)
    if folder_path:  # Periksa apakah pengguna tidak membatalkan dialog
        normalized_path = os.path.normpath(folder_path)
        output_folder_entry.delete(0, tk.END)
        output_folder_entry.insert(0, normalized_path)

def open_preset_file():
    file_path = filedialog.askopenfilename(initialdir=os.path.join(parent_dir, "config"), filetypes=[("JSON files", "*.json")])
    if file_path:  # Periksa apakah pengguna tidak membatalkan dialog
        normalized_path = os.path.normpath(file_path)
        preset_file_entry.delete(0, tk.END)
        preset_file_entry.insert(0, normalized_path)
        update_preset_default(normalized_path)
        
def update_preset_default(preset_path):
    with open(preset_path, 'r') as file:
        data = json.load(file)
        for preset in data.get("PresetList", []):
            preset["Default"] = True

    with open(preset_path, 'w') as file:
        json.dump(data, file, indent=4)
        
def open_input_folder():
    folder_path = filedialog.askdirectory(initialdir=input_folder_path)
    if folder_path:
        input_folder_entry.delete(0, tk.END)
        input_folder_entry.insert(0, folder_path)

def open_output_folder():
    folder_path = filedialog.askdirectory(initialdir=output_folder_path)
    if folder_path:
        output_folder_entry.delete(0, tk.END)
        output_folder_entry.insert(0, folder_path)

def open_preset_file():
    file_path = filedialog.askopenfilename(initialdir=os.path.join(parent_dir, "config"), filetypes=[("JSON files", "*.json")])
    if file_path:
        preset_file_entry.delete(0, tk.END)
        preset_file_entry.insert(0, file_path)

def explore_folder(path):
    os.startfile(path)
        
def cancel_shutdown():
    os.system("shutdown -a")
    cancel_shutdown_button.grid_remove()  # Sembunyikan tombol Cancel Shutdown

def process_files():
    input_folder = input_folder_entry.get()
    output_folder = output_folder_entry.get()
    quality = int(quality_entry.get())
    resolution_x = int(resolution_x_entry.get())
    resolution_y = int(resolution_y_entry.get())
    resolution = (resolution_x, resolution_y)
    preset_file = preset_file_entry.get()

    if convert_var.get() == 1:
        print("Converting images...")
        converted_folder = os.path.join(parent_dir, "temp")
        batch_convert_images(input_folder, converted_folder, quality, resolution)
        print("Converting videos...")
        batch_convert_videos(input_folder, converted_folder, preset_file)
    else:
        # Jika tidak ada konversi, salin isi input_folder ke temp_folder
        converted_folder = os.path.join(parent_dir, "temp")
        shutil.copytree(input_folder, converted_folder, dirs_exist_ok=True)

    if reorganize_var.get():
        print("Reorganizing files...")
        reorganize_files(converted_folder)

    if rename_var.get():
        print("Renaming files...")
        rename_files(converted_folder)

    # Pindahkan hasil dari temp folder ke output folder
    for item in os.listdir(converted_folder):
        shutil.move(os.path.join(converted_folder, item), output_folder)

    # Hapus folder temp
    shutil.rmtree(converted_folder)

    print("Processing complete!")

    # After Complete
    if play_sound_var.get() == 1:
        sound_repeat = int(sound_repeat_entry.get())
        for _ in range(sound_repeat):
            winsound.PlaySound(os.path.join(current_dir, 'Complete.wav'), winsound.SND_FILENAME)

    if shutdown_var.get() == 1:
        shutdown_delay = int(shutdown_delay_entry.get()) * 60  # Konversi menit ke detik
        os.system(f"shutdown /s /t {shutdown_delay}")
        cancel_shutdown_button.grid(row=4, column=2, pady=(10, 10), sticky="ew")

def start_processing():
    # Jalankan proses dalam thread terpisah
    processing_thread = threading.Thread(target=process_files)
    processing_thread.start()

root = tk.Tk()
root.title("Batch Rename and Mover")

# Dapatkan jalur folder induk dari main.py
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
# Pastikan folder input dan output ada
input_folder_path = os.path.join(parent_dir, "input")
output_folder_path = os.path.join(parent_dir, "output")
os.makedirs(input_folder_path, exist_ok=True)
os.makedirs(output_folder_path, exist_ok=True)

# Frame untuk Input, Output, dan Preset File
folder_frame = tk.Frame(root)
folder_frame.grid(row=0, column=0, columnspan=4, pady=(0, 10))

tk.Label(folder_frame, text="Input Folder:").grid(row=0, column=0)
input_folder_entry = tk.Entry(folder_frame, width=50)
input_folder_entry.grid(row=0, column=1)
input_folder_entry.insert(0, input_folder_path)
tk.Button(folder_frame, text="Browse", command=open_input_folder).grid(row=0, column=2)
tk.Button(folder_frame, text="Open", command=lambda: explore_folder(input_folder_entry.get())).grid(row=0, column=3)

tk.Label(folder_frame, text="Output Folder:").grid(row=1, column=0)
output_folder_entry = tk.Entry(folder_frame, width=50)
output_folder_entry.grid(row=1, column=1)
output_folder_entry.insert(0, output_folder_path)
tk.Button(folder_frame, text="Browse", command=open_output_folder).grid(row=1, column=2)
tk.Button(folder_frame, text="Open", command=lambda: explore_folder(output_folder_entry.get())).grid(row=1, column=3)

tk.Label(folder_frame, text="Preset File:").grid(row=2, column=0)
preset_file_entry = tk.Entry(folder_frame, width=50)
preset_file_entry.grid(row=2, column=1)
preset_file_entry.insert(0, os.path.join(parent_dir, "config", "NVEC-35.json"))  # Default value
tk.Button(folder_frame, text="Browse", command=open_preset_file).grid(row=2, column=2)

# Frame untuk Checkboxes
checkbox_frame = tk.Frame(root)
checkbox_frame.grid(row=1, column=0, columnspan=4, pady=(10, 10))

reorganize_var = tk.IntVar(value=1)
rename_var = tk.IntVar(value=1)
convert_var = tk.IntVar(value=1)

tk.Checkbutton(checkbox_frame, text="Re-organize", variable=reorganize_var).grid(row=0, column=0, padx=5, sticky='W')
tk.Checkbutton(checkbox_frame, text="Rename", variable=rename_var).grid(row=0, column=1, padx=5, sticky='W')
tk.Checkbutton(checkbox_frame, text="Convert", variable=convert_var).grid(row=0, column=2, padx=5, sticky='W')

# Frame untuk Quality dan Resolution
settings_frame = tk.Frame(root)
settings_frame.grid(row=2, column=0, columnspan=4, pady=(0, 10))

tk.Label(settings_frame, text="Quality (0-100):").grid(row=0, column=0)
quality_entry = tk.Entry(settings_frame)
quality_entry.grid(row=0, column=1)
quality_entry.insert(0, "80")  # Default value

tk.Label(settings_frame, text="Resolution (Width x Height):").grid(row=1, column=0)
resolution_x_entry = tk.Entry(settings_frame, width=10)
resolution_x_entry.grid(row=1, column=1)
resolution_x_entry.insert(0, "2000")  # Default width

tk.Label(settings_frame, text="x").grid(row=1, column=2)

resolution_y_entry = tk.Entry(settings_frame, width=10)
resolution_y_entry.grid(row=1, column=3)
resolution_y_entry.insert(0, "2000")  # Default height

# Di awal file main.py, setelah import
play_sound_var = tk.IntVar(value=1)  # Default tidak terceklis
shutdown_var = tk.IntVar(value=0)    # Default tidak terceklis

# Frame untuk Play Sound dan Shutdown
options_frame = tk.Frame(root)
options_frame.grid(row=3, column=0, columnspan=4, pady=(0, 10))

tk.Checkbutton(options_frame, text="Play Sound When Finish", variable=play_sound_var).grid(row=0, column=0, padx=5, sticky='W')
sound_repeat_entry = tk.Entry(options_frame, width=5)
sound_repeat_entry.grid(row=0, column=1)
sound_repeat_entry.insert(0, "1")  # Default value
tk.Label(options_frame, text="Times").grid(row=0, column=2)

tk.Checkbutton(options_frame, text="Shutdown When Finish", variable=shutdown_var).grid(row=1, column=0, padx=5, sticky='W')
shutdown_delay_entry = tk.Entry(options_frame, width=5)
shutdown_delay_entry.grid(row=1, column=1)
shutdown_delay_entry.insert(0, "1")  # Default value (1 menit)
tk.Label(options_frame, text="Minutes Delay").grid(row=1, column=2)

# Tombol Proses
start_processing_button = tk.Button(root, text="Start Processing", command=start_processing)
start_processing_button.grid(row=4, column=1, pady=(10, 10), sticky="ew")

# Tombol Cancel Shutdown
cancel_shutdown_button = tk.Button(root, text="Cancel Shutdown", command=cancel_shutdown)
cancel_shutdown_button.grid(row=5, column=1, pady=(10, 10), sticky="ew")
cancel_shutdown_button.grid_remove()  # Sembunyikan tombol pada awalnya

root.mainloop()