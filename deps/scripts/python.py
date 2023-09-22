from ntpath import join
import subprocess
import sys
import os
from pathlib import Path

# Paths to add to for python to look in. These paths should be relative to the root of the repository
# and will be resolved before added to the env.
_ADD_PYTHON_PATHS = [
	"tools/python"
]

# Python executable to use
_PYTHON_TOOL= Path(sys.executable).resolve()

# Resolve the path to this script
exec_script_path = Path(sys.argv[0])
if not exec_script_path.is_absolute():
	exec_script_path = Path.cwd().joinpath(exec_script_path)

# Ensure we resolved it correctly
if not exec_script_path.exists():
	print(f"[Error] Failed to determine the path to this script. Got : {exec_script_path}")
	exit(1)

# Resolve!
exec_script_path = exec_script_path.resolve()

# Path to the repository root folder
repo_root_path = exec_script_path.parent.parent.parent.parent

# Path to the deps folder
deps_directory_path = repo_root_path.joinpath("tools", "deps")

# Path to the deps scripts folder
deps_script_directory_path = deps_directory_path.joinpath("scripts")

# Path to the project's repo directory
project_repo_directory = repo_root_path.joinpath("repo")


# Make sure project repo directory exists
if not project_repo_directory.exists():
	os.mkdir(project_repo_directory)

# Add the project root dir to the python paths
_ADD_PYTHON_PATHS.append(str(project_repo_directory))




# Grab the command line args (excluding path to this script)
args = sys.argv
if len(args) != 0:
	args.pop(0)

# Create custom environment
env = os.environ

# Add REPO_ROOT_PATH to the environment
if env.get("REPO_ROOT_PATH") is not None and env.get("REPO_ROOT_PATH") != str(repo_root_path.as_posix()) : 
	print("[Error] REPO_ROOT_PATH already defined in env!")
	exit(1)
env["REPO_ROOT_PATH"] = str(repo_root_path.as_posix())


def get_python_path_seperator() -> str:
	if sys.platform.startswith("win32"):
		return ";"
	else:
		return ":"

def get_python_paths() -> "list[str]" :
	_SEPERATOR = get_python_path_seperator()
	paths_str = env.get("PYTHONPATH", "")
	raw_paths = paths_str.split(_SEPERATOR)
	paths = []
	for v in raw_paths:
		if len(v) > 0:
			paths.append(v)
	return paths

def set_python_paths(paths : "list[str]"):
	_SEPERATOR = get_python_path_seperator()
	existant_paths = get_python_paths()
	new_paths = existant_paths
	for v in paths:
		if existant_paths.count(v) == 0:
			new_paths.append(v)
	path_str = ""
	for v in new_paths:
		if len(v) > 0:
			path_str += (v + _SEPERATOR)
	env["PYTHONPATH"] = path_str

# Add custom python paths
add_python_paths = []
for v in _ADD_PYTHON_PATHS:
	p = repo_root_path.joinpath(v)
	if not p.exists():
		print(f"[Error] Custom python path entry does not exist! Path : {p}")
		exit(1)
	add_python_paths.append(str(p.as_posix()))
if len(add_python_paths) != 0:
	set_python_paths(add_python_paths)



# Form the command
proc_command = [_PYTHON_TOOL]
if len(args) == 0:
	print("[Error] No arguments were given!")
	exit(1)
proc_command.extend(args)

#print(f"[Info] Running python command {proc_command}")
pp = env.get("PYTHONPATH", "")
#print(f"[Debug] PYTHONPATH = {pp}")

# Create the process
proc = subprocess.Popen(proc_command, env=env, universal_newlines=True)

# Return result of proc
proc_result = proc.wait()
exit(proc_result)
