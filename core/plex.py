# pyright: reportUnknownArgumentType=none,reportUnknownMemberType=none,reportUnknownVariableType=none,reportTypedDictNotRequiredAccess=none,reportOptionalMemberAccess=none,reportMissingTypeStubs=none

from .config import config
from .discord import DiscordIpcService
from .imgur import uploadToImgur
from config.constants import name, plexClientID
from plexapi.alert import AlertListener
from plexapi.media import Genre, Guid
from plexapi.myplex import MyPlexAccount, PlexServer
from typing import Optional
from utils.cache import getCacheKey, setCacheKey
from utils.logging import LoggerWithPrefix
from utils.text import formatSeconds, truncate, transliterate
import models.config
import models.discord
import models.plex
import requests
import threading
import time
import urllib.parse

def initiateAuth() -> tuple[str, str, str]:
	response = requests.post("https://plex.tv/api/v2/pins.json?strong=true", headers = {
		"X-Plex-Product": name,
		"X-Plex-Client-Identifier": plexClientID,
	})
	response.raise_for_status()
	data = response.json()
	pinId = data.get("id")
	code = data.get("code")
	if not pinId or not code:
		raise ValueError(f"Unexpected response from Plex auth API: missing 'id' or 'code' (got: {data})")
	queryString = urllib.parse.urlencode({
		"clientID": plexClientID,
		"code": code,
		"context[device][product]": name,
	})
	authUrl = f"https://app.plex.tv/auth#?{queryString}"
	return str(pinId), str(code), authUrl

def getAuthToken(id: str, code: str) -> Optional[str]:
	response = requests.get(f"https://plex.tv/api/v2/pins/{id}.json?code={code}", headers = {
		"X-Plex-Client-Identifier": plexClientID,
	})
	response.raise_for_status()
	token = response.json().get("authToken")
	if not token or not isinstance(token, str):
		return None
	return token

mediaTypeActivityTypeMap = {
	"movie": models.discord.ActivityType.WATCHING,
	"episode": models.discord.ActivityType.WATCHING,
	"live_episode": models.discord.ActivityType.WATCHING,
	"track": models.discord.ActivityType.LISTENING,
	"clip": models.discord.ActivityType.WATCHING,
}
buttonTypeGuidTypeMap = {
	"imdb": "imdb",
	"tmdb": "tmdb",
	"thetvdb": "tvdb",
	"trakt": "tmdb",
	"letterboxd": "tmdb",
	"musicbrainz": "mbid",
}

class PlexAlertListener(threading.Thread):

	productName = "Plex Media Server"
	updateTimeoutTimerInterval = 30
	connectionCheckTimerInterval = 60
	disconnectTimerInterval = 3
	maximumIgnores = 2

	def __init__(self, token: str, serverConfig: models.config.Server):
		super().__init__()
		self.daemon = True
		self.token = token
		self.serverConfig = serverConfig
		self.logger = LoggerWithPrefix(f"[{self.serverConfig['name']}] ")
		self.discordIpcService = DiscordIpcService(self.serverConfig.get("ipcPipeNumber"))
		self.updateTimeoutTimer: Optional[threading.Timer] = None
		self.connectionCheckTimer: Optional[threading.Timer] = None
		self.disconnectTimer: Optional[threading.Timer] = None
		self.account: Optional[MyPlexAccount] = None
		self.server: Optional[PlexServer] = None
		self.alertListener: Optional[AlertListener] = None
		self.lastState, self.lastSessionKey, self.lastRatingKey = "", 0, 0
		self.listenForUser, self.isServerOwner, self.ignoreCount = "", False, 0
		self._reconnectEvent = threading.Event()
		self._stopped = False
		self.start()

	def run(self) -> None:
		while not self._stopped:
			self._reconnectEvent.clear()
			try:
				self.logger.info("Signing into Plex")
				self.account = MyPlexAccount(token = self.token)
				self.logger.info("Signed in as Plex user '%s'", self.account.username)
				self.listenForUser = self.serverConfig.get("listenForUser", "") or self.account.username
				self.server = None
				for resource in self.account.resources():
					if resource.product == self.productName and resource.name.lower() == self.serverConfig["name"].lower():
						self.logger.info("Connecting to %s '%s'", self.productName, self.serverConfig["name"])
						self.server = resource.connect()
						try:
							self.server.account()
							self.isServerOwner = True
						except Exception:
							self.logger.debug("Could not confirm server ownership (may be a managed/shared server)")
						self.logger.info("Connected to %s '%s'", self.productName, resource.name)
						self.alertListener = AlertListener(self.server, self.tryHandleAlert, self.reconnect)
						self.alertListener.start()
						self.logger.info("Listening for alerts from user '%s'", self.listenForUser)
						self.connectionCheckTimer = threading.Timer(self.connectionCheckTimerInterval, self.connectionCheck)
						self.connectionCheckTimer.start()
						# Wait until a reconnect is signalled or the thread is stopped
						self._reconnectEvent.wait()
						break
				else:
					raise Exception("Server not found")
			except Exception as e:
				if self._stopped:
					break
				self.logger.error("Failed to connect to %s '%s': %s", self.productName, self.serverConfig["name"], e)
				self.logger.error("Reconnecting in 10 seconds")
				time.sleep(10)

	def disconnect(self) -> None:
		self._stopped = True
		self._reconnectEvent.set()
		if self.alertListener:
			try:
				self.alertListener.stop()
			except:
				pass
		self.disconnectRpc()
		if self.connectionCheckTimer:
			self.connectionCheckTimer.cancel()
			self.connectionCheckTimer = None
		self.account, self.server, self.alertListener, self.listenForUser, self.isServerOwner, self.ignoreCount = None, None, None, "", False, 0
		self.logger.info("Stopped listening for alerts")

	def reconnect(self, exception: Exception) -> None:
		self.logger.error("Connection to Plex lost: %s", exception)
		if self.alertListener:
			try:
				self.alertListener.stop()
			except:
				pass
		self.disconnectRpc()
		if self.connectionCheckTimer:
			self.connectionCheckTimer.cancel()
			self.connectionCheckTimer = None
		self.account, self.server, self.alertListener, self.listenForUser, self.isServerOwner, self.ignoreCount = None, None, None, "", False, 0
		self.logger.error("Reconnecting")
		# Signal run() to restart its loop — no recursive call needed
		self._reconnectEvent.set()

	def disconnectRpc(self) -> None:
		self.lastState, self.lastSessionKey, self.lastRatingKey = "", 0, 0
		if self.discordIpcService.connected:
			self.discordIpcService.disconnect()
		if self.updateTimeoutTimer:
			self.updateTimeoutTimer.cancel()
			self.updateTimeoutTimer = None

	def updateTimeout(self) -> None:
		self.logger.debug("No recent updates from session key %s", self.lastSessionKey)
		self.disconnectRpc()

	def connectionCheck(self) -> None:
		try:
			self.logger.debug("Running periodic connection check")
			self.server.clients()
		except Exception as e:
			self.reconnect(e)
		else:
			self.connectionCheckTimer = threading.Timer(self.connectionCheckTimerInterval, self.connectionCheck)
			self.connectionCheckTimer.start()

	def tryHandleAlert(self, alert: models.plex.Alert) -> None:
		try:
			self.handleAlert(alert)
		except:
			self.logger.exception("An unexpected error occurred in the Plex alert handler")
			self.disconnectRpc()

	def uploadToImgur(self, thumb: str) -> Optional[str]:
		thumbUrl = getCacheKey(thumb)
		if not thumbUrl or not isinstance(thumbUrl, str):
			self.logger.debug("Uploading image to Imgur")
			thumbUrl = uploadToImgur(self.server.url(thumb, True))
			setCacheKey(thumb, thumbUrl)
		return thumbUrl

	# ------------------------------------------------------------------
	# Alert handling — orchestrator + focused builder helpers
	# ------------------------------------------------------------------

	def handleAlert(self, alert: models.plex.Alert) -> None:
		"""Top-level alert handler: filters, deduplicates, then builds and sends the activity."""
		if alert["type"] != "playing" or "PlaySessionStateNotification" not in alert:
			return
		stateNotification = alert["PlaySessionStateNotification"][0]
		self.logger.debug("Received alert: %s", stateNotification)

		ratingKey = int(stateNotification["ratingKey"])
		state = stateNotification["state"]
		sessionKey = int(stateNotification["sessionKey"])
		viewOffset = int(stateNotification["viewOffset"])

		item = self.server.fetchItem(ratingKey)
		mediaType = "live_episode" if (item.key and item.key.startswith("/livetv")) else item.type

		if mediaType not in mediaTypeActivityTypeMap:
			self.logger.debug("Unsupported media type '%s', ignoring", mediaType)
			return

		if not self._isLibraryAllowed(item):
			return

		isIgnorableState = state == "stopped" or (state == "paused" and not config["display"]["paused"])

		if not self._shouldUpdate(sessionKey, ratingKey, state, isIgnorableState):
			return

		if not self._isSessionForListenUser(sessionKey):
			return

		# Commit session tracking state and reset timers
		self._resetUpdateTimer()
		if self.disconnectTimer:
			self.disconnectTimer.cancel()
			self.disconnectTimer = None
		self.lastState, self.lastSessionKey, self.lastRatingKey = state, sessionKey, ratingKey

		activity = self._buildActivity(item, mediaType, state, viewOffset)

		if not self.discordIpcService.connected:
			self.discordIpcService.connect()
		if self.discordIpcService.connected:
			self.discordIpcService.setActivity(activity)

	def _isLibraryAllowed(self, item) -> bool:
		"""Return False if the item's library is blacklisted or not whitelisted."""
		try:
			libraryName = item.section().title
		except:
			libraryName = "ERROR"
		if "blacklistedLibraries" in self.serverConfig and libraryName in self.serverConfig["blacklistedLibraries"]:
			self.logger.debug("Library '%s' is blacklisted, ignoring", libraryName)
			return False
		if "whitelistedLibraries" in self.serverConfig and libraryName not in self.serverConfig["whitelistedLibraries"]:
			self.logger.debug("Library '%s' is not whitelisted, ignoring", libraryName)
			return False
		return True

	def _shouldUpdate(self, sessionKey: int, ratingKey: int, state: str, isIgnorableState: bool) -> bool:
		"""
		Apply deduplication logic. Returns True if the alert should proceed to activity update.
		May schedule a disconnect timer as a side effect when transitioning to a stopped/paused state.
		"""
		if self.lastSessionKey == sessionKey and self.lastRatingKey == ratingKey:
			if self.updateTimeoutTimer:
				self.updateTimeoutTimer.cancel()
				self.updateTimeoutTimer = None
			if self.lastState == state and self.ignoreCount < self.maximumIgnores:
				self.logger.debug("Nothing changed, ignoring")
				self.ignoreCount += 1
				self.updateTimeoutTimer = threading.Timer(self.updateTimeoutTimerInterval, self.updateTimeout)
				self.updateTimeoutTimer.start()
				return False
			self.ignoreCount = 0
			if isIgnorableState:
				if self.disconnectTimer:
					self.disconnectTimer.cancel()
				self.disconnectTimer = threading.Timer(self.disconnectTimerInterval, self.disconnectRpc)
				self.disconnectTimer.start()
				return False
		elif isIgnorableState:
			self.logger.debug("Received '%s' state alert from unknown session, ignoring", state)
			return False
		return True

	def _isSessionForListenUser(self, sessionKey: int) -> bool:
		"""
		When this client is the server owner, verify the session belongs to the configured user.
		Always returns True for non-owner clients (session list is not accessible).
		"""
		if not self.isServerOwner:
			return True
		self.logger.debug("Searching sessions for session key %s", sessionKey)
		sessions = self.server.sessions()
		if not sessions:
			self.logger.debug("Empty session list, ignoring")
			return False
		for session in sessions:
			self.logger.debug("%s, Session Key: %s, Usernames: %s", session, session.sessionKey, session.usernames)
			if session.sessionKey == sessionKey:
				self.logger.debug("Session found")
				sessionUsername = session.usernames[0]
				if sessionUsername.lower() == self.listenForUser.lower():
					self.logger.debug("Username '%s' matches '%s', continuing", sessionUsername, self.listenForUser)
					return True
				self.logger.debug("Username '%s' doesn't match '%s', ignoring", sessionUsername, self.listenForUser)
				return False
		self.logger.debug("No matching session found, ignoring")
		return False

	def _resetUpdateTimer(self) -> None:
		"""Cancel any existing update-timeout timer and start a fresh one."""
		if self.updateTimeoutTimer:
			self.updateTimeoutTimer.cancel()
		self.updateTimeoutTimer = threading.Timer(self.updateTimeoutTimerInterval, self.updateTimeout)
		self.updateTimeoutTimer.start()

	def _buildMediaMetadata(self, item, mediaType: str) -> tuple[str, str, str, str, str, str, list[str]]:
		"""
		Extract display metadata for the given media type.

		Returns:
			(title, shortTitle, thumb, smallThumb, largeText, smallText, stateStrings)
		"""
		stateStrings: list[str] = []
		largeText = thumb = smallText = smallThumb = ""

		if config["display"]["duration"] and item.duration and mediaType != "track":
			stateStrings.append(formatSeconds(item.duration / 1000))

		if mediaType == "movie":
			title = shortTitle = item.title
			if config["display"]["year"] and item.year:
				title += f" ({item.year})"
			if config["display"]["genres"] and item.genres:
				genres: list[Genre] = item.genres[:3]
				stateStrings.append(", ".join(genre.tag for genre in genres))
			thumb = item.thumb

		elif mediaType == "episode":
			title = shortTitle = item.grandparentTitle
			if config["display"]["year"]:
				grandparent = self.server.fetchItem(item.grandparentRatingKey)
				if grandparent.year:
					title += f" ({grandparent.year})"
			stateStrings.append(f"S{item.parentIndex:02}E{item.index:02}")
			stateStrings.append(item.title)
			thumb = item.grandparentThumb

		elif mediaType == "live_episode":
			title = shortTitle = item.grandparentTitle
			if item.title != item.grandparentTitle:
				stateStrings.append(item.title)
			thumb = item.grandparentThumb

		elif mediaType == "track":
			title = shortTitle = item.title
			if config["display"]["album"]:
				largeText = item.parentTitle
				if config["display"]["year"]:
					parent = self.server.fetchItem(item.parentRatingKey)
					if parent.year:
						largeText = f"{truncate(largeText, 110)} ({parent.year})"
			if config["display"]["albumImage"]:
				thumb = item.thumb
			if config["display"]["artist"]:
				stateStrings.append(item.originalTitle or item.grandparentTitle)
			if config["display"]["artistImage"]:
				smallText = item.grandparentTitle or item.originalTitle
				smallThumb = item.grandparentThumb

		else:
			title = shortTitle = item.title
			thumb = item.thumb

		return title, shortTitle, thumb, smallThumb, largeText, smallText, stateStrings

	def _buildButtons(self, item, mediaType: str, shortTitle: str) -> list[models.discord.ActivityButton]:
		"""Resolve configured buttons, substituting dynamic URL placeholders with real URLs."""
		guidsRaw: list[Guid] = []
		if mediaType in ["movie", "track"]:
			guidsRaw = item.guids
		elif mediaType == "episode":
			guidsRaw = self.server.fetchItem(item.grandparentRatingKey).guids
		guids: dict[str, str] = {
			parts[0]: parts[1]
			for parts in (guid.id.split("://") for guid in guidsRaw)
			if len(parts) > 1
		}

		buttons: list[models.discord.ActivityButton] = []
		for button in config["display"]["buttons"]:
			if "mediaTypes" in button and mediaType not in button["mediaTypes"]:
				continue
			label = truncate(button["label"].format(title=transliterate(shortTitle)), 30)
			if not button["url"].startswith("dynamic:"):
				buttons.append({"label": label, "url": button["url"]})
				continue
			url = self._resolveDynamicButtonUrl(button["url"][8:], mediaType, guids)
			if url:
				buttons.append({"label": label, "url": url})
		return buttons[:2]

	def _resolveDynamicButtonUrl(self, buttonType: str, mediaType: str, guids: dict[str, str]) -> str:
		"""Map a dynamic button type name to a fully-qualified external URL."""
		guidType = buttonTypeGuidTypeMap.get(buttonType)
		if not guidType:
			return ""
		guid = guids.get(guidType)
		if not guid:
			return ""
		if buttonType == "imdb":
			return f"https://www.imdb.com/title/{guid}"
		if buttonType == "tmdb":
			segment = "movie" if mediaType == "movie" else "tv"
			return f"https://www.themoviedb.org/{segment}/{guid}"
		if buttonType == "thetvdb":
			segment = "movie" if mediaType == "movie" else "series"
			return f"https://www.thetvdb.com/dereferrer/{segment}/{guid}"
		if buttonType == "trakt":
			idType = "movie" if mediaType == "movie" else "show"
			return f"https://trakt.tv/search/tmdb/{guid}?id_type={idType}"
		if buttonType == "letterboxd" and mediaType == "movie":
			return f"https://letterboxd.com/tmdb/{guid}"
		if buttonType == "musicbrainz":
			return f"https://musicbrainz.org/track/{guid}"
		return ""

	def _buildTimestamps(self, state: str, viewOffset: int, itemDuration) -> Optional[models.discord.ActivityTimestamps]:
		"""Build Discord timestamp payload for progress bar display (playing state only)."""
		if state != "playing" or not itemDuration:
			return None
		currentTimestamp = int(time.time() * 1000)
		progressMode = config["display"]["progressMode"]
		if progressMode == "elapsed":
			return {"start": round(currentTimestamp - viewOffset)}
		if progressMode == "remaining":
			return {"end": round(currentTimestamp + (itemDuration - viewOffset))}
		if progressMode == "bar":
			return {
				"start": round(currentTimestamp - viewOffset),
				"end": round(currentTimestamp + (itemDuration - viewOffset)),
			}
		return None

	def _buildActivity(self, item, mediaType: str, state: str, viewOffset: int) -> models.discord.Activity:
		"""Assemble the full Discord activity payload from media metadata and config."""
		title, shortTitle, thumb, smallThumb, largeText, smallText, stateStrings = self._buildMediaMetadata(item, mediaType)

		# Progress text for non-playing states (not applicable to tracks)
		if state != "playing" and mediaType != "track":
			progressMode = config["display"]["progressMode"]
			if progressMode == "remaining":
				stateStrings.append(f"{formatSeconds((item.duration - viewOffset) / 1000, ':')} left")
			else:
				stateStrings.append(f"{formatSeconds(viewOffset / 1000, ':')} elapsed")
			if not config["display"]["statusIcon"]:
				stateStrings.append(state.capitalize())

		stateText = " · ".join(s for s in stateStrings if s)

		postersEnabled = config["display"]["posters"]["enabled"]
		thumbUrl = self.uploadToImgur(thumb) if thumb and postersEnabled else ""
		smallThumbUrl = self.uploadToImgur(smallThumb) if smallThumb and postersEnabled else ""

		activity: models.discord.Activity = {
			"type": mediaTypeActivityTypeMap[mediaType],
			"details": truncate(title, 120),
		}

		if config["display"]["statusIcon"]:
			smallText = smallText or state.capitalize()
			smallThumbUrl = smallThumbUrl or state

		if largeText or thumbUrl or smallText or smallThumbUrl:
			activity["assets"] = {}
			if largeText:
				activity["assets"]["large_text"] = truncate(largeText, 120)
			if thumbUrl:
				activity["assets"]["large_image"] = thumbUrl
			if smallText:
				activity["assets"]["small_text"] = truncate(smallText, 120)
			if smallThumbUrl:
				activity["assets"]["small_image"] = smallThumbUrl

		if stateText:
			activity["state"] = truncate(stateText, 120)

		if config["display"]["buttons"]:
			buttons = self._buildButtons(item, mediaType, shortTitle)
			if buttons:
				activity["buttons"] = buttons

		timestamps = self._buildTimestamps(state, viewOffset, item.duration)
		if timestamps:
			activity["timestamps"] = timestamps

		return activity
