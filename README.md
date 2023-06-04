# Batch-Organize-Compress
A python script that is useful for organizing the file contents of a folder (especially media files). For example, if you have a lot of files in a subfolder, this script will move them to the parent folder. In addition to organizing, this script also compresses image and video media files, with minimal loss of quality.

To use this script you must install python, and install this library:

pip install pillow natsort

You must also download HandBrakeCLI if you want the video compression feature, add it to the System Variable "Path". But if you don't want to use the video compression feature, change "convert-encode.py" to "convert.py" in the "run.bat" file.

To adjust the image quality and resolution edit the file "convert*.py"
