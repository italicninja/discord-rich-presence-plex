# GUI Settings Window Feature

## Overview

Version 2.14.0 introduces a **graphical settings window** that allows users to configure the application without manually editing YAML files. This makes the Windows executable even more user-friendly and accessible.

## Features

### Accessible from System Tray
- Right-click tray icon → **"Settings..."**
- Opens instantly in a clean, organized window
- Always stays on top initially (then can be moved behind)

### Three Organized Tabs

#### 1. Display Settings Tab
Configure what metadata appears in your Discord Rich Presence:

**Metadata Display:**
- ☑️ Show duration (movies & TV shows)
- ☑️ Show release year
- ☑️ Show genres (movies only)

**Music Display:**
- ☑️ Show album name
- ☑️ Show artist name
- ☑️ Show album image
- ☑️ Show artist image

**Progress Display:**
- 🔘 Progress mode: Bar / Elapsed / Remaining / Off
- ☑️ Show Rich Presence while paused
- ☑️ Show status icon (playing/paused/buffering)

#### 2. Posters & Images Tab
Configure poster/image uploads to Discord:

**Poster Settings:**
- ☑️ Enable poster display (requires Imgur Client ID)
- 📝 Imgur Client ID input field
- 📚 Help text with link to get Client ID
- 🔢 Maximum poster size (64-1024px)
  - Larger = better quality, slower upload
  - Default: 256px

**Smart Field Toggling:**
- Imgur fields automatically enable/disable based on poster checkbox
- Visual feedback for what's active

#### 3. Logging Tab
Configure application logging:

**Logging Settings:**
- ☑️ Enable debug logging
  - Provides detailed troubleshooting information
- ☑️ Write logs to file
  - Note: System tray mode always writes logs

### User Experience

**Input Validation:**
- Warns if poster display enabled but no Imgur Client ID provided
- Prevents saving invalid configurations

**Helpful UI Elements:**
- Tooltips and descriptions explain each option
- Color-coded background for help text
- Disabled state for irrelevant options

**Save Workflow:**
1. Adjust settings as needed
2. Click "Save & Restart Required"
3. Config saved to YAML file
4. Notification: "Settings saved! Please restart..."
5. User quits and restarts app
6. Changes take effect

**Cancel Option:**
- "Cancel" button discards changes
- Window close button also cancels

## Technical Implementation

### Architecture

**Module:** `ui/config_window.py`
- Self-contained GUI configuration window
- Uses Python's built-in `tkinter` library
- No external GUI dependencies needed

**Integration:** `main_tray.py`
- Gracefully handles missing tkinter
- Falls back to manual config editing if GUI unavailable
- Menu item only appears when GUI is available

### Dependencies

**Required:**
- `tkinter` - Built into Python on Windows
- `tkinter.ttk` - Modern themed widgets
- `tkinter.scrolledtext` - Not used currently, reserved for future

**PyInstaller:**
- tkinter explicitly included in hiddenimports
- Adds ~3MB to executable size (18MB total vs 15MB)

### Config Workflow

1. **Load:** Copy current config into window
2. **Edit:** User modifies settings via GUI controls
3. **Validate:** Check for required fields (e.g., Imgur ID)
4. **Save:** Update config dictionary
5. **Persist:** Write to config.yaml via `saveConfig()`
6. **Notify:** Inform user to restart

### Error Handling

**Missing tkinter:**
- Import wrapped in try/except
- `HAS_GUI` flag set to False
- Settings menu item not added
- Fallback notification if user somehow triggers it

**Config Save Errors:**
- Exception logging
- User notification via system tray
- Config file not corrupted (transaction-like save)

## User Benefits

### Before (v2.13.0 and earlier)
❌ Edit config.yaml manually
❌ Learn YAML syntax
❌ Risk syntax errors
❌ Find config file location
❌ Use external text editor
❌ Remember all option names

### After (v2.14.0)
✅ Click "Settings..."
✅ Visual checkboxes and controls
✅ No syntax errors possible
✅ Built into application
✅ No external tools needed
✅ Clear option descriptions

## Comparison to Manual Editing

| Aspect | Manual YAML | GUI Settings |
|--------|-------------|--------------|
| **Ease of Use** | Advanced users | Everyone |
| **Error Risk** | High (syntax) | Low (validated) |
| **Discovery** | Read docs | Visual options |
| **Speed** | Fast (if skilled) | Fast (if unskilled) |
| **Help** | External docs | Inline tooltips |
| **Restart** | Manual | Reminder notification |

**Both methods supported!** Advanced users can still edit YAML directly.

## Future Enhancements

Potential improvements for future versions:

### Additional Settings
- [ ] User/server management (add/remove accounts)
- [ ] Library whitelist/blacklist configuration
- [ ] Button URL customization
- [ ] Discord IPC pipe selection
- [ ] Auto-start toggle (Phase 4 feature)

### UI Improvements
- [ ] Live preview of Rich Presence
- [ ] Import/export settings profiles
- [ ] Reset to defaults button
- [ ] Dark mode theme
- [ ] Keyboard shortcuts (Ctrl+S to save)

### Advanced Features
- [ ] Apply changes without restart (hot reload)
- [ ] Undo/Redo support
- [ ] Search/filter settings
- [ ] Tooltips on hover
- [ ] Link to online documentation

## Testing

### Manual Testing Checklist
- [x] Window opens and displays correctly
- [x] All tabs accessible
- [x] Checkboxes toggle correctly
- [x] Radio buttons select correctly
- [x] Text inputs accept text
- [x] Spinbox adjusts numbers
- [x] Imgur fields enable/disable properly
- [x] Validation prevents invalid saves
- [x] Cancel button discards changes
- [x] Save button persists changes
- [x] Config file updated correctly
- [x] Notification shown after save
- [x] Window closes properly
- [ ] Changes take effect after restart (needs full integration test)

### Edge Cases
- [x] Missing tkinter (graceful fallback)
- [x] Empty Imgur ID with posters enabled (validation error)
- [x] Config save failure (error notification)
- [x] Window already open (brings to front)
- [ ] Corrupted config file (needs testing)
- [ ] Very large/small window sizes (needs testing)

## Screenshots

*TODO: Add screenshots of settings window*

1. Display Settings tab
2. Posters & Images tab
3. Logging tab
4. Validation error message
5. Save confirmation notification

## Files Created/Modified

### New Files
- `ui/__init__.py` - Package initialization
- `ui/config_window.py` - GUI configuration window (380 lines)
- `GUI_SETTINGS_FEATURE.md` - This documentation

### Modified Files
- `main_tray.py` - Added GUI integration and menu item
- `PlexDiscordRPC.spec` - Added tkinter to hiddenimports
- `README.md` - Added GUI configuration section
- `CHANGELOG.md` - Version 2.14.0 entry
- `config/constants.py` - Version bump to 2.14.0
- `.gitignore` - Excluded test_config_gui.py

### Test Files (Not in Git)
- `test_config_gui.py` - Standalone GUI test script

## Version History

- **v2.14.0** (2024-12-05) - Initial GUI settings implementation
- **v2.13.0** (2024-12-05) - AppData storage (prerequisite)
- **v2.12.0** (2024-12-03) - System tray application

## Related Documentation

- [README.md](README.md) - User guide with GUI instructions
- [CHANGELOG.md](CHANGELOG.md) - Version 2.14.0 changes
- [CLAUDE.md](CLAUDE.md) - Development architecture
- [main_tray.py](main_tray.py) - Main application code
- [ui/config_window.py](ui/config_window.py) - GUI implementation

---

**Summary:** The GUI settings window makes Discord Rich Presence for Plex accessible to non-technical users while maintaining flexibility for advanced users who prefer manual configuration.
