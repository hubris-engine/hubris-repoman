import sys

class OS:
	windows = "windows",
	linux = "linux"

def get_os() -> "OS | None" :
	s = sys.platform
	if s.startswith("win"):
		return OS.windows
	elif s.startswith("linux"):
		return OS.linux
	else:
		return None

