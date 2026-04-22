from config.constants import discordClientID, isUnix, processID, ipcPipeBase
from typing import Any, Optional
from utils.logging import logger
import asyncio
import json
import models.discord
import os
import struct
import time

class DiscordIpcService:

	def __init__(self, pipeNumber: Optional[int]):
		pipeNumber = pipeNumber or -1
		pipeNumbers = range(10) if pipeNumber == -1 else [pipeNumber]
		self.pipes: list[str] = []
		for pipeNumber in pipeNumbers:
			pipeFilename = f"discord-ipc-{pipeNumber}"
			self.pipes.append(os.path.join(ipcPipeBase, pipeFilename))
			self.pipes.append(os.path.join(ipcPipeBase, "app", "com.discordapp.Discord", pipeFilename))
			self.pipes.append(os.path.join(ipcPipeBase, ".flatpak", "com.discordapp.Discord", "xdg-run", pipeFilename))
		self.loop: Optional[asyncio.AbstractEventLoop] = None
		self.pipeReader: Optional[asyncio.StreamReader] = None
		self.pipeWriter: Optional[asyncio.StreamWriter] = None
		self.connected = False

	async def handshake(self) -> None:
		if not self.loop:
			return
		for pipe in self.pipes:
			try:
				if isUnix:
					self.pipeReader, self.pipeWriter = await asyncio.open_unix_connection(pipe) # pyright: ignore[reportAttributeAccessIssue,reportUnknownMemberType]
				else:
					self.pipeReader = asyncio.StreamReader()
					self.pipeWriter = (await self.loop.create_pipe_connection(lambda: asyncio.StreamReaderProtocol(self.pipeReader), pipe))[0] # pyright: ignore[reportAttributeAccessIssue,reportUnknownMemberType,reportArgumentType]
				self.write(0, { "v": 1, "client_id": discordClientID })
				if await self.read():
					self.connected = True
					logger.info(f"Connected to Discord IPC pipe {pipe}")
					break
			except FileNotFoundError:
				pass
			except Exception:
				logger.exception(f"An unexpected error occurred while connecting to Discord IPC pipe {pipe}")
		if not self.connected:
			logger.error(f"Discord IPC pipe not found (attempted pipes: {', '.join(self.pipes)})")

	async def read(self) -> Optional[Any]:
		if not self.pipeReader:
			return
		try:
			dataBytes = await self.pipeReader.read(1024)
			data = json.loads(dataBytes[8:].decode("utf-8"))
			logger.debug("[READ] %s", data)
			return data
		except Exception:
			logger.exception("An unexpected error occurred during an IPC read operation")
			self.connected = False

	def write(self, op: int, payload: Any) -> None:
		if not self.pipeWriter:
			return
		try:
			logger.debug("[WRITE] %s", payload)
			payload = json.dumps(payload)
			self.pipeWriter.write(struct.pack("<ii", op, len(payload)) + payload.encode("utf-8"))
		except Exception:
			logger.exception("An unexpected error occurred during an IPC write operation")
			self.connected = False

	def connect(self) -> None:
		if self.connected:
			logger.warning("Attempt to connect to Discord IPC pipe while already connected")
			return
		logger.info("Connecting to Discord IPC pipe")
		self.loop = asyncio.new_event_loop()
		self.loop.run_until_complete(self.handshake())

	def disconnect(self) -> None:
		if not self.connected:
			logger.warning("Attempt to disconnect from Discord IPC pipe while not connected")
			return
		logger.info("Disconnecting from Discord IPC pipe")
		loop, writer = self.loop, self.pipeWriter
		self.connected = False
		self.pipeReader = None
		self.pipeWriter = None
		self.loop = None
		if writer:
			try:
				writer.close()
				if loop:
					# wait_closed() flushes buffers and releases OS resources cleanly.
					# Reading from the reader after closing the writer causes spurious
					# errors on Windows named pipes, so we do not do that here.
					loop.run_until_complete(writer.wait_closed())
			except Exception:
				logger.exception("An unexpected error occurred while closing the IPC pipe writer")
		if loop:
			try:
				loop.close()
			except Exception:
				logger.exception("An unexpected error occurred while closing the asyncio event loop")

	def setActivity(self, activity: models.discord.Activity) -> None:
		if not self.connected:
			logger.warning("Attempt to set activity while not connected to Discord IPC pipe")
			return
		if not self.loop:
			return
		logger.info("Activity update: %s", activity)
		payload = {
			"cmd": "SET_ACTIVITY",
			"args": {
				"pid": processID,
				"activity": activity,
			},
			"nonce": "{0:.2f}".format(time.time()),
		}
		self.write(1, payload)
		self.loop.run_until_complete(self.read())
