# AppData Storage Implementation

## Overview

Version 2.13.0 introduces persistent data storage in Windows AppData for the standalone executable. This ensures configuration, cache, and logs persist across application updates and follow Windows best practices.

## What Changed

### Before (v2.12.0 and earlier)
- Data stored in `.\data\` directory (same folder as the executable)
- Config would be lost if executable was moved or deleted
- Not following Windows conventions for application data

### After (v2.13.0+)
- **Windows Executable**: Data stored in `%APPDATA%\PlexDiscordRPC`
  - Example: `C:\Users\YourName\AppData\Roaming\PlexDiscordRPC`
- **Python Script / Docker**: Still uses `.\data\` (unchanged)
- Config persists across updates and executable location changes

## Implementation Details

### File Changes

#### `config/constants.py`
Added `get_data_directory()` function that:
1. Detects if running as PyInstaller executable (`sys.frozen` check)
2. Returns AppData path on Windows when frozen
3. Falls back to `./data` for development and Docker

```python
def get_data_directory() -> str:
    is_frozen = getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')

    if sys.platform == "win32" and is_frozen:
        appdata = os.environ.get("APPDATA")
        if appdata:
            return os.path.join(appdata, "PlexDiscordRPC")

    return "data"
```

#### `main_tray.py`
Enhanced initialization with:
1. **Automatic migration**: Copies existing config from `./data` to AppData on first run
2. **Data folder menu item**: New "Open Data Folder" option in tray menu
3. **Logging**: Shows absolute path to data directory on startup

### Migration Logic

When the executable runs for the first time (v2.13.0+), it:
1. Creates `%APPDATA%\PlexDiscordRPC` if it doesn't exist
2. Checks for existing files in `./data` directory
3. Copies found files to AppData (if not already present):
   - `config.yaml` / `config.yml` / `config.json`
   - `cache.json`
   - `console.log`
4. Logs migration actions

Files are **copied** (not moved) for safety - old files remain in `./data`.

## User Experience

### First-Time Users (v2.13.0)
- No changes needed
- Data automatically created in AppData
- Works out of the box

### Upgrading from v2.12.0 or earlier
- **Automatic**: Old config is automatically migrated on first run
- **Manual**: Can copy `data\config.yaml` to `%APPDATA%\PlexDiscordRPC\config.yaml`
- **Easy access**: Right-click tray icon → "Open Data Folder"

### Finding Your Config

Three easy ways:
1. **Tray menu**: Right-click icon → "Open Data Folder"
2. **Tray menu**: Right-click icon → "Open Config File"
3. **Manually**: Navigate to `%APPDATA%\PlexDiscordRPC`
   - Press `Win+R`, type `%APPDATA%\PlexDiscordRPC`, press Enter

## Benefits

### For Users
✅ Config survives application updates
✅ Can move/delete executable without losing settings
✅ Follows Windows standards (familiar location)
✅ Easy access via tray menu
✅ Automatic migration from old location

### For Developers
✅ Cleaner distribution (no data folder needed)
✅ Better update experience
✅ Consistent with other Windows applications
✅ Backwards compatible (dev mode unchanged)

## Data Structure

```
%APPDATA%\PlexDiscordRPC\
├── config.yaml          # User configuration
├── cache.json          # Imgur upload cache
└── console.log         # Application logs
```

## Platform Compatibility

| Platform | Mode | Data Location |
|----------|------|---------------|
| Windows | Executable | `%APPDATA%\PlexDiscordRPC` |
| Windows | Python Script | `.\data` |
| Linux | Docker | `.\data` |
| Linux | Python Script | `.\data` |
| macOS | Python Script | `.\data` |

## Testing

### Test AppData Detection
```python
import sys
sys.frozen = True
sys._MEIPASS = 'C:\\temp\\fake'
from config.constants import dataDirectoryPath
print(dataDirectoryPath)  # Should show AppData path
```

### Test Development Mode
```bash
python -c "from config.constants import dataDirectoryPath; print(dataDirectoryPath)"
# Output: data
```

### Test Executable
1. Run `PlexDiscordRPC-v2.13.0.exe`
2. Check logs for: `Data directory: C:\Users\...\AppData\Roaming\PlexDiscordRPC`
3. Right-click tray icon → "Open Data Folder"
4. Verify folder opens in Explorer

## Troubleshooting

### Can't Find Config
1. Right-click tray icon → "Open Data Folder"
2. Or manually: `Win+R` → `%APPDATA%\PlexDiscordRPC`

### Migration Didn't Work
1. Check `console.log` for migration messages
2. Manually copy `data\config.yaml` to `%APPDATA%\PlexDiscordRPC\config.yaml`
3. Restart the application

### Want to Use Old Location
- Use Python script mode instead: `python main_tray.py`
- Data will be stored in `.\data` as before

## Future Enhancements

Possible improvements for future versions:
- Linux/macOS support for XDG config dirs (`~/.config/PlexDiscordRPC`)
- Settings UI to change data location
- Backup/export configuration option
- Cloud sync support

## Version History

- **v2.13.0** (2024-12-05): AppData storage implemented
- **v2.12.0** (2024-12-03): System tray app with `./data` storage
- **v2.11.0 and earlier**: Python script with `./data` storage

---

**Summary**: This update makes the Windows application more professional and user-friendly by following Windows conventions for data storage while maintaining backwards compatibility for development and Docker usage.
