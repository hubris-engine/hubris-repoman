import subprocess
from .error import DepGetError

class Pacman_AptGet:
	def _popen(self, args : "list[str]", stdout=None) -> subprocess.Popen :
		command = [
			self._exec_path
		]
		command.extend(args)
		proc = subprocess.Popen(command, stdout=stdout, universal_newlines=True)
		return proc

	def _popen_install(self, package_name : str, stdout=None) -> subprocess.Popen :
		return self._popen(["install", package_name], stdout=stdout)

	def install(self, package_name : str) -> bool :
		f = open("_depget.log", "a")
		try:
			proc = self._popen_install(package_name, stdout=f)
			proc_result = proc.wait()
			f.close()
			return proc_result == 0
		except FileNotFoundError:
			raise DepGetError("Invalid package manner")

	def search(self, package_name : str):
		return ""

	def __init__(self):
		self.name = "apt-get"
		self.valid = True
		self._exec_path = "apt-get"
