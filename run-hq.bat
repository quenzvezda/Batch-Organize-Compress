@echo off

rem Menjalankan skrip movev3.py
echo Menjalankan movev3.py...
python movev3.py

rem Menjalankan skrip rename.py
echo Menjalankan rename.py...
python rename.py

rem Menjalankan skrip convert.py
echo Menjalankan convert-encode-v2.py...
python convert-encode-v2.py

rem Menampilkan pesan selesai
echo Semua Skrip Selesai dijalankan.
pause >nul

rem Menutup jendela Command Prompt
exit
