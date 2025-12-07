# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.14.0] - 2024-12-05

### Added
- **GUI Settings Window**: New graphical configuration interface accessible from system tray menu
  - Right-click tray icon → "Settings..." to open
  - Three organized tabs: Display Settings, Posters & Images, Logging
  - Edit common settings without manually editing YAML files
  - Visual controls: checkboxes, radio buttons, text inputs, spinners
  - Input validation and helpful tooltips
  - Changes require application restart to take effect
- **Display Settings Tab**:
  - Toggle metadata display (duration, year, genres)
  - Music display options (album, artist, images)
  - Progress mode selection (bar, elapsed, remaining, off)
  - Status icon and paused display options
- **Posters & Images Tab**:
  - Enable/disable poster display
  - Imgur Client ID configuration with instructions
  - Maximum poster size adjustment
- **Logging Tab**:
  - Debug logging toggle
  - Write to file toggle

### Changed
- System tray menu now includes "Settings..." option (when tkinter is available)
- Menu reorganized: Settings at top, file access options grouped together

### Technical
- Created new `ui` package with `config_window.py` module
- Uses tkinter for cross-platform GUI (bundled with Python)
- GUI gracefully disabled if tkinter not available
- PyInstaller spec updated to include tkinter dependencies
- Config changes are validated before saving

## [2.13.0] - 2024-12-05

### Added
- **Persistent AppData storage**: Configuration, cache, and logs are now stored in `%APPDATA%\PlexDiscordRPC` when running as a Windows executable
  - Ensures data persists across application updates
  - Follows Windows best practices for user data storage
  - Development/Docker mode still uses `./data` directory for backwards compatibility
- **Data folder menu item**: Added "Open Data Folder" option to system tray menu for easy access to config files
- **Automatic migration**: Existing config files in `./data` are automatically migrated to AppData on first run
- **Data directory logging**: Application now logs the absolute path to the data directory on startup

### Changed
- Data directory location is now platform and context-aware:
  - Windows (executable): `%APPDATA%\PlexDiscordRPC`
  - Windows/Linux (development): `./data`
  - Docker: `./data`

### Fixed
- Config files are now preserved when updating the executable to a new version

## [2.12.0] - 2024-12-03

### Added
- Windows system tray application (`main_tray.py`)
- PyInstaller packaging for standalone executable distribution
- GitHub Actions CI/CD pipeline for automated builds and releases
- System notifications for monitoring status changes
- Pause/Resume functionality without restarting
- Quick access menu items for config and log files

### Changed
- Application now runs silently in Windows system tray
- No console window when running as executable
- File logging enabled by default in tray mode

### Technical
- Created `PlexDiscordRPC.spec` for PyInstaller configuration
- Added `build.bat` script for building Windows executable
- Implemented resource path handling for PyInstaller compatibility
- Added Windows version information metadata

## [2.11.0 and earlier]

See git history for changes prior to Windows application conversion.
