# Batch Rename and Converter

An application for batch organizing, renaming, and converting image and video files.

## ✨ Features

- **File organization** — Group files into a cleaner folder structure
- **File renaming** — Batch rename files following a specific pattern
- **File conversion** — Convert images & videos with adjustable quality and resolution
- **Audio notification** — Play a sound when processing is complete (optional)
- **Auto shutdown** — Automatically shut down the computer after processing (optional)

## 📋 Requirements

- Python 3.12 or higher
- HandBrakeCLI (can be installed automatically, see Setup)

## 🚀 Setup

1. **Install dependencies** — Run `install.bat`
2. **Install HandBrakeCLI** — Run `setup_handbrake.bat`
   - Automatically downloads the official release
   - Installs & adds to PATH automatically
   - No admin rights required

## 📖 How to Use

1. Launch the application by running `start.bat`
2. Select the **Input** (source) and **Output** (destination) folders
3. Set the desired **Quality** and **Resolution** for conversion
4. Check the operations you want to perform: **Re-organize**, **Rename**, **Convert**
5. Click **Start Processing**

### Additional Options

| Option | Description |
|---|---|
| Play Sound When Finish | Play a notification sound after completion |
| Shutdown When Finish | Automatically shut down the PC after completion (configurable delay) |

## 🔧 Troubleshooting

| Issue | Solution |
|---|---|
| `HandBrakeCLI` not found | Run `setup_handbrake.bat`, then restart your terminal |
| Module not found error | Run `install.bat` again |
| Video conversion fails | Make sure the preset JSON file in `config/` is valid |

## 🤝 Contributing

Contributions are always welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for technical details about the project.
