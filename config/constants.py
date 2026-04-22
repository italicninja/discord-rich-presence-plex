import os
import sys

name = "Discord Rich Presence for Plex"
version = "2.15.1"  # Performance, resource management, and code quality improvements

plexClientID = "discord-rich-presence-plex"
discordClientID = "413407336082833418"

# Determine data directory based on platform and execution context
def get_data_directory() -> str:
	"""
	Get the appropriate data directory for storing config, cache, and logs.

	- Windows (frozen/exe): %APPDATA%/PlexDiscordRPC
	- Windows (dev): ./data (for backwards compatibility)
	- Linux/macOS: ./data (or container-specific path)
	"""
	# Check if running as PyInstaller executable
	is_frozen = getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')

	# For Windows executable, use AppData
	if sys.platform == "win32" and is_frozen:
		appdata = os.environ.get("APPDATA")
		if appdata:
			return os.path.join(appdata, "PlexDiscordRPC")

	# Fallback to ./data for development, Docker, and other platforms
	return "data"

dataDirectoryPath = get_data_directory()
configFilePathBase = os.path.join(dataDirectoryPath, "config")
cacheFilePath = os.path.join(dataDirectoryPath, "cache.json")
logFilePath = os.path.join(dataDirectoryPath, "console.log")

isUnix = sys.platform in ["linux", "darwin"]
processID = os.getpid()
isInteractive = sys.stdin and sys.stdin.isatty()
plexServerNameInput = os.environ.get("DRPP_PLEX_SERVER_NAME_INPUT")
noPipInstall = os.environ.get("DRPP_NO_PIP_INSTALL", "") == "true"
isInContainer = os.environ.get("DRPP_IS_IN_CONTAINER", "") == "true"
runtimeDirectory = "/run/app" if isInContainer else os.environ.get("XDG_RUNTIME_DIR", os.environ.get("TMPDIR", os.environ.get("TMP", os.environ.get("TEMP", "/tmp"))))
ipcPipeBase = runtimeDirectory if isUnix else r"\\?\pipe"
uid = int(os.environ.get("DRPP_UID", "-1"))
gid = int(os.environ.get("DRPP_GID", "-1"))
containerCwd = "/app"
noRuntimeDirChown = os.environ.get("DRPP_NO_RUNTIME_DIR_CHOWN", "") == "true"
