#
# Basic package manager middleman
#

import os
import pathlib
import subprocess
import sys
import hubris

from .choco import Pacman_Choco
from .apt_get import Pacman_AptGet
from .error import DepGetError


Pacman = None
def _get_pacman_type():
	global Pacman
	if Pacman is None:
		# See https://docs.python.org/3/library/sys.html#sys.platform
		platform_str = sys.platform
		if platform_str.startswith("win32"):
			# Windows
			# Using chocolatey as the github virtual windows runner has Choco
			Pacman = Pacman_Choco
		elif platform_str.startswith("linux"):
			# Linux
			Pacman = Pacman_AptGet
		else:
			raise DepGetError("Unsupported platform for depget")
	return Pacman


_PacmanValue = None

def _get_pacman():
	global _PacmanValue
	if _PacmanValue is None:
		_PacmanValue = _get_pacman_type()() 
	# See https://docs.python.org/3/library/sys.html#sys.platform
	return _PacmanValue


# Installs a package using the auto-determined package manager
def install(package_name : str) -> bool :
	_pacman = _get_pacman()
	if _pacman.valid:
		return _pacman.install(package_name)
	else:
		raise DepGetError("Invalid package manager")

# Searches for a package using the auto-determined package manager
def search(package_name : str) -> str :
	_pacman = _get_pacman()
	if _pacman.valid:
		return _pacman.search(package_name)
	else:
		raise DepGetError("Invalid package manager")


def pacman_name() -> str :
	"""Gets the name of the selected package manager, or None if no selection could be made"""
	_pacman = _get_pacman()
	return _pacman.name
