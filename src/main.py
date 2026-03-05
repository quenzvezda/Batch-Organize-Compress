import os
import time
import winsound
import shutil
import threading
import json
import customtkinter as ctk
from tkinter import filedialog
from move import reorganize_files
from rename import rename_files
from convert import batch_convert_images
from convert_video import batch_convert_videos
from console import print_header, print_step, print_success

# Set CustomTkinter theme
ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Batch Rename and Converter")
        # Set window size and prevent resizing for cleaner look
        self.geometry("700x650")
        self.resizable(False, False)

        # Paths
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.parent_dir = os.path.dirname(self.current_dir)
        self.input_folder_path = os.path.join(self.parent_dir, "input")
        self.output_folder_path = os.path.join(self.parent_dir, "output")
        os.makedirs(self.input_folder_path, exist_ok=True)
        os.makedirs(self.output_folder_path, exist_ok=True)

        # Variables
        self.reorganize_var = ctk.IntVar(value=1)
        self.rename_var = ctk.IntVar(value=1)
        self.convert_var = ctk.IntVar(value=1)
        self.play_sound_var = ctk.IntVar(value=1)
        self.shutdown_var = ctk.IntVar(value=0)

        # Build UI
        self._build_header()
        self._build_folder_frame()
        self._build_checkbox_frame()
        self._build_settings_frame()
        self._build_options_frame()
        self._build_action_buttons()
        self._build_progress_frame()

    # ── UI Construction ──────────────────────────────────────────────

    def _build_header(self):
        header = ctk.CTkLabel(self, text="Batch Rename & Converter", font=ctk.CTkFont(size=24, weight="bold"))
        header.pack(pady=(20, 10))

    def _build_folder_frame(self):
        frame = ctk.CTkFrame(self)
        frame.pack(padx=20, pady=10, fill="x")

        # Input folder
        ctk.CTkLabel(frame, text="Input Folder:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.input_folder_entry = ctk.CTkEntry(frame, width=350)
        self.input_folder_entry.grid(row=0, column=1, padx=10, pady=10)
        self.input_folder_entry.insert(0, self.input_folder_path)
        ctk.CTkButton(frame, text="Browse", width=80, command=self._browse_input_folder).grid(row=0, column=2, padx=(0, 5))
        ctk.CTkButton(frame, text="Open", width=60, fg_color="gray", hover_color="dim gray",
                      command=lambda: self._explore_folder(self.input_folder_entry.get())).grid(row=0, column=3, padx=(0, 10))

        # Output folder
        ctk.CTkLabel(frame, text="Output Folder:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.output_folder_entry = ctk.CTkEntry(frame, width=350)
        self.output_folder_entry.grid(row=1, column=1, padx=10, pady=10)
        self.output_folder_entry.insert(0, self.output_folder_path)
        ctk.CTkButton(frame, text="Browse", width=80, command=self._browse_output_folder).grid(row=1, column=2, padx=(0, 5))
        ctk.CTkButton(frame, text="Open", width=60, fg_color="gray", hover_color="dim gray",
                      command=lambda: self._explore_folder(self.output_folder_entry.get())).grid(row=1, column=3, padx=(0, 10))

        # Preset file
        ctk.CTkLabel(frame, text="Preset File:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.preset_file_entry = ctk.CTkEntry(frame, width=350)
        self.preset_file_entry.grid(row=2, column=1, padx=10, pady=10)
        self.preset_file_entry.insert(0, os.path.join(self.parent_dir, "config", "NVENC 1080p30 35Q.json"))
        ctk.CTkButton(frame, text="Browse", width=80, command=self._browse_preset_file).grid(row=2, column=2, padx=(0, 5))

    def _build_checkbox_frame(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(padx=20, pady=5, fill="x")

        ctk.CTkCheckBox(frame, text="Re-organize", variable=self.reorganize_var).pack(side="left", padx=(10, 20))
        ctk.CTkCheckBox(frame, text="Rename", variable=self.rename_var).pack(side="left", padx=20)
        ctk.CTkCheckBox(frame, text="Convert", variable=self.convert_var).pack(side="left", padx=20)

    def _build_settings_frame(self):
        frame = ctk.CTkFrame(self)
        frame.pack(padx=20, pady=10, fill="x")

        # Quality
        ctk.CTkLabel(frame, text="Quality (0-100):").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.quality_entry = ctk.CTkEntry(frame, width=60)
        self.quality_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        self.quality_entry.insert(0, "80")

        # Resolution
        ctk.CTkLabel(frame, text="Resolution:").grid(row=0, column=2, padx=10, pady=10, sticky="w")
        self.resolution_x_entry = ctk.CTkEntry(frame, width=60)
        self.resolution_x_entry.grid(row=0, column=3, padx=5, pady=10)
        self.resolution_x_entry.insert(0, "2000")

        ctk.CTkLabel(frame, text="x").grid(row=0, column=4, padx=5, pady=10)

        self.resolution_y_entry = ctk.CTkEntry(frame, width=60)
        self.resolution_y_entry.grid(row=0, column=5, padx=5, pady=10)
        self.resolution_y_entry.insert(0, "2000")

    def _build_options_frame(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(padx=20, pady=5, fill="x")

        # Sound
        ctk.CTkCheckBox(frame, text="Play Sound", variable=self.play_sound_var).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.sound_repeat_entry = ctk.CTkEntry(frame, width=40)
        self.sound_repeat_entry.grid(row=0, column=1, padx=5, pady=5)
        self.sound_repeat_entry.insert(0, "1")
        ctk.CTkLabel(frame, text="Times").grid(row=0, column=2, padx=5, pady=5, sticky="w")

        # Shutdown
        ctk.CTkCheckBox(frame, text="Shutdown When Finish", variable=self.shutdown_var).grid(row=0, column=3, padx=(30, 10), pady=5, sticky="w")
        self.shutdown_delay_entry = ctk.CTkEntry(frame, width=40)
        self.shutdown_delay_entry.grid(row=0, column=4, padx=5, pady=5)
        self.shutdown_delay_entry.insert(0, "1")
        ctk.CTkLabel(frame, text="Min Delay").grid(row=0, column=5, padx=5, pady=5, sticky="w")

    def _build_action_buttons(self):
        # We use a frame to place buttons side-by-side
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(padx=20, pady=(15, 5), fill="x")

        self.start_processing_button = ctk.CTkButton(
            frame, text="START PROCESSING", 
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40, command=self._start_processing
        )
        self.start_processing_button.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.open_logs_button = ctk.CTkButton(
            frame, text="Open Logs", 
            font=ctk.CTkFont(size=12),
            height=40, width=100, fg_color="gray", hover_color="dim gray",
            command=self._open_logs
        )
        self.open_logs_button.pack(side="right")

        self.cancel_shutdown_button = ctk.CTkButton(
            self, text="Cancel Shutdown", 
            fg_color="#D32F2F", hover_color="#B71C1C",
            command=self._cancel_shutdown
        )
        # Pack later when needed

    def _build_progress_frame(self):
        self.progress_frame = ctk.CTkFrame(self)
        self.progress_frame.pack(padx=20, pady=10, fill="x")

        # Top row: Status Label
        self.status_label = ctk.CTkLabel(self.progress_frame, text="Ready", font=ctk.CTkFont(weight="bold"))
        self.status_label.pack(pady=(10, 5), padx=10, anchor="w")

        # Second row: Overall Progress
        self.overall_progress = ctk.CTkProgressBar(self.progress_frame)
        self.overall_progress.pack(padx=10, pady=5, fill="x")
        self.overall_progress.set(0)

        # Third row: Detail Progress and Stats
        detail_frame = ctk.CTkFrame(self.progress_frame, fg_color="transparent")
        detail_frame.pack(padx=10, pady=(5, 10), fill="x")

        self.detail_progress = ctk.CTkProgressBar(detail_frame, progress_color="#10B981") # Greenish
        self.detail_progress.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.detail_progress.set(0)

        self.stats_label = ctk.CTkLabel(detail_frame, text="", font=ctk.CTkFont(size=11), width=120, anchor="e")
        self.stats_label.pack(side="right")

    # ── Browse Dialogs ───────────────────────────────────────────────

    def _browse_input_folder(self):
        folder_path = filedialog.askdirectory(initialdir=self.input_folder_path)
        if folder_path:
            normalized_path = os.path.normpath(folder_path)
            self.input_folder_entry.delete(0, 'end')
            self.input_folder_entry.insert(0, normalized_path)

    def _browse_output_folder(self):
        folder_path = filedialog.askdirectory(initialdir=self.output_folder_path)
        if folder_path:
            normalized_path = os.path.normpath(folder_path)
            self.output_folder_entry.delete(0, 'end')
            self.output_folder_entry.insert(0, normalized_path)

    def _browse_preset_file(self):
        file_path = filedialog.askopenfilename(
            initialdir=os.path.join(self.parent_dir, "config"),
            filetypes=[("JSON files", "*.json")]
        )
        if file_path:
            normalized_path = os.path.normpath(file_path)
            self.preset_file_entry.delete(0, 'end')
            self.preset_file_entry.insert(0, normalized_path)
            self._update_preset_default(normalized_path)

    # ── Callbacks for Thread Updates ─────────────────────────────────

    def _update_status(self, text):
        # the .after method safely updates the GUI from a background thread
        self.after(0, lambda: self.status_label.configure(text=text))

    def _update_overall_progress(self, percent):
        self.after(0, lambda: self.overall_progress.set(percent))

    def _update_detail_progress(self, percent):
        self.after(0, lambda: self.detail_progress.set(percent))
        
    def _update_stats(self, text):
        self.after(0, lambda: self.stats_label.configure(text=text))

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
        self.cancel_shutdown_button.pack_forget()
        self._update_status("Shutdown cancelled.")
        
    def _open_logs(self):
        log_file = os.path.join(self.parent_dir, "logs", "app.log")
        if os.path.exists(log_file):
            os.startfile(log_file)
        else:
            self._update_status("Log file not found yet.")

    def _start_processing(self):
        self.start_processing_button.configure(state="disabled")
        self.overall_progress.set(0)
        self.detail_progress.set(0)
        
        processing_thread = threading.Thread(target=self._process_files)
        processing_thread.start()

    def _count_steps(self):
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

        # Optional Terminal Output for logging
        print_header("Batch Rename and Converter UI Running")

        if self.convert_var.get() == 1:
            current_step += 1
            print_step(current_step, total_steps, "Converting images...")
            self._update_detail_progress(0) # Hide/reset detail bar
            
            # Convert Images
            batch_convert_images(
                input_folder, temp_folder, quality, resolution,
                status_callback=self._update_status,
                progress_callback=self._update_overall_progress
            )

            current_step += 1
            print_step(current_step, total_steps, "Converting videos...")
            
            # Convert Videos
            batch_convert_videos(
                input_folder, temp_folder, preset_file,
                status_callback=self._update_status,
                progress_callback=self._update_overall_progress,
                detail_progress_callback=self._update_detail_progress,
                stats_callback=self._update_stats
            )
            self._update_stats("")  # Clear stats after video conversion
        else:
            self._update_status("Copying files...")
            shutil.copytree(input_folder, temp_folder, dirs_exist_ok=True)

        self._update_detail_progress(0) # Reset detail bar for remaining non-detail steps

        if self.reorganize_var.get():
            current_step += 1
            print_step(current_step, total_steps, "Reorganizing files...")
            self._update_overall_progress(current_step / total_steps)
            reorganize_files(temp_folder, status_callback=self._update_status)

        if self.rename_var.get():
            current_step += 1
            print_step(current_step, total_steps, "Renaming files...")
            self._update_overall_progress(current_step / total_steps)
            rename_files(temp_folder, status_callback=self._update_status)

        # Move results from temp folder to output folder
        self._update_status("Finalizing output...")
        for item in os.listdir(temp_folder):
            shutil.move(os.path.join(temp_folder, item), output_folder)

        shutil.rmtree(temp_folder)

        # Summary
        elapsed = time.time() - start_time
        minutes, seconds = divmod(int(elapsed), 60)
        time_str = f"{minutes:02d}:{seconds:02d}"

        self._update_status(f"✓ Processing complete in {time_str}!")
        self._update_overall_progress(1.0)
        
        # Restore Start Button in GUI thread
        self.after(0, lambda: self.start_processing_button.configure(state="normal"))
        print_success("Processing complete.")

        # Post-processing options
        if self.play_sound_var.get() == 1:
            sound_repeat = int(self.sound_repeat_entry.get())
            for _ in range(sound_repeat):
                winsound.PlaySound(os.path.join(self.current_dir, 'Complete.wav'), winsound.SND_FILENAME)

        if self.shutdown_var.get() == 1:
            shutdown_delay = int(self.shutdown_delay_entry.get()) * 60
            os.system(f"shutdown /s /t {shutdown_delay}")
            self.after(0, lambda: self.cancel_shutdown_button.pack(padx=20, pady=5, fill="x"))


if __name__ == "__main__":
    app = App()
    app.mainloop()
