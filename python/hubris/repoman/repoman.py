from .repoman_linux import RepoMan_Linux
from .repoman_windows import RepoMan_Windows

import sys

def _repoman_type():
	if sys.platform.startswith("win32"):
		return RepoMan_Windows
	else:
		return RepoMan_Linux

RepoMan = _repoman_type()
