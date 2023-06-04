# Batch-Organize-Compress
A python script that is useful for organizing the file contents of a folder (especially media files). For example, if you have a lot of files in a subfolder, this script will move them to the parent folder. In addition to organizing, this script also compresses image and video media files, with minimal loss of quality.

To use this script you must install python, and install this library:

pip install pillow natsort

You must also download HandBrakeCLI if you want the video compression feature, add it to the System Variable "Path". Replace "NVEC-35.JSON" with your handbrake preset. The result of the image and video compression is in "[input folder name] Converted".
I recommend using an NVIDIA GPU, but if you don't have an NVIDIA GPU you will need to change the "command" in the "convert-encode.py".
But if you don't want to use the video compression feature, change "convert-encode.py" to "convert.py" in the "run.bat" file.

To use this script you need to put the folder and script in the same directory. Then start "run.bat".
To adjust the image quality and resolution edit the file "convert*.py"

Please be careful when using this script, any changes made cannot be undone.
