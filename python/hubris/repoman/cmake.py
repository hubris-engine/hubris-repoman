import os
import pathlib
import re
import subprocess
import hubris


_CLANG_WARNING_REGEX = re.compile("warning:")
_CMAKE_FAILED_REGEX = re.compile("FAILED:")
	

class CMakeLogLevel:
	warning="WARNING"
	notice="NOTICE"
	error="ERROR"
	status="STATUS"
	verbose="VERBOSE"
	debug="DEBUG"
	trace="TRACE"

class Compiler:
	clang=0
	gcc=1
	
class _CompilerInfo:
	def __init__(self, c, cpp):
		self.c = c
		self.cpp = cpp

_COMPILER_NAMES = [
	_CompilerInfo("clang", "clang++"),
	_CompilerInfo("gcc", "g++")
]	


_CMAKE_DEFAULT_GENERATOR = "Ninja"
_CMAKE_DEFAULT_COMPILER = Compiler.clang



class CMakeDef:

	def make_def(self) -> str:
		return "-D" + str(self)

	def __str__(self):
		return f"{self.name}={self.value}"

	def __init__(self, name : str, value : "str | bool"):
		self.name = name
		value_type = type(value)
		if value_type == type(str()):
			self.value = value
		elif value_type == type(bool()):
			if value:
				self.value = "ON"
			else:
				self.value = "OFF"

def _make_cmake_generate_command(
	definitions : "list[CMakeDef]" = [],
	generator 	: str | None = None,
	source_root : str = ".",
	build_root 	: str = "_build",
	log_level 	: CMakeLogLevel = "VERBOSE",
	enable_dev_output : bool = False):

	command = ["cmake"]
	if not enable_dev_output:
		command.append("-Wno-dev")

	command.extend([
		"-G", generator or _CMAKE_DEFAULT_GENERATOR,
		"--log-level=" + str(log_level)
	])

	for v in definitions:
		if type(v) == type(""):
			command.append(v)
		else:
			command.append(v.make_def())
	command.extend(["-S", source_root])
	command.extend(["-B", build_root])
	
	return command

def does_generator_support_platform_option(generator : str):
	if generator == "Ninja":
		return False
	else:
		return True



class CMake:

	def generate(self,
		defs : "list[CMakeDef]" = None,
		build_root : "pathlib.Path" = "_build",
		source_root : "pathlib.Path" = ".",
		compiler : Compiler = None,
		env = None,
		generator : str | None = None,
		target_platform : str | None = None):	
		"""
		defs : Additional definitions to give to cmake.
		build_root : Path to the build directory root relative to the repository root dir. 
		"""

		if defs is None:
			defs = []

		build_root = pathlib.Path(build_root)
		source_root = pathlib.Path(source_root)
		generator = generator or _CMAKE_DEFAULT_GENERATOR
		
		# No compiler should be specified for Visual Studio
		if not generator.startswith("Visual Studio"):
			compiler = compiler or _CMAKE_DEFAULT_COMPILER
		else:
			compiler = None

		# Create our custom environment
		_env = env or os.environ

		if not build_root.is_absolute():
			build_root = self._repo_root.joinpath(build_root).resolve()
			hubris.log_debug(f"Resolved CMake build root to {str(source_root)}")
		if not source_root.is_absolute():
			source_root = self._repo_root.joinpath(source_root).resolve()
			hubris.log_debug(f"Resolved CMake source root to {str(build_root)}")

		# If the compiler was specified, set it
		cmake_generate_extra_args = []
		if compiler is not None:
			name = _COMPILER_NAMES[compiler]
			_env["CC"] = name.c
			_env["CXX"] = name.cpp
			cmake_generate_extra_args.append(f"-DCMAKE_C_COMPILER={name.c}")
			cmake_generate_extra_args.append(f"-DCMAKE_CXX_COMPILER={name.cpp}")
			hubris.log_debug(f'CC = {_env["CC"]}')
			hubris.log_debug(f'CXX = {_env["CXX"]}')

		# If the platform parameter was set, add it
		if target_platform is not None:
			if does_generator_support_platform_option(generator):
				cmake_generate_extra_args.extend(['-A', target_platform])
			else:
				cmake_generate_extra_args.extend([f'-DCMAKE_CXX_FLAGS="--target={target_platform}-unknown-unknown"'])

		defs.extend(cmake_generate_extra_args)
		cmake_generate_command = _make_cmake_generate_command(
			defs,
			log_level=CMakeLogLevel.verbose,
			build_root=str(build_root),
			source_root=str(source_root),
			generator=generator
		)
		hubris.log_debug(f"{cmake_generate_command}")

		try:
			result = subprocess.run(cmake_generate_command, env=_env)
		except FileNotFoundError as exc:
			hubris.log_error("Missing cmake, please install it and ensure it is available on the path")
			exit(1)

		if result.returncode == 0:
			return True
		else:
			return False

	def build(self,
		config : "str | None" = None,
		clean_first : bool = False,
		build_root : pathlib.Path = "_build",
		jobs : "int | None" = None,
		hide_warnings : bool = True,
		compiler : Compiler = None,
		target_platform : str | None = None,
		generator : str | None = None):

		build_root = pathlib.Path(build_root)

		generator = generator or _CMAKE_DEFAULT_GENERATOR

		# No compiler should be specified for Visual Studio
		if not generator.startswith("Visual Studio"):
			compiler = compiler or _CMAKE_DEFAULT_COMPILER
		else:
			compiler = None

		# Ensure the build root exists
		if not build_root.exists():
			os.makedirs(build_root)
		log_file_path = build_root.joinpath("log.txt")

		cmake_build_command = [
			"cmake",
			"--build",
			f'"{str(build_root.resolve())}"',
		]
	
		# Set the config if one was specified.
		if config is not None:
			cmake_build_command.extend([
				"--config",
				config
			])

		# If clean_first was specified, add it to the command.
		if clean_first:
			cmake_build_command.append("--clean-first")

		# Set the job count if specified.
		if jobs is not None:
			cmake_build_command.extend([
				"--parallel",
				str(jobs)
			])



		# Run cmake build and redirect output to a file
		log_file = open(log_file_path, "w")
		print(" ".join(cmake_build_command))
		result = subprocess.run(" ".join(cmake_build_command), stdout=log_file)
		log_file.close()

		# Read in the logged information
		log_file_data = open(log_file_path, "r").read()
		warning_match = _CLANG_WARNING_REGEX.search(log_file_data)
		if warning_match:
			for warning in warning_match.groups():
				hubris.log_warn(warning)



		if result.returncode == 0:

			# Check log file for errors
			failed_match = _CMAKE_FAILED_REGEX.search(log_file_data)
			if failed_match:
				hubris.log_error("Failed to build the CMake project")
				hubris.log_error(log_file_data)
				return False

			return True
		else:
			log_file_data = open(log_file_path, "r").read()
			hubris.log_error("Failed to build the CMake project")

			if hide_warnings:
				msg_lines = []
				ignoring = False
				for line in log_file_data.splitlines(False):
					if line.count(" warning: ") != 0:
						ignoring = True
					else:
						if line.count("error") != 0:
							ignoring = False
						if not ignoring:
							msg_lines.append(line)
				msg = "\n".join(msg_lines)
				hubris.log_error(msg)

			else:
				hubris.log_error(log_file_data)
			return False

	def install(self,
		build_root : "pathlib.Path | str" = "_build",
		install_prefix : "pathlib.Path | str" = "_install",
		component : "str | None" = None,
		config : "str | None" = None):

		build_root = pathlib.Path(build_root)
		install_prefix = pathlib.Path(install_prefix)

		cmake_install_command = [
			"cmake",
			"--install",
			str(build_root.resolve()),
			"--prefix",
			str(install_prefix.resolve()),
		]
		hubris.log_debug(f"{cmake_install_command}")

		# Set the component if one was specified.
		if component is not None:
			cmake_install_command.extend([
				"--component", component
			])

		# Set the config if one was specified.
		if config is not None:
			cmake_install_command.extend([
				"--config",
				config
			])

		# Ensure the build root exists
		if not build_root.exists():
			os.makedirs(build_root)
		log_file_path = build_root.joinpath("install_log.txt")

		with open(log_file_path, "w") as logfile:
			result = subprocess.run(cmake_install_command, stdout=logfile)

			# Snag the log output
			log_output = ""
			with open(log_file_path, "r") as f:
				log_output = f.read()
			
			# Report result, log as needed
			if result.returncode == 0:
				hubris.log_debug(log_output)
				return True
			else:
				hubris.log_error(log_output)
				return False

	def generate_and_build(self,
		defs : "list[CMakeDef]" = [],
		build_root : "pathlib.Path" = "_build",
		source_root : "pathlib.Path" = ".",
		compiler : Compiler = Compiler.clang,
		env = None,
		generator : str | None = None,
		target_platform : str | None = None,
		config : "str | None" = None,
		clean_first : bool = False,
		jobs : "int | None" = None,
		hide_warnings : bool = True):

		if not self.generate(
			defs=defs,
			build_root=build_root,
			source_root=source_root,
			compiler=compiler,
			env=env,
			target_platform=target_platform,
			generator=generator
		):
			return False
		
		if not self.build(
			config=config,
			clean_first=clean_first,
			build_root=build_root,
			jobs=jobs,
			hide_warnings=hide_warnings,
			compiler=compiler,
			target_platform=target_platform,
			generator=generator
		):
			return False

		return True


	def __init__(self):
		self._repo_root = os.getenv("REPO_ROOT_PATH")
		if self._repo_root is None:
			raise Exception("Missing REPO_ROOT_PATH environment variable")
		self._repo_root = pathlib.Path(self._repo_root)

