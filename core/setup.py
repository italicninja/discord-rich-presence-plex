"""
Shared container and runtime environment setup logic.

Used by both main.py and main_tray.py to avoid duplication and to ensure
shell commands are executed safely without shell injection risk.
"""

from config.constants import isInContainer, runtimeDirectory, uid, gid, containerCwd, noRuntimeDirChown
from utils.logging import logger
import os
import subprocess
import sys

def _run(args: list[str]) -> None:
	"""Run a system command using subprocess (no shell, no injection risk)."""
	try:
		subprocess.run(args, check=True)
	except Exception as e:
		logger.warning("Command %s failed: %s", args, e)

def configure_container_environment() -> None:
	"""
	Validate and configure the runtime environment when running inside a container.

	- Ensures the Discord IPC runtime directory exists and is mounted.
	- When running as root, adjusts ownership of the runtime and app directories
	  so that the target UID/GID can access them.
	- Drops privileges to the target UID/GID after setup.

	This function is a no-op when not running in a container (isInContainer=False).
	"""
	if not isInContainer:
		return

	if not os.path.isdir(runtimeDirectory):
		logger.error(
			"Runtime directory does not exist. "
			"Ensure that it is mounted into the container at %s",
			runtimeDirectory,
		)
		sys.exit(1)

	if os.geteuid() == 0:  # pyright: ignore[reportAttributeAccessIssue,reportUnknownMemberType]
		_apply_ownership()
		logger.debug("Dropping privileges to uid=%s gid=%s", uid, gid)
		os.setgid(gid)  # pyright: ignore[reportAttributeAccessIssue,reportUnknownMemberType]
		os.setuid(uid)  # pyright: ignore[reportAttributeAccessIssue,reportUnknownMemberType]
	else:
		logger.warning("Not running as the superuser. Manually ensure appropriate ownership of mounted contents")

def _apply_ownership() -> None:
	"""Determine effective UID/GID and apply ownership to runtime/app directories."""
	global uid, gid

	if uid == -1 or gid == -1:
		logger.warning(
			"Environment variable(s) DRPP_UID and/or DRPP_GID are/is not set. "
			"Deriving ownership from existing runtime directory stat."
		)
		stat = os.stat(runtimeDirectory)
		uid, gid = stat.st_uid, stat.st_gid

	if noRuntimeDirChown:
		logger.warning(
			"Environment variable DRPP_NO_RUNTIME_DIR_CHOWN is set to true. "
			"Manually ensure appropriate ownership of %s",
			runtimeDirectory,
		)
	else:
		_run(["chmod", "700", runtimeDirectory])
		_run(["chown", "-R", f"{uid}:{gid}", runtimeDirectory])

	_run(["chown", "-R", f"{uid}:{gid}", containerCwd])
