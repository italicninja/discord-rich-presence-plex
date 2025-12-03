@echo off
REM Build script for Discord Rich Presence for Plex
REM Creates a standalone Windows executable

echo ========================================
echo Discord Rich Presence for Plex Builder
echo ========================================
echo.

REM Clean previous builds
echo [1/4] Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
echo Done.
echo.

REM Build with PyInstaller
echo [2/4] Building executable with PyInstaller...
python -m PyInstaller PlexDiscordRPC.spec --clean
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Build failed!
    pause
    exit /b 1
)
echo Done.
echo.

REM Copy icon to dist folder (for runtime icon loading fallback)
echo [3/4] Copying assets to dist folder...
copy icon.png dist\ >nul 2>&1
copy icon.ico dist\ >nul 2>&1
echo Done.
echo.

REM Show results
echo [4/4] Build complete!
echo.
echo Executable location: dist\PlexDiscordRPC.exe
echo.
echo You can now:
echo   1. Test: dist\PlexDiscordRPC.exe
echo   2. Distribute: dist\PlexDiscordRPC.exe (standalone)
echo.
echo Data files (config, cache, logs) will be created in:
echo   %APPDATA%\PlexDiscordRPC\data\
echo   (or .\data\ if APPDATA is not available)
echo.

pause
