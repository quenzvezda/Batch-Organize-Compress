# Batch Rename and Converter

This project is an application for batch organizing, renaming, and converting image and video files. It uses Python for the backend and Tkinter for the user interface.

## Requirements

Before starting, make sure you have the following requirements:

- Python version 3.12 or higher.
- HandBrakeCLI (can be installed automatically, see below).

## Setup

1. **Install Python dependencies**: Run `install.bat` to install the required Python packages.
2. **Install HandBrakeCLI**: Run `setup_handbrake.bat` to automatically download and configure HandBrakeCLI.
   - Downloads the official binary from GitHub Releases.
   - Installs to `%LOCALAPPDATA%\HandBrakeCLI`.
   - Adds it to your User PATH automatically.
   - No admin rights required.

## How to Use

1. Open the application by running `start.bat`.
2. Select the input and output folders.
3. Set the desired quality and resolution for conversion.
4. Choose the operations you want to perform: Re-organize, Rename, Convert.
5. Click "Start Processing" to begin the process.
6. Optional: Enable "Play Sound When Finish" to get an audio notification after the process is complete.
7. Optional: Enable "Shutdown When Finish" to automatically shut down the computer after the process is complete.

## Features

- **File organization**: Group files into a neater folder structure.
- **File renaming**: Batch rename files according to a certain pattern.
- **File conversion**: Convert image and video files to the desired format with adjustable quality and resolution.
- **Audio notification**: Play a sound after the process is complete (optional).
- **Automatic shutdown**: Shut down the computer after the process is complete (optional).

## Contribution

Contributions are always welcome! Please fork this repository and create a pull request with your changes.
