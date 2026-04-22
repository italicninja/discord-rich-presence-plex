from .logging import logger
import sys

def ensure_dependencies() -> None:
	"""
	Compare installed packages against requirements.txt and pip-install any that are
	missing or at the wrong version. Call this at startup before importing application
	modules that depend on third-party packages.

	Errors are logged but never re-raised so a transient pip failure doesn't prevent
	the application from attempting to run with whatever is already installed.
	"""
	try:
		import subprocess
		def _parse_pip_packages(packages_str: str) -> dict[str, str]:
			result: dict[str, str] = {}
			for line in packages_str.splitlines():
				parts = line.split("==", 1)
				result[parts[0].lower()] = parts[1] if len(parts) > 1 else ""
			return result
		pip_freeze = subprocess.run(
			[sys.executable, "-m", "pip", "freeze"],
			stdout = subprocess.PIPE,
			text = True,
			check = True,
		)
		installed = _parse_pip_packages(pip_freeze.stdout)
		with open("requirements.txt", "r", encoding = "UTF-8") as f:
			required = _parse_pip_packages(f.read())
		for package_name, required_version in required.items():
			installed_version = installed.get(package_name, "none")
			if installed_version != required_version:
				logger.info(
					"Installing dependency: %s (required: %s, installed: %s)",
					package_name, required_version, installed_version,
				)
				subprocess.run(
					[sys.executable, "-m", "pip", "install", "-U", f"{package_name}=={required_version}"],
					check = True,
				)
	except Exception:
		logger.exception(
			"An unexpected error occurred during automatic installation of dependencies. "
			"Install them manually by running the following command: python -m pip install -U -r requirements.txt"
		)
