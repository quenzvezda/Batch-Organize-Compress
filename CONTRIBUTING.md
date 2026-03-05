# Contributing

Technical guide for developers who want to contribute to this project.

## Project Structure

```
Batch Rename - Mover/
├── src/
│   ├── main.py           # Entry point, Tkinter GUI (App class)
│   ├── console.py        # Shared Rich console & output helpers
│   ├── file_utils.py     # Shared utilities (collect_files, prepare_output_path)
│   ├── convert.py        # Image conversion (Pillow) + Rich progress bar
│   ├── convert_video.py  # Video conversion (HandBrakeCLI) + real-time progress
│   ├── move.py           # File reorganization (flatten subfolders)
│   ├── rename.py         # Batch file renaming
│   └── Complete.wav      # Sound notification asset
├── config/               # HandBrakeCLI preset files (.json)
├── input/                # Default input folder (gitignored)
├── output/               # Default output folder (gitignored)
├── install.bat           # Install Python dependencies
├── setup_handbrake.bat   # Auto-download & configure HandBrakeCLI
├── start.bat             # Launch the application
└── requirements.txt      # Python dependencies
```

## Architecture

### Processing Pipeline

```
Input Folder
  │
  ├─ [Convert]     → convert.py (images) + convert_video.py (videos) → temp/
  │                   or copy directly to temp/ if Convert is disabled
  │
  ├─ [Reorganize]  → move.py → flatten subfolders in temp/
  │
  ├─ [Rename]      → rename.py → rename files in temp/
  │
  └─ Move temp/ → Output Folder → Delete temp/
```

### Key Modules

| Module | Responsibility |
|---|---|
| `main.py` | GUI (Tkinter `App` class), orchestrates the processing pipeline in a background thread |
| `console.py` | Shared singleton `Console` instance with themed helpers (`print_header`, `print_step`, `print_success`, `print_error`) |
| `file_utils.py` | `collect_files(folder, extensions)` — walk & filter files; `prepare_output_path(...)` — mirror folder structure to output |
| `convert.py` | `convert_image()` — single image via Pillow; `batch_convert_images()` — batch with Rich progress |
| `convert_video.py` | `convert_video_with_progress()` — HandBrakeCLI with real-time stdout parsing; `batch_convert_videos()` — batch with nested Rich progress |
| `move.py` | Flatten nested subfolders, rename with `folder_index` pattern |
| `rename.py` | Sequential rename: `FolderName 1.ext`, `FolderName 2.ext`, etc. |

### HandBrakeCLI Progress Parsing

HandBrakeCLI outputs progress via `\r` carriage returns to stdout:
```
Encoding: task 1 of 1, 45.67 % (23.45 fps, avg 22.10 fps, ETA 00h02m30s)
```

This is captured by:
1. Running `subprocess.Popen` with `stdout=PIPE`
2. Reading stdout char-by-char to handle `\r` line updates
3. Parsing with regex: `r"Encoding:.*?(\d+\.\d+)\s*%"`
4. Feeding the percentage into a Rich progress bar

## Tech Stack

| Component | Technology |
|---|---|
| GUI | Tkinter |
| Terminal UI | [Rich](https://github.com/Textualize/rich) |
| Image conversion | [Pillow](https://python-pillow.org/) |
| Video conversion | [HandBrakeCLI](https://handbrake.fr/) |
| Video metadata | FFmpeg (`ffprobe` + `ffmpeg`) |
| File sorting | [natsort](https://github.com/SethMMorton/natsort) |

## Development Setup

```bash
# Clone & install
git clone <repo-url>
pip install -r requirements.txt

# Run
python src/main.py
```

## Code Conventions

- **Python naming**: `snake_case` for files, functions, and variables
- **Terminal output**: Always use helpers from `console.py`, never raw `print()`
- **File operations**: Use `file_utils.py` helpers for batch file collection and output path preparation
- **Progress bars**: Use `rich.progress.Progress` — see `convert.py` for a simple example, `convert_video.py` for nested progress
