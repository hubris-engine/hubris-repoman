import os
import shutil
import hubris
import hubris.depget as depget

from .cmake import CMake
from .cmake import Compiler as CMakeCompiler

from pathlib import Path



def _install_package(name, exit_on_failure=True):
	if not depget.install(name):
		hubris.log_error(f"Failed to install {name}")
		if exit_on_failure:
			exit(1)
		return False
	else:
		hubris.log_info(f"Installed {name}")
		return True

class RepoMan_Windows:

	_CMAKE_COMPILER = CMakeCompiler.clang
	
	def clean(self):
		for v in self.artifact_paths:
			p = Path(v).resolve()
			if p.exists():
				if p.is_dir():
					shutil.rmtree(p)
				else:
					os.remove(p)
		return True
		
	def getdeps(self,
		exit_on_fail : bool = True):
		# Install packages
		failed = False
		for v in self.deps:
			if not _install_package(v, exit_on_fail):
				failed = True
		return not failed

	def build(self, **tool_args):
		if not self.tool.generate_and_build(**tool_args):
			return False
		return True

	def generate(self, **tool_args):
		if not self.tool.generate(**tool_args):
			return False
		return True

	def just_build(self, **tool_args):
		if not self.tool.build(**tool_args):
			return False

		return True
	def install(self, **tool_args):
		if not self.tool.install(**tool_args):
			return False
		return True

	def __init__(self):
		self.tool = CMake()
		self.compiler = RepoMan_Windows._CMAKE_COMPILER

		# The paths to be cleaned if they exist, relative to repo root
		self.artifact_paths : "list[Path]" = [
		]

		self.deps : "list[str]" = [
		]


