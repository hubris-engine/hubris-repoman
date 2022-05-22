import subprocess
import pathlib
import os
import hubris

class Pacman_Choco:
	def _popen(self, args : "list[str]", stdout=None) -> subprocess.Popen :
		command = [
			self._exec_path
		]
		command.extend(args)
		command.append("--limitoutput")

		hubris.log_debug(f"Running command {command}")
		proc = subprocess.Popen(command, stdout=stdout)
		return proc

	def install(self, package_name : str) -> bool :

		p = pathlib.Path("_build/depget.log")
		if not p.parent.exists():
			os.mkdir(p.parent)
		
		f = open(str(p), "a")
		proc = self._popen(["install", package_name, "-y"])
		proc_result = proc.wait()
		f.close()

		# On failure, print the log file contents
		if proc_result != 0:
			hubris.log_error(f"choco failed to install a package {package_name}")
			if p.exists():
				data = open(str(p), "r").read()
				hubris.log_error(f"{data}")
			return False

		return proc_result == 0

	def search(self, package_name : str) -> bool :
		proc = self._popen(["search", package_name], subprocess.PIPE)
		pout, perr = proc.communicate()
		return pout

	def __init__(self):
		self._exec_path = "choco"
		self.name = "choco"
		self.valid = True
