# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Discord Rich Presence for Plex is a Python script that displays your Plex Media Server status on Discord using Rich Presence. The script monitors Plex playback alerts and updates Discord with current media information including posters, progress, and metadata.

## Running the Application

### Windows Standalone Executable (v2.13.0+)
```bash
# Build the executable
python generate_version_info.py
python -m PyInstaller PlexDiscordRPC.spec --clean
copy icon.png dist\
copy icon.ico dist\

# Run the executable
dist\PlexDiscordRPC-v2.13.0.exe

# Data is stored in %APPDATA%\PlexDiscordRPC
```

### Python Script (Development/CLI)
```bash
# Install dependencies
python -m pip install -U -r requirements.txt

# Run CLI version
python main.py

# Run system tray version (development)
python main_tray.py

# Test Discord IPC connection
python main.py test-ipc [pipe_number]
```

### Docker Usage
```bash
# Build and run with docker-compose
docker-compose up -d

# View logs
docker-compose logs -f drpp
```

## Development Commands

### Environment Variables
- `DRPP_PLEX_SERVER_NAME_INPUT` - Plex server name during initial setup
- `DRPP_NO_PIP_INSTALL` - Set to `true` to skip automatic dependency installation
- `DRPP_UID` / `DRPP_GID` - User/group ID for Docker containers
- `DRPP_NO_RUNTIME_DIR_CHOWN` - Set to `true` to skip runtime directory ownership changes in Docker

## Architecture

### Core Components

**Multi-threaded Alert System**: The application uses a threaded architecture where each Plex server gets its own `PlexAlertListener` thread that independently monitors playback alerts and manages Discord IPC connections.

**IPC Communication**: Discord Rich Presence is updated via Discord's IPC (Inter-Process Communication) pipes. The `DiscordIpcService` handles connection to Discord's local IPC socket using asyncio for async I/O operations. On Unix systems it uses Unix domain sockets, on Windows it uses named pipes (`\\?\pipe\discord-ipc-N`).

**Alert Flow**:
1. `PlexAlertListener` receives WebSocket alerts from Plex Media Server
2. Validates alert is from the correct user and library
3. Fetches media metadata from Plex API
4. Optionally uploads poster images to Imgur for Rich Presence display
5. Constructs Discord activity payload with media details
6. Sends activity to Discord via `DiscordIpcService`

**Session Management**: The listener maintains state (`lastSessionKey`, `lastRatingKey`, `lastState`) to deduplicate alerts and handle paused/stopped states with configurable timeout timers (`updateTimeoutTimer`, `disconnectTimer`).

### Directory Structure

```
core/          - Core business logic (Discord IPC, Plex alerts, Imgur uploads, config management)
models/        - TypedDict type definitions for structured data
utils/         - Utility functions (logging, text formatting, caching, dict operations, PyInstaller resources)
config/        - Application constants and environment configuration
data/          - Runtime data (config.yaml, cache.json, console.log)
               - Windows executable: %APPDATA%\PlexDiscordRPC (v2.13.0+)
               - Python/Docker: ./data
```

### Data Storage (v2.13.0+)

**Platform-aware data directory:**
- Windows executable: `%APPDATA%\PlexDiscordRPC` (persistent across updates)
- Development/Docker: `./data` (local directory)

**Implementation** (`config/constants.py`):
- `get_data_directory()` detects execution context (frozen vs. script)
- Returns AppData path when running as PyInstaller executable on Windows
- Falls back to `./data` for backwards compatibility

**Migration:**
- `main_tray.py` automatically migrates existing config from `./data` to AppData on first run
- Old files are copied (not moved) for safety
- See `APPDATA_MIGRATION.md` for details

### Key Modules

**core/plex.py**:
- `PlexAlertListener` - Main thread class that handles Plex WebSocket alerts
- Implements connection retry logic and periodic connection checks
- Filters alerts by user, library whitelist/blacklist, and media type
- Maps Plex media to Discord activity format

**core/discord.py**:
- `DiscordIpcService` - Manages Discord IPC connection lifecycle
- Uses asyncio for non-blocking pipe I/O operations
- Handles multiple pipe locations (standard, Flatpak, Discord App paths)
- Implements handshake and activity update protocol

**core/config.py**:
- Config loading/saving with YAML and JSON support
- Maintains default config structure with runtime overrides
- Handles config migration from older versions

**utils/cache.py**:
- Caches Imgur upload URLs to avoid re-uploading the same posters
- Persists to `data/cache.json`

### Configuration System

The config is loaded from `data/config.{yaml,yml,json}` with YAML preferred. The config structure is type-safe using TypedDict models in `models/config.py`. Configuration supports:
- Multiple users with multiple Plex servers per user
- Per-server settings (library filters, IPC pipe selection, user filtering)
- Display options for posters, buttons, progress modes, metadata fields
- Dynamic button URLs that resolve to IMDb, TMDB, TheTVDB, Trakt, Letterboxd, MusicBrainz

### Media Type Handling

The script supports: `movie`, `episode`, `live_episode`, `track`, `clip`

Each media type has custom metadata extraction:
- **Movies**: Title, year, genres, poster
- **Episodes**: Show title, season/episode number, episode title, show poster
- **Music**: Track title, album, artist, duration, album art, artist image
- **Live TV**: Show title, episode title (if different), show poster

### Button System

Buttons use dynamic URL placeholders (`dynamic:imdb`, `dynamic:tmdb`, etc.) that are resolved at runtime using Plex's Guid metadata. The script maps Plex GUIDs to external service URLs and supports filtering buttons by media type.

## Testing

There are no automated tests. Use `python main.py test-ipc` to verify Discord IPC connectivity.

## Important Notes

- The script must run on the same machine as the Discord client (Discord IPC is local-only)
- For containerized Discord, the Discord IPC Unix socket directory must be mounted into both containers
- Config file is auto-created on first run with defaults; first-time setup requires Plex OAuth authentication via browser
- Imgur client ID is required for poster display (obtain from https://api.imgur.com/oauth2/addclient)

## Documentation Maintenance

### Documentation Philosophy

**Active Documentation (Root Directory):**
- **README.md** - Primary user documentation (installation, configuration, usage)
- **CHANGELOG.md** - Version history (append-only, never delete)
- **CLAUDE.md** - Developer guide (this file)
- **RELEASING.md** - Release process and CI/CD
- **DOCS.md** - Documentation index

**Feature Documentation (Root Directory):**
- Technical deep-dives on specific features (e.g., `APPDATA_MIGRATION.md`, `GUI_SETTINGS_FEATURE.md`)
- Keep only if actively referenced or provides ongoing value
- Archive when superseded by README/CHANGELOG

**Archived Documentation (`.archive/` Directory):**
- Phase completion reports (development history)
- Troubleshooting guides for resolved issues
- One-time status reports
- Superseded technical documents

### When to Archive Documents

**Archive a document when it meets ANY of these criteria:**

1. ✅ **Completion Report** - Documents a completed phase/project
   - Example: `PHASE1_COMPLETE.md`, `DEPLOYMENT_COMPLETE.md`
   - Reason: Historical record, not needed for ongoing work

2. ✅ **Resolved Issue** - Troubleshooting guide for a fixed problem
   - Example: `GITHUB_PERMISSIONS_FIX.md`
   - Reason: Issue no longer occurs, kept for reference

3. ✅ **Superseded Content** - Information now in active docs
   - Example: Phase details now in CHANGELOG.md
   - Reason: Duplicates information in maintained docs

4. ✅ **Point-in-Time Report** - Snapshot of status at a specific time
   - Example: `PIPELINE_TEST_RESULTS.md`, `VERSIONING_AND_CI_COMPLETE.md`
   - Reason: Status has changed, historical value only

5. ✅ **Completed Checklist** - Development plan that's been finished
   - Example: `WINDOWS_APP_CONVERSION.md` (conversion complete)
   - Reason: Work is done, kept for "how we got here" context

### When to Keep Documents Active

**Keep a document active when it meets ANY of these criteria:**

1. ✅ **User Reference** - Actively referenced by end users
   - Example: README.md, CHANGELOG.md
   - Reason: Primary documentation

2. ✅ **Developer Reference** - Current architecture/processes
   - Example: CLAUDE.md, RELEASING.md
   - Reason: Living documents, regularly updated

3. ✅ **Feature Deep-Dive** - Technical details for current features
   - Example: `APPDATA_MIGRATION.md` (current feature)
   - Reason: Useful for troubleshooting and similar implementations
   - **Archive when:** Feature is deprecated or replaced

4. ✅ **Index/Navigation** - Helps users find information
   - Example: DOCS.md
   - Reason: Central navigation hub

### Archiving Process

**Step 1: Create/Update Archive README**
```bash
# If .archive/README.md doesn't exist or needs updating
# Document what's being archived and why
```

**Step 2: Move Files to Archive**
```bash
mv OUTDATED_DOC.md .archive/
```

**Step 3: Update .gitignore (if needed)**
```gitignore
# Archive is tracked in git for history
# .archive/ should NOT be in .gitignore
```

**Step 4: Update Documentation Index**
```bash
# Update DOCS.md to reflect current active docs
# Remove references to archived files
```

### Regular Maintenance Schedule

**After Each Release:**
1. Review completion/status report documents
2. Archive phase completion docs
3. Update CHANGELOG.md with release notes
4. Archive any superseded technical docs

**Monthly Review:**
1. Check for outdated troubleshooting guides
2. Verify feature docs are still relevant
3. Update DOCS.md index
4. Clean up temporary development notes

**Before Major Releases:**
1. Comprehensive documentation audit
2. Archive obsolete feature docs
3. Ensure README.md is concise and current
4. Verify all links work

### README.md Best Practices

**Keep README Concise and User-Focused:**

✅ **Include:**
- Installation instructions (Windows exe, Python, Docker)
- Quick start guide
- Essential configuration (with GUI emphasis for Windows)
- Common use cases
- Troubleshooting basics
- Links to detailed docs

❌ **Avoid:**
- Developer implementation details (→ CLAUDE.md)
- Version history (→ CHANGELOG.md)
- Release process (→ RELEASING.md)
- Resolved issues (→ archive)
- Excessive technical depth (→ feature docs)

**README Structure:**
1. Brief description with screenshot
2. Installation (platform-specific)
3. Configuration (emphasize GUI for Windows)
4. Usage examples
5. FAQ/Troubleshooting
6. Links to other docs
7. License/Contributing

### CHANGELOG.md Best Practices

**Never Delete CHANGELOG Entries:**
- Append-only document
- Follows [Keep a Changelog](https://keepachangelog.com/) format
- Each version has: Added, Changed, Deprecated, Removed, Fixed, Security

**Supersedes:**
- Phase completion reports
- Version release notes files (e.g., `V2.13.0_RELEASE_NOTES.md`)
- Deployment status documents

### Feature Documentation Lifecycle

**Creation:**
```
New Feature Implemented
    ↓
Create FEATURE_NAME.md (detailed technical doc)
    ↓
Update README.md (user-facing summary)
    ↓
Update CHANGELOG.md (version entry)
```

**Maintenance:**
```
Feature Updated
    ↓
Update FEATURE_NAME.md (technical details)
    ↓
Update README.md (if user-facing changes)
    ↓
Update CHANGELOG.md (new version entry)
```

**Deprecation:**
```
Feature Removed/Replaced
    ↓
Update README.md (remove references)
    ↓
Update CHANGELOG.md (note deprecation)
    ↓
Archive FEATURE_NAME.md → .archive/
    ↓
Update .archive/README.md
```

### Example Archives

**Already Archived:**
- `PHASE1_COMPLETE.md` - System tray completion (superseded by CHANGELOG)
- `PHASE3_COMPLETE.md` - PyInstaller packaging (superseded by CHANGELOG)
- `WINDOWS_APP_CONVERSION.md` - Conversion plan (work complete)
- `DEPLOYMENT_COMPLETE.md` - v2.12.0 status (superseded by CHANGELOG)
- `GITHUB_PERMISSIONS_FIX.md` - Resolved CI/CD issue
- `PIPELINE_TEST_RESULTS.md` - Initial test results
- `VERSIONING_AND_CI_COMPLETE.md` - CI/CD setup (superseded by RELEASING.md)

**Currently Active Feature Docs:**
- `APPDATA_MIGRATION.md` - Current feature (v2.13.0), useful for troubleshooting
- `GUI_SETTINGS_FEATURE.md` - Current feature (v2.14.0), technical reference

**Archive These When:**
- AppData storage is replaced with different system
- GUI settings are significantly redesigned
- Features are deprecated or removed

### Commands Reference

**Check for outdated docs:**
```bash
# List all markdown files with last modified date
ls -lt *.md

# Search for "complete" or "status" in filenames (candidates for archiving)
ls *.md | grep -i "complete\|status\|results\|fix"
```

**Archive a document:**
```bash
# Move to archive
mv DOCUMENT.md .archive/

# Update archive README
echo "- DOCUMENT.md - Description of why archived" >> .archive/README.md

# Update DOCS.md
# (manually remove references to archived doc)
```

**Verify archive is tracked:**
```bash
# Archive should be in git
git status .archive/

# Archive should NOT be in .gitignore
grep -v "^#" .gitignore | grep archive
# (should return nothing)
```

### Documentation Checklist

**Before Committing Changes:**
- [ ] README.md is concise and user-focused
- [ ] CHANGELOG.md has entry for version changes
- [ ] Completion/status reports moved to `.archive/`
- [ ] `.archive/README.md` updated with new archives
- [ ] DOCS.md index reflects current active docs
- [ ] Feature docs are still relevant or archived
- [ ] No duplicate information across docs
- [ ] All internal links work

**Monthly Audit:**
- [ ] Review all root-level .md files
- [ ] Archive obsolete documents
- [ ] Update DOCS.md
- [ ] Verify README is current
- [ ] Check CHANGELOG format
- [ ] Review feature docs relevance

---

**Remember:** Archive liberally to keep the project clean, but never delete - historical context has value!
