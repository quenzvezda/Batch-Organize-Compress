import os
import time
import tkinter as tk
import winsound
import shutil
import threading
import json
from tkinter import filedialog
from move import reorganize_files
from rename import rename_files
from convert import batch_convert_images
from convert_video import batch_convert_videos
from console import console, print_header, print_step, print_success, print_error
from rich.panel import Panel
from rich.text import Text


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Batch Rename and Mover")

        # Paths
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.parent_dir = os.path.dirname(self.current_dir)
        self.input_folder_path = os.path.join(self.parent_dir, "input")
        self.output_folder_path = os.path.join(self.parent_dir, "output")
        os.makedirs(self.input_folder_path, exist_ok=True)
        os.makedirs(self.output_folder_path, exist_ok=True)

        # Variables
        self.reorganize_var = tk.IntVar(value=1)
        self.rename_var = tk.IntVar(value=1)
        self.convert_var = tk.IntVar(value=1)
        self.play_sound_var = tk.IntVar(value=1)
        self.shutdown_var = tk.IntVar(value=0)

        # Build UI
        self._build_folder_frame()
        self._build_checkbox_frame()
        self._build_settings_frame()
        self._build_options_frame()
        self._build_action_buttons()

    # ── UI Construction ──────────────────────────────────────────────

    def _build_folder_frame(self):
        frame = tk.Frame(self.root)
        frame.grid(row=0, column=0, columnspan=4, pady=(0, 10))

        # Input folder
        tk.Label(frame, text="Input Folder:").grid(row=0, column=0)
        self.input_folder_entry = tk.Entry(frame, width=50)
        self.input_folder_entry.grid(row=0, column=1)
        self.input_folder_entry.insert(0, self.input_folder_path)
        tk.Button(frame, text="Browse", command=self._browse_input_folder).grid(row=0, column=2)
        tk.Button(frame, text="Open", command=lambda: self._explore_folder(self.input_folder_entry.get())).grid(row=0, column=3)

        # Output folder
        tk.Label(frame, text="Output Folder:").grid(row=1, column=0)
        self.output_folder_entry = tk.Entry(frame, width=50)
        self.output_folder_entry.grid(row=1, column=1)
        self.output_folder_entry.insert(0, self.output_folder_path)
        tk.Button(frame, text="Browse", command=self._browse_output_folder).grid(row=1, column=2)
        tk.Button(frame, text="Open", command=lambda: self._explore_folder(self.output_folder_entry.get())).grid(row=1, column=3)

        # Preset file
        tk.Label(frame, text="Preset File:").grid(row=2, column=0)
        self.preset_file_entry = tk.Entry(frame, width=50)
        self.preset_file_entry.grid(row=2, column=1)
        self.preset_file_entry.insert(0, os.path.join(self.parent_dir, "config", "NVENC 1080p30 35Q.json"))
        tk.Button(frame, text="Browse", command=self._browse_preset_file).grid(row=2, column=2)

    def _build_checkbox_frame(self):
        frame = tk.Frame(self.root)
        frame.grid(row=1, column=0, columnspan=4, pady=(10, 10))

        tk.Checkbutton(frame, text="Re-organize", variable=self.reorganize_var).grid(row=0, column=0, padx=5, sticky='W')
        tk.Checkbutton(frame, text="Rename", variable=self.rename_var).grid(row=0, column=1, padx=5, sticky='W')
        tk.Checkbutton(frame, text="Convert", variable=self.convert_var).grid(row=0, column=2, padx=5, sticky='W')

    def _build_settings_frame(self):
        frame = tk.Frame(self.root)
        frame.grid(row=2, column=0, columnspan=4, pady=(0, 10))

        tk.Label(frame, text="Quality (0-100):").grid(row=0, column=0)
        self.quality_entry = tk.Entry(frame)
        self.quality_entry.grid(row=0, column=1)
        self.quality_entry.insert(0, "80")

        tk.Label(frame, text="Resolution (Width x Height):").grid(row=1, column=0)
        self.resolution_x_entry = tk.Entry(frame, width=10)
        self.resolution_x_entry.grid(row=1, column=1)
        self.resolution_x_entry.insert(0, "2000")

        tk.Label(frame, text="x").grid(row=1, column=2)

        self.resolution_y_entry = tk.Entry(frame, width=10)
        self.resolution_y_entry.grid(row=1, column=3)
        self.resolution_y_entry.insert(0, "2000")

    def _build_options_frame(self):
        frame = tk.Frame(self.root)
        frame.grid(row=3, column=0, columnspan=4, pady=(0, 10))

        tk.Checkbutton(frame, text="Play Sound When Finish", variable=self.play_sound_var).grid(row=0, column=0, padx=5, sticky='W')
        self.sound_repeat_entry = tk.Entry(frame, width=5)
        self.sound_repeat_entry.grid(row=0, column=1)
        self.sound_repeat_entry.insert(0, "1")
        tk.Label(frame, text="Times").grid(row=0, column=2)

        tk.Checkbutton(frame, text="Shutdown When Finish", variable=self.shutdown_var).grid(row=1, column=0, padx=5, sticky='W')
        self.shutdown_delay_entry = tk.Entry(frame, width=5)
        self.shutdown_delay_entry.grid(row=1, column=1)
        self.shutdown_delay_entry.insert(0, "1")
        tk.Label(frame, text="Minutes Delay").grid(row=1, column=2)

    def _build_action_buttons(self):
        tk.Button(self.root, text="Start Processing", command=self._start_processing).grid(row=4, column=1, pady=(10, 10), sticky="ew")

        self.cancel_shutdown_button = tk.Button(self.root, text="Cancel Shutdown", command=self._cancel_shutdown)
        self.cancel_shutdown_button.grid(row=5, column=1, pady=(10, 10), sticky="ew")
        self.cancel_shutdown_button.grid_remove()

    # ── Browse Dialogs ───────────────────────────────────────────────

    def _browse_input_folder(self):
        folder_path = filedialog.askdirectory(initialdir=self.input_folder_path)
        if folder_path:
            normalized_path = os.path.normpath(folder_path)
            self.input_folder_entry.delete(0, tk.END)
            self.input_folder_entry.insert(0, normalized_path)

    def _browse_output_folder(self):
        folder_path = filedialog.askdirectory(initialdir=self.output_folder_path)
        if folder_path:
            normalized_path = os.path.normpath(folder_path)
            self.output_folder_entry.delete(0, tk.END)
            self.output_folder_entry.insert(0, normalized_path)

    def _browse_preset_file(self):
        file_path = filedialog.askopenfilename(
            initialdir=os.path.join(self.parent_dir, "config"),
            filetypes=[("JSON files", "*.json")]
        )
        if file_path:
            normalized_path = os.path.normpath(file_path)
            self.preset_file_entry.delete(0, tk.END)
            self.preset_file_entry.insert(0, normalized_path)
            self._update_preset_default(normalized_path)

    # ── Actions ──────────────────────────────────────────────────────

    @staticmethod
    def _explore_folder(path):
        os.startfile(path)

    @staticmethod
    def _update_preset_default(preset_path):
        with open(preset_path, 'r') as f:
            data = json.load(f)
            for preset in data.get("PresetList", []):
                preset["Default"] = True

        with open(preset_path, 'w') as f:
            json.dump(data, f, indent=4)

    def _cancel_shutdown(self):
        os.system("shutdown -a")
        self.cancel_shutdown_button.grid_remove()

    def _start_processing(self):
        processing_thread = threading.Thread(target=self._process_files)
        processing_thread.start()

    def _count_steps(self):
        """Count active processing steps based on checkbox state."""
        steps = 0
        if self.convert_var.get() == 1:
            steps += 2  # images + videos
        if self.reorganize_var.get():
            steps += 1
        if self.rename_var.get():
            steps += 1
        return steps

    def _process_files(self):
        start_time = time.time()

        input_folder = self.input_folder_entry.get()
        output_folder = self.output_folder_entry.get()
        quality = int(self.quality_entry.get())
        resolution_x = int(self.resolution_x_entry.get())
        resolution_y = int(self.resolution_y_entry.get())
        resolution = (resolution_x, resolution_y)
        preset_file = self.preset_file_entry.get()

        temp_folder = os.path.join(self.parent_dir, "temp")
        total_steps = self._count_steps()
        current_step = 0

        # Header
        print_header("🚀 Batch Rename and Converter")

        if self.convert_var.get() == 1:
            current_step += 1
            print_step(current_step, total_steps, "Converting images...")
            batch_convert_images(input_folder, temp_folder, quality, resolution)

            current_step += 1
            print_step(current_step, total_steps, "Converting videos...")
            batch_convert_videos(input_folder, temp_folder, preset_file)
        else:
            shutil.copytree(input_folder, temp_folder, dirs_exist_ok=True)

        if self.reorganize_var.get():
            current_step += 1
            print_step(current_step, total_steps, "Reorganizing files...")
            reorganize_files(temp_folder)

        if self.rename_var.get():
            current_step += 1
            print_step(current_step, total_steps, "Renaming files...")
            rename_files(temp_folder)

        # Move results from temp folder to output folder
        for item in os.listdir(temp_folder):
            shutil.move(os.path.join(temp_folder, item), output_folder)

        shutil.rmtree(temp_folder)

        # Summary
        elapsed = time.time() - start_time
        minutes, seconds = divmod(int(elapsed), 60)
        hours, minutes = divmod(minutes, 60)
        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

        summary = Text.assemble(
            ("✓ Processing complete!\n", "bold green"),
            (f"  Total time: {time_str}", ""),
        )
        console.print()
        console.print(Panel(summary, border_style="green", padding=(1, 2)))

        # Post-processing options
        if self.play_sound_var.get() == 1:
            sound_repeat = int(self.sound_repeat_entry.get())
            for _ in range(sound_repeat):
                winsound.PlaySound(os.path.join(self.current_dir, 'Complete.wav'), winsound.SND_FILENAME)

        if self.shutdown_var.get() == 1:
            shutdown_delay = int(self.shutdown_delay_entry.get()) * 60
            os.system(f"shutdown /s /t {shutdown_delay}")
            self.cancel_shutdown_button.grid(row=4, column=2, pady=(10, 10), sticky="ew")


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
