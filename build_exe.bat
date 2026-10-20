@echo off
echo ========================================================
echo       Building WDoing Standalone Executable (.exe)
echo ========================================================
python -m PyInstaller --noconfirm --onedir --windowed --icon "assets/icon.ico" --add-data "assets;assets" --name "WDoing" wdoing.py
echo ========================================================
if exist "dist\WDoing\WDoing.exe" (
    echo [SUCCESS] Built executable at dist\WDoing\WDoing.exe
) else (
    echo [ERROR] Build failed.
)
pause
