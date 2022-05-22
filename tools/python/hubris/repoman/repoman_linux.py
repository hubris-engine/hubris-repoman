import os
import shutil

import hubris
import hubris.depget as depget

from .cmake import CMake
from .cmake import Compiler as CMakeCompiler

from pathlib import Path



class RepoMan_Linux:

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

	def getdeps(self, exit_on_fail : bool = True):
		# Install packages
		failed = False
		for v in self.deps:
			if not depget.install(v):
				hubris.log_error(f"Failed to install {v}")
				failed = True
				if exit_on_fail:
					return False
			else:
				hubris.log_info(f"Installed {v}")
		return not failed

	def build(self, **tool_args):
		if not self.tool.generate_and_build(**tool_args):
			return False
		return True

	def install(self, **tool_args):
		if not self.tool.install(**tool_args):
			return False
		return True

	def __init__(self):
		self.tool = CMake()
		self.compiler = RepoMan_Linux._CMAKE_COMPILER

		# The paths to be cleaned if they exist, relative to repo root
		self.artifact_paths : "list[Path]" = [
		]

		self.deps = []

