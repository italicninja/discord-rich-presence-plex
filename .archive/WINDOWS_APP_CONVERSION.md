# Windows Application Conversion Checklist

This document outlines the plan to convert Discord Rich Presence for Plex into a Windows system tray application.

## Overview

**Goal:** Convert the Python script into a professional Windows application that runs in the system tray, starts automatically with Windows, and provides easy user controls.

**Approach:** PyInstaller + pystray + Registry Auto-Start

**Estimated Time:** 6-10 hours

---

## Phase 1: System Tray Interface

### 1.1 Add Dependencies
- [ ] Add `pystray>=0.19.4` to requirements.txt
- [ ] Add `Pillow>=10.0.0` to requirements.txt
- [ ] Test dependency installation

### 1.2 Create Icon Assets
- [ ] Create/obtain icon image (64x64 PNG recommended)
- [ ] Create icon.png for system tray
- [ ] Create icon.ico for Windows executable
- [ ] Add icon files to repository

### 1.3 Refactor Main Application Structure
- [ ] Create `PlexDiscordRPC` class to encapsulate application logic
- [ ] Move existing monitoring code into background thread method
- [ ] Add `running` and `monitoring` state flags
- [ ] Ensure clean shutdown handling

### 1.4 Implement System Tray Icon
- [ ] Create icon image generation/loading function
- [ ] Implement system tray menu structure:
  - [ ] Application name (disabled item)
  - [ ] Separator
  - [ ] Pause/Resume toggle
  - [ ] Settings option
  - [ ] Separator
  - [ ] Exit option
- [ ] Wire up menu callbacks

### 1.5 Add Tray Functionality
- [ ] Implement pause/resume monitoring logic
- [ ] Update icon title based on monitoring state
- [ ] Implement graceful exit from tray
- [ ] Add tooltip status updates
- [ ] (Optional) Add notification support for status changes

### 1.6 Redirect Console Output
- [ ] Ensure all output goes to log file (not console)
- [ ] Update logging configuration for background operation
- [ ] Test that no console window appears

---

## Phase 2: Settings Interface

### 2.1 Settings Access (Choose One Approach)

**Option A: Open config file in default editor**
- [ ] Implement "Open Config" menu item
- [ ] Use `os.startfile()` or `subprocess` to open YAML in default editor
- [ ] Add notification to restart app after config changes

**Option B: Simple Tkinter dialog**
- [ ] Create basic settings dialog with Tkinter
- [ ] Add fields for common settings (enable/disable features)
- [ ] Implement save functionality
- [ ] Add "Apply" button that reloads config

**Option C: Advanced PyQt settings window** (Optional, if needed later)
- [ ] Design settings UI
- [ ] Implement all configuration options
- [ ] Add validation
- [ ] Implement apply/save logic

**Decision:** Start with **Option A** (simplest), can upgrade later if needed

---

## Phase 3: PyInstaller Packaging

### 3.1 Create Build Configuration
- [ ] Create `build.bat` build script for Windows
- [ ] Configure PyInstaller options:
  - [ ] `--onefile` for single executable
  - [ ] `--noconsole` to hide console window
  - [ ] `--name "PlexDiscordRPC"`
  - [ ] `--icon=icon.ico`
  - [ ] `--add-data` for config template
  - [ ] `--add-data` for icon.png
  - [ ] `--hidden-import` for pystray dependencies

### 3.2 Test Packaging
- [ ] Run PyInstaller build
- [ ] Test executable on clean Windows machine (no Python installed)
- [ ] Verify all dependencies are included
- [ ] Test Discord IPC connectivity
- [ ] Test Plex API connectivity
- [ ] Check executable size (optimize if needed)

### 3.3 Handle Data Files
- [ ] Ensure config.yaml is created in correct location
- [ ] Test config file persistence across runs
- [ ] Verify cache.json location
- [ ] Verify log file location
- [ ] Document data file locations for users

### 3.4 Debug Packaging Issues
- [ ] Fix any missing imports
- [ ] Fix any missing data files
- [ ] Address antivirus false positives (if any)
- [ ] Optimize startup time

---

## Phase 4: Windows Auto-Start

### 4.1 Implement Auto-Start Functionality
- [ ] Create `auto_start.py` module
- [ ] Implement `add_to_startup()` function using Windows Registry
  - [ ] Target: `HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run`
- [ ] Implement `remove_from_startup()` function
- [ ] Implement `is_in_startup()` check function

### 4.2 Add Auto-Start Menu Option
- [ ] Add "Start with Windows" toggle to system tray menu
- [ ] Show checkmark when enabled
- [ ] Persist preference in config file
- [ ] Test registry modifications

### 4.3 First-Run Setup
- [ ] Detect first run
- [ ] Prompt user to enable auto-start (optional)
- [ ] Set default auto-start preference

### 4.4 Test Auto-Start
- [ ] Enable auto-start
- [ ] Restart Windows
- [ ] Verify app launches automatically
- [ ] Verify app connects to Discord
- [ ] Verify app connects to Plex
- [ ] Test disable auto-start

---

## Phase 5: Installer Creation (Optional but Recommended)

### 5.1 Choose Installer Tool
**Recommended:** Inno Setup (free, popular, easy to use)
- [ ] Download and install Inno Setup
- [ ] Learn basic Inno Setup scripting

### 5.2 Create Installer Script
- [ ] Create `setup.iss` Inno Setup script
- [ ] Configure application metadata
- [ ] Set installation directory
- [ ] Include executable and assets
- [ ] Create Start Menu shortcuts
- [ ] (Optional) Create Desktop shortcut

### 5.3 Installer Features
- [ ] Add option to launch app after installation
- [ ] Add option to start with Windows (checkbox)
- [ ] Create uninstaller
- [ ] Add registry cleanup on uninstall
- [ ] Include license agreement (if needed)

### 5.4 Test Installer
- [ ] Build installer executable
- [ ] Test installation on clean Windows machine
- [ ] Test all installer options
- [ ] Test uninstallation
- [ ] Verify registry cleanup
- [ ] Verify file cleanup

---

## Phase 6: Documentation Updates

### 6.1 Update README.md
- [ ] Add Windows installation section
- [ ] Add system tray usage instructions
- [ ] Update screenshots with tray icon
- [ ] Document auto-start configuration
- [ ] Add troubleshooting section for Windows

### 6.2 Update CLAUDE.md
- [ ] Document new architecture (tray app)
- [ ] Add build instructions
- [ ] Document PyInstaller configuration
- [ ] Add Windows-specific development notes

### 6.3 Create User Documentation
- [ ] Create quick start guide
- [ ] Document system tray features
- [ ] Explain configuration access
- [ ] Add FAQ section

---

## Phase 7: Testing & Quality Assurance

### 7.1 Functional Testing
- [ ] Test on Windows 10
- [ ] Test on Windows 11
- [ ] Test with multiple Plex servers
- [ ] Test with multiple users
- [ ] Test pause/resume functionality
- [ ] Test configuration changes
- [ ] Test exit and restart

### 7.2 Edge Case Testing
- [ ] Test when Discord is not running
- [ ] Test when Plex server is offline
- [ ] Test network disconnection/reconnection
- [ ] Test rapid config changes
- [ ] Test with corrupted config file
- [ ] Test with missing config file

### 7.3 Performance Testing
- [ ] Monitor memory usage over 24 hours
- [ ] Monitor CPU usage during playback
- [ ] Check startup time
- [ ] Verify no memory leaks
- [ ] Test with long-running sessions (days/weeks)

### 7.4 User Acceptance Testing
- [ ] Get feedback from beta testers
- [ ] Address usability issues
- [ ] Refine menu options based on feedback
- [ ] Improve error messages

---

## Phase 8: Release Preparation

### 8.1 Version Management
- [ ] Update version number in constants.py
- [ ] Create CHANGELOG.md
- [ ] Tag release in git

### 8.2 Build Final Release
- [ ] Clean build with PyInstaller
- [ ] Build installer with Inno Setup
- [ ] Create ZIP archive of portable executable
- [ ] Generate checksums (SHA256)

### 8.3 Release Assets
- [ ] Prepare release notes
- [ ] Create GitHub release
- [ ] Upload installer executable
- [ ] Upload portable ZIP
- [ ] Upload checksums file

### 8.4 Announcement
- [ ] Update README badges
- [ ] Announce on relevant communities
- [ ] Update documentation links

---

## Additional Considerations

### Security
- [ ] Review code for security vulnerabilities
- [ ] Ensure sensitive data (tokens) are never logged
- [ ] Verify config file permissions
- [ ] Add code signing certificate (optional, improves trust)

### Backwards Compatibility
- [ ] Ensure existing config files work with new version
- [ ] Migrate old configs if needed
- [ ] Support both CLI and tray mode (optional)

### Future Enhancements
- [ ] Consider adding update checker
- [ ] Consider adding in-app configuration editor
- [ ] Consider adding activity history/statistics
- [ ] Consider adding multiple Discord account support

---

## Success Criteria

- ✅ Application runs silently in system tray
- ✅ Icon reflects current status (monitoring/paused)
- ✅ Right-click menu provides all essential controls
- ✅ Auto-starts with Windows (configurable)
- ✅ Single .exe file (no dependencies)
- ✅ Professional installer available
- ✅ All existing functionality preserved
- ✅ No console window appears
- ✅ Graceful error handling
- ✅ Works on Windows 10 and 11

---

## Development Priority

**Phase 1-2:** Core functionality (tray interface) - **Start Here**
**Phase 3:** Packaging - **Essential for distribution**
**Phase 4:** Auto-start - **Important for UX**
**Phase 5:** Installer - **Nice to have, improves UX**
**Phase 6-8:** Polish and release - **Final steps**

---

## Notes

- Keep the Python script mode available as fallback for advanced users
- Maintain cross-platform compatibility where possible (Docker still works)
- Document all Windows-specific changes
- Test thoroughly on fresh Windows installations
