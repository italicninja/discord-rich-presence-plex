"""
Resource path utilities for PyInstaller compatibility
"""

import os
import sys

def get_resource_path(relative_path: str) -> str:
	"""
	Get absolute path to resource, works for dev and for PyInstaller

	When running as a PyInstaller executable, resources are extracted to a temp folder.
	This function returns the correct path whether running from source or as .exe

	Args:
		relative_path: Path relative to the application root

	Returns:
		Absolute path to the resource
	"""
	try:
		# PyInstaller creates a temp folder and stores path in _MEIPASS
		base_path = sys._MEIPASS # type: ignore
	except AttributeError:
		# Running from source
		base_path = os.path.abspath(".")

	return os.path.join(base_path, relative_path)

def is_frozen() -> bool:
	"""
	Check if running as a PyInstaller executable

	Returns:
		True if running as frozen executable, False if running from source
	"""
	return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')
