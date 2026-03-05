@echo off
setlocal EnableDelayedExpansion

:: ── Configuration ───────────────────────────────────────────────
set "VERSION=1.10.2"
set "DOWNLOAD_URL=https://github.com/HandBrake/HandBrake/releases/download/%VERSION%/HandBrakeCLI-%VERSION%-win-x86_64.zip"
set "INSTALL_DIR=%LOCALAPPDATA%\HandBrakeCLI"
set "ZIP_FILE=%TEMP%\HandBrakeCLI-%VERSION%.zip"

:: ── Check if already installed ──────────────────────────────────
where HandBrakeCLI >nul 2>nul
if %ERRORLEVEL% equ 0 (
    echo [OK] HandBrakeCLI sudah terinstall dan tersedia di PATH.
    HandBrakeCLI --version
    echo.
    echo Jika ingin reinstall, hapus dulu folder: %INSTALL_DIR%
    pause
    exit /b 0
)

echo ============================================================
echo   HandBrakeCLI Installer v%VERSION%
echo ============================================================
echo.

:: ── Download ────────────────────────────────────────────────────
echo [1/4] Downloading HandBrakeCLI v%VERSION%...
echo       URL: %DOWNLOAD_URL%
echo       Destination: %ZIP_FILE%
echo.

powershell -NoProfile -Command ^
    "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; " ^
    "$ProgressPreference = 'SilentlyContinue'; " ^
    "try { Invoke-WebRequest -Uri '%DOWNLOAD_URL%' -OutFile '%ZIP_FILE%' -UseBasicParsing } " ^
    "catch { Write-Host '[ERROR] Download gagal:' $_.Exception.Message; exit 1 }"

if %ERRORLEVEL% neq 0 (
    echo [ERROR] Download gagal. Periksa koneksi internet Anda.
    pause
    exit /b 1
)

echo [OK] Download selesai.
echo.

:: ── Extract ─────────────────────────────────────────────────────
echo [2/4] Extracting ke %INSTALL_DIR%...

if exist "%INSTALL_DIR%" (
    rmdir /s /q "%INSTALL_DIR%"
)
mkdir "%INSTALL_DIR%"

powershell -NoProfile -Command ^
    "Expand-Archive -Path '%ZIP_FILE%' -DestinationPath '%INSTALL_DIR%' -Force"

if %ERRORLEVEL% neq 0 (
    echo [ERROR] Ekstraksi gagal.
    pause
    exit /b 1
)

:: Cleanup zip
del "%ZIP_FILE%" >nul 2>nul

echo [OK] Extracted ke %INSTALL_DIR%
echo.

:: ── Add to User PATH ────────────────────────────────────────────
echo [3/4] Menambahkan ke User PATH...

:: Check if already in PATH
powershell -NoProfile -Command ^
    "$userPath = [Environment]::GetEnvironmentVariable('PATH', 'User'); " ^
    "if ($userPath -split ';' | Where-Object { $_ -eq '%INSTALL_DIR%' }) { " ^
    "    Write-Host '[OK] Sudah ada di PATH.'; exit 0 " ^
    "} else { " ^
    "    $newPath = $userPath.TrimEnd(';') + ';%INSTALL_DIR%'; " ^
    "    [Environment]::SetEnvironmentVariable('PATH', $newPath, 'User'); " ^
    "    Write-Host '[OK] Berhasil ditambahkan ke User PATH.' " ^
    "}"

:: Also update current session PATH so we can verify immediately
set "PATH=%PATH%;%INSTALL_DIR%"

echo.

:: ── Verify ──────────────────────────────────────────────────────
echo [4/4] Verifikasi instalasi...
echo.

where HandBrakeCLI >nul 2>nul
if %ERRORLEVEL% equ 0 (
    echo ============================================================
    echo   Instalasi berhasil!
    echo ============================================================
    echo.
    HandBrakeCLI --version
    echo.
    echo   Lokasi  : %INSTALL_DIR%
    echo   PATH    : Sudah ditambahkan (User level)
    echo.
    echo   PENTING : Tutup dan buka ulang terminal/CMD yang sedang
    echo             terbuka agar PATH terupdate.
    echo ============================================================
) else (
    echo [ERROR] HandBrakeCLI tidak ditemukan setelah instalasi.
    echo         Coba restart terminal dan jalankan: HandBrakeCLI --version
)

echo.
pause
