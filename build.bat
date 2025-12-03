@echo off
REM Build script for Discord Rich Presence for Plex
REM Creates a standalone Windows executable

echo ========================================
echo Discord Rich Presence for Plex Builder
echo ========================================
echo.

REM Clean previous builds
echo [1/5] Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist version_info.txt del version_info.txt
echo Done.
echo.

REM Generate version info
echo [2/5] Generating version information...
python generate_version_info.py
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to generate version info!
    pause
    exit /b 1
)
echo Done.
echo.

REM Build with PyInstaller
echo [3/5] Building executable with PyInstaller...
python -m PyInstaller PlexDiscordRPC.spec --clean
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Build failed!
    pause
    exit /b 1
)
echo Done.
echo.

REM Copy icon to dist folder (for runtime icon loading fallback)
echo [4/5] Copying assets to dist folder...
copy icon.png dist\ >nul 2>&1
copy icon.ico dist\ >nul 2>&1
echo Done.
echo.

REM Show results
echo [5/5] Build complete!
echo.
for %%F in (dist\PlexDiscordRPC*.exe) do (
    echo Executable: %%F
    set EXENAME=%%F
)
echo.
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
