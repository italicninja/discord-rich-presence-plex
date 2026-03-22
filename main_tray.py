"""
Windows System Tray Application for Discord Rich Presence for Plex
"""

from core.setup import configure_container_environment
from utils.logging import logger
import os
import sys

configure_container_environment()

from config.constants import noPipInstall
from utils.resources import is_frozen

# Auto-install dependencies (skip if running as PyInstaller executable)
if not noPipInstall and not is_frozen():
	try:
		import subprocess
		def parsePipPackages(packagesStr: str) -> dict[str, str]:
			return { packageSplit[0].lower(): packageSplit[1] if len(packageSplit) > 1 else "" for packageSplit in [package.split("==") for package in packagesStr.splitlines()] }
		pipFreezeResult = subprocess.run([sys.executable, "-m", "pip", "freeze"], stdout = subprocess.PIPE, text = True, check = True)
		installedPackages = parsePipPackages(pipFreezeResult.stdout)
		with open("requirements.txt", "r", encoding = "UTF-8") as requirementsFile:
			requiredPackages = parsePipPackages(requirementsFile.read())
		for packageName, requiredPackageVersion in requiredPackages.items():
			installedPackageVersion = installedPackages.get(packageName, "none")
			if installedPackageVersion != requiredPackageVersion:
				logger.info(f"Installing dependency: {packageName} (required: {requiredPackageVersion}, installed: {installedPackageVersion})")
				subprocess.run([sys.executable, "-m", "pip", "install", "-U", f"{packageName}=={requiredPackageVersion}"], check = True)
	except Exception:
		logger.exception("An unexpected error occurred during automatic installation of dependencies. Install them manually by running the following command: python -m pip install -U -r requirements.txt")

from config.constants import dataDirectoryPath, logFilePath, name, version, plexServerNameInput
from core.config import config, config_lock, loadConfig, saveConfig
from core.plex import PlexAlertListener, initiateAuth, getAuthToken
from typing import Optional
from utils.cache import loadCache
from utils.logging import formatter
from utils.text import formatSeconds
from utils.resources import get_resource_path
import logging
import models.config
import time
import threading
import pystray
from PIL import Image

# Import GUI configuration window
try:
	from ui.config_window import ConfigWindow
	HAS_GUI = True
except ImportError:
	HAS_GUI = False
	import warnings
	warnings.warn("tkinter not available - GUI settings will be disabled")

class PlexDiscordRPC:
	"""Main application class for Windows system tray"""

	def __init__(self):
		self.running = True
		self.monitoring = True
		self.icon: Optional[pystray.Icon] = None
		self.plexAlertListeners: list[PlexAlertListener] = []
		self.monitor_thread: Optional[threading.Thread] = None

	def init(self) -> None:
		"""Initialize application (same as main.py init)"""
		if not os.path.isdir(dataDirectoryPath):
			os.makedirs(dataDirectoryPath)

		# Migrate old files from current directory to data directory
		for oldFilePath in ["config.json", "cache.json", "console.log"]:
			if os.path.isfile(oldFilePath):
				os.rename(oldFilePath, os.path.join(dataDirectoryPath, oldFilePath))

		# Migrate old data from ./data to AppData (when running as executable on Windows)
		from utils.resources import is_frozen
		if sys.platform == "win32" and is_frozen() and dataDirectoryPath != "data":
			old_data_dir = "data"
			if os.path.isdir(old_data_dir):
				# Migrate config, cache, and logs from old location
				for filename in ["config.yaml", "config.yml", "config.json", "cache.json", "console.log"]:
					old_file = os.path.join(old_data_dir, filename)
					new_file = os.path.join(dataDirectoryPath, filename)
					if os.path.isfile(old_file) and not os.path.isfile(new_file):
						try:
							import shutil
							shutil.copy2(old_file, new_file)
							logger.info(f"Migrated {filename} from {old_data_dir} to {dataDirectoryPath}")
						except Exception as e:
							logger.warning(f"Failed to migrate {filename}: {e}")

		loadConfig()
		if config["logging"]["debug"]:
			logger.setLevel(logging.DEBUG)
		# Always write to file for tray app (no console)
		if not any(isinstance(h, logging.FileHandler) for h in logger.handlers):
			fileHandler = logging.FileHandler(logFilePath)
			fileHandler.setFormatter(formatter)
			logger.addHandler(fileHandler)
		logger.info("%s - v%s (System Tray Mode)", name, version)
		logger.info(f"Data directory: {os.path.abspath(dataDirectoryPath)}")
		loadCache()

	def auth_new_user(self) -> Optional[models.config.User]:
		"""Authenticate a new Plex user"""
		id, code, url = initiateAuth()
		logger.info("Authentication required. Opening browser...")
		logger.info(f"Auth URL: {url}")

		# Try to open browser automatically
		try:
			import webbrowser
			webbrowser.open(url)
		except:
			pass

		# Show notification
		if self.icon:
			self.icon.notify("Please sign in to Plex in your browser", "Authentication Required")

		time.sleep(5)
		for i in range(35):
			logger.info(f"Checking authentication status ({formatSeconds((i + 1) * 5)})")
			authToken = getAuthToken(id, code)
			if authToken:
				logger.info("Authentication successful")
				serverName = plexServerNameInput or "ServerName"
				if serverName == "ServerName":
					logger.warning("Using 'ServerName' as placeholder. Edit config.yaml to set the correct server name.")
				if self.icon:
					self.icon.notify("Authentication successful!", "Plex Discord RPC")
				return { "token": authToken, "servers": [{ "name": serverName }] }
			time.sleep(5)
		else:
			logger.info(f"Authentication timed out ({formatSeconds(180)})")
			if self.icon:
				self.icon.notify("Authentication timed out. Please restart the app.", "Plex Discord RPC")
			return None

	def start_monitoring(self) -> None:
		"""Start Plex monitoring (creates PlexAlertListener threads for each server)."""
		if self.plexAlertListeners:
			logger.debug("start_monitoring() called but listeners are already running — ignoring")
			return

		if not config["users"]:
			logger.info("No users found in config file")
			user = self.auth_new_user()
			if not user:
				logger.error("Authentication failed. Cannot start monitoring.")
				return
			config["users"].append(user)
			saveConfig()

		self.plexAlertListeners = [
			PlexAlertListener(user["token"], server)
			for user in config["users"]
			for server in user["servers"]
		]
		logger.info(f"Started monitoring {len(self.plexAlertListeners)} Plex server(s)")

	def stop_monitoring(self) -> None:
		"""Stop all Plex monitoring and disconnect Discord Rich Presence."""
		for listener in self.plexAlertListeners:
			try:
				listener.disconnect()
			except Exception:
				pass
		self.plexAlertListeners = []
		logger.info("Stopped monitoring")

	def monitoring_loop(self) -> None:
		"""Entry point for the background monitoring thread — starts listeners and keeps the thread alive."""
		self.start_monitoring()
		while self.running:
			time.sleep(1)

	def toggle_monitoring(self, icon, item) -> None:
		"""Pause or resume Plex monitoring from the system tray menu."""
		self.monitoring = not self.monitoring

		if self.monitoring:
			logger.info("Monitoring resumed")
			self.start_monitoring()
			if self.icon:
				self.icon.title = f"{name} - Monitoring"
				self.icon.notify("Monitoring resumed", name)
		else:
			logger.info("Monitoring paused")
			self.stop_monitoring()
			if self.icon:
				self.icon.title = f"{name} - Paused"
				self.icon.notify("Monitoring paused", name)

		if self.icon:
			self.icon.update_menu()

	def open_config(self, icon, item) -> None:
		"""Open config file in default editor"""
		from config.constants import configFilePathBase
		config_path = None

		# Find the config file
		for ext in ['yaml', 'yml', 'json']:
			test_path = f"{configFilePathBase}.{ext}"
			if os.path.isfile(test_path):
				config_path = test_path
				break

		if config_path:
			try:
				os.startfile(config_path)
				logger.info(f"Opened config file: {config_path}")
				if self.icon:
					self.icon.notify("Restart the app after making changes", "Config file opened")
			except Exception as e:
				logger.error(f"Failed to open config file: {e}")
		else:
			logger.error("Config file not found")

	def open_logs(self, icon, item) -> None:
		"""Open log file in default editor"""
		if os.path.isfile(logFilePath):
			try:
				os.startfile(logFilePath)
				logger.info("Opened log file")
			except Exception as e:
				logger.error(f"Failed to open log file: {e}")
		else:
			logger.error("Log file not found")

	def open_data_folder(self, icon, item) -> None:
		"""Open data folder in Windows Explorer"""
		try:
			if sys.platform == "win32":
				os.startfile(dataDirectoryPath)
			else:
				# For other platforms, try xdg-open or open
				import subprocess
				opener = "xdg-open" if sys.platform == "linux" else "open"
				subprocess.run([opener, dataDirectoryPath])
			logger.info(f"Opened data folder: {dataDirectoryPath}")
		except Exception as e:
			logger.error(f"Failed to open data folder: {e}")

	def open_settings(self, icon, item) -> None:
		"""Open GUI settings window"""
		if not HAS_GUI:
			logger.error("GUI settings not available - tkinter not installed")
			if self.icon:
				self.icon.notify("GUI not available. Please edit config file manually.", name)
			return

		try:
			logger.info("Opening settings window")

			# Create and show the config window
			config_window = ConfigWindow(config, self._on_config_saved)
			config_window.show()

		except Exception as e:
			logger.exception(f"Failed to open settings window: {e}")
			if self.icon:
				self.icon.notify("Failed to open settings. Check logs for details.", name)

	def _on_config_saved(self, new_config: dict) -> None:
		"""Callback when user saves configuration from GUI"""
		try:
			with config_lock:
				# Atomically replace the global config so listener threads never
				# see a partially-cleared dict between clear() and update().
				config.clear() # pyright: ignore[reportAttributeAccessIssue]
				config.update(new_config) # pyright: ignore[reportAttributeAccessIssue]
				saveConfig()

			logger.info("Configuration saved successfully")

			if self.icon:
				self.icon.notify(
					"Settings saved! Please restart the application for changes to take effect.",
					"Configuration Saved"
				)

		except Exception as e:
			logger.exception(f"Failed to save configuration: {e}")
			if self.icon:
				self.icon.notify("Failed to save settings. Check logs for details.", name)

	def quit_app(self, icon, item) -> None:
		"""Quit the application"""
		logger.info("Shutting down...")
		self.running = False
		self.monitoring = False

		# Stop monitoring
		self.stop_monitoring()

		# Stop icon
		if self.icon:
			self.icon.stop()

	def create_menu(self) -> pystray.Menu:
		"""Create system tray menu"""
		menu_items = [
			pystray.MenuItem(name, None, enabled=False),
			pystray.Menu.SEPARATOR,
			pystray.MenuItem(
				lambda text: "Resume Monitoring" if not self.monitoring else "Pause Monitoring",
				self.toggle_monitoring,
				default=True
			),
			pystray.Menu.SEPARATOR,
		]

		# Add Settings option if GUI is available
		if HAS_GUI:
			menu_items.append(pystray.MenuItem("Settings...", self.open_settings))
			menu_items.append(pystray.Menu.SEPARATOR)

		# Add file/folder access options
		menu_items.extend([
			pystray.MenuItem("Open Data Folder", self.open_data_folder),
			pystray.MenuItem("Open Config File", self.open_config),
			pystray.MenuItem("Open Log File", self.open_logs),
			pystray.Menu.SEPARATOR,
			pystray.MenuItem("Quit", self.quit_app)
		])

		return pystray.Menu(*menu_items)

	def load_icon(self) -> Image.Image:
		"""Load or create icon image"""
		# Try to load icon from resource path (works with PyInstaller)
		icon_path = get_resource_path("icon.png")

		if os.path.isfile(icon_path):
			try:
				return Image.open(icon_path)
			except Exception as e:
				logger.warning(f"Failed to load icon from {icon_path}: {e}")

		# Fallback: try current directory
		if os.path.isfile("icon.png"):
			try:
				return Image.open("icon.png")
			except:
				pass

		# Create a simple icon if file doesn't exist
		logger.warning("icon.png not found, creating default icon")
		from PIL import ImageDraw

		size = 64
		image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
		draw = ImageDraw.Draw(image)

		# Draw a simple orange circle with blue center
		draw.ellipse([4, 4, size-4, size-4], fill=(229, 160, 13))
		draw.ellipse([16, 16, size-16, size-16], fill=(88, 101, 242))

		return image

	def setup_tray(self) -> None:
		"""Setup and run system tray icon"""
		image = self.load_icon()
		menu = self.create_menu()

		self.icon = pystray.Icon(
			"plex_discord_rpc",
			image,
			f"{name} - Monitoring",
			menu
		)

		# Start monitoring in background thread
		self.monitor_thread = threading.Thread(target=self.monitoring_loop, daemon=True)
		self.monitor_thread.start()

		logger.info("System tray application started")

		# Run the icon (this blocks until icon.stop() is called)
		self.icon.run()

	def run(self) -> None:
		"""Main entry point"""
		try:
			self.init()
			self.setup_tray()
		except KeyboardInterrupt:
			logger.info("Interrupted by user")
			self.quit_app(None, None)
		except Exception:
			logger.exception("Fatal error in main application")
			sys.exit(1)

if __name__ == "__main__":
	app = PlexDiscordRPC()
	app.run()
