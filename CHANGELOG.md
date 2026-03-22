# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.15.0] - 2026-03-21

### Fixed
- **Pause/Resume monitoring** now actually stops and restarts Plex listener threads — previously toggling pause had no effect on active monitoring
- **Reconnect loop** no longer grows the call stack on repeated connection failures — `reconnect()` now signals the existing `run()` loop via a threading event instead of calling `run()` recursively
- **Discord IPC disconnect** no longer attempts to read from the pipe after closing the writer, eliminating spurious `ConnectionResetError` log entries on every clean shutdown
- **Imgur upload** now logs a clear actionable error when `imgurClientID` is empty instead of silently failing with a 403
- **Plex auth API** responses are now validated — missing or null `authToken` / `id` / `code` fields produce clear errors instead of `KeyError` crashes
- Server ownership check (`server.account()`) failure is now logged at DEBUG level instead of silently swallowed

### Changed
- **Default `logging.debug`** is now `false` — new installs no longer produce verbose debug output
- **Pause/Resume** from the system tray menu now fully disconnects Discord Rich Presence when paused and reconnects listeners when resumed
- **Config reads/writes** are now protected by a reentrant lock — eliminates a race condition between listener threads reading config and the GUI saving it
- **Container setup** (`chmod`/`chown`) now uses `subprocess.run()` with list arguments instead of `os.system()` with f-strings, eliminating shell injection risk from environment variables
- **Button label encoding** now uses Unicode transliteration (`unidecode`) instead of stripping non-ASCII characters — non-English titles like `"Ñoño"` become `"Nono"` instead of `""`
- Auth URL construction uses `urllib.parse.urlencode` instead of manual `%%5B`/`%%5D` escape sequences
- Shared container setup logic extracted from `main.py` and `main_tray.py` into `core/setup.py`
- `handleAlert` decomposed into focused helper methods (`_isLibraryAllowed`, `_shouldUpdate`, `_isSessionForListenUser`, `_buildMediaMetadata`, `_buildButtons`, `_buildTimestamps`, `_buildActivity`)
- Imgur cache entries now store a 30-day TTL — expired entries are treated as missing and re-uploaded automatically
- `ConfigWindow` validates all fields before mutating config; `maxSize` range (64–1024) is enforced; double-close is handled safely
- Release notes in CI workflow updated to reflect `%APPDATA%\PlexDiscordRPC` data directory

### Added
- **Automated test suite**: 89 tests across `tests/` covering `utils/text.py`, `utils/dict.py`, `utils/cache.py`, config migration logic, and `core/plex.py` helpers
- **Ruff linting** added to CI — runs in parallel with the build job on every push and pull request
- `pyproject.toml` with ruff and pytest configuration

### Dependencies
- Added `Unidecode==1.4.0`

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
