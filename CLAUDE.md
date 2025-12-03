# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Discord Rich Presence for Plex is a Python script that displays your Plex Media Server status on Discord using Rich Presence. The script monitors Plex playback alerts and updates Discord with current media information including posters, progress, and metadata.

## Running the Application

### Standard Usage
```bash
# Install dependencies
python -m pip install -U -r requirements.txt

# Run the application
python main.py

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
utils/         - Utility functions (logging, text formatting, caching, dict operations)
config/        - Application constants and environment configuration
data/          - Runtime data (config.yaml, cache.json, console.log)
```

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
