import os
import hubris

from argparse import ArgumentParser
from pathlib import Path

parser = ArgumentParser(description="Generates a batch or shell script that redirects to a python script")
parser.add_argument("py_script", type=Path, help="Path to the python script to redirect into")
parser.add_argument("name", type=Path, help="Name/path for the generated scripts to use, extension will be replaced or added as needed")
parser.add_argument("--shell", "--sh", action="store_true", help="Generates a shell (.sh) script")
parser.add_argument("--batch", "--bat", action="store_true", help="Generates a batch (.bat) script")
parser.add_argument("--repo_root", type=Path, default=Path(os.getenv("REPO_ROOT_PATH", Path.cwd())), help="Path to the repo root directory")
args = parser.parse_args()


def append_values(lines : "list[str]", append : str):
	o = []
	for v in lines:
		o.append(v + append)
	return o




def pyredirect(py_script_path : Path, name : Path, shell : bool, batch : bool, repo_root : Path) -> int :

	# Handle repo path
	try:
		repo_root = repo_root.resolve(True)
	except FileNotFoundError as exc:
		hubris.log_error(f"Cannot find repo root directory, path given = {str(repo_root.as_posix())}")
		return 1
	if not repo_root.is_dir():
		hubris.log_error(f"Repo root path given isn't a directory, path given = {str(repo_root.as_posix())}")
		return 1

	# Handle py_script path
	try:
		py_script_path = py_script_path.resolve(True)
	except FileNotFoundError as exc:
		hubris.log_error(f"Cannot find python script, path given = {str(py_script_path.as_posix())}")
		return 1
	if not py_script_path.is_file():
		hubris.log_error(f"Python script given isn't a regular file, path given = {str(py_script_path.as_posix())}")
		return 1

	# Bool table for if certain file types should be generated
	generate_file_types = {
		"shell" : shell,
		"batch" : batch
	}	
	
	# Determine if we should generate all
	generate_all : bool = True
	for v in generate_file_types.values():
		if v:
			generate_all = False
			break
	if generate_all:
		for k in generate_file_types.keys():
			generate_file_types[k] = True

	# Resolve that path buckaroo
	name = name.resolve(strict=False)

	# Determine the path to the output script relative to the repo root
	name_rel_to_root = name.parent.relative_to(repo_root)
	path_to_repo_root = Path()
	for v in name_rel_to_root.parents:
		path_to_repo_root = path_to_repo_root.joinpath("..")

	# Check determined path
	if name.parent.joinpath(path_to_repo_root).resolve(strict=False) != repo_root:
		hubris.log_error("Failed to determine relative path from output script to repo root")
		return 1
	
	# Determine the path to the output script relative to the repo root
	script_rel_to_name = py_script_path.relative_to(name.parent)
	if name.parent.joinpath(script_rel_to_name).resolve(strict=False) != py_script_path:
		hubris.log_error("Failed to determine relative path from output script to the python script")
		return 1

	# Generate shell script
	if generate_file_types["shell"]:

		# Look for the python tool as a final check of repo path validity
		python_tool_path = repo_root.joinpath("tools", "deps", "python.sh")
		if not python_tool_path.exists():
			hubris.log_error(f"Cannot find python tool, repo root path may be invalid. Looked for {python_tool_path}")
			return 1

		out_path = name.with_suffix(".sh")

		lines = [
			"#!",
			"set -e",
			"",
			"# Path to this script's parent directory",
			"SCRIPT_DIR=$(dirname ${BASH_SOURCE})",
			"",
			"# Path to the repo's root directory",
		 	f"REPO_ROOT=${{SCRIPT_DIR}}/{path_to_repo_root.as_posix()}",
			"",
			"# Path to the tools directory",
			"TOOLS_ROOT=${REPO_ROOT}/tools",
			"",
			"# Path to the python tool",
			"PYTHON_TOOL=${TOOLS_ROOT}/deps/python.sh",
			"",
			"# Path to the python script",
			f"PYTHON_SCRIPT=${{SCRIPT_DIR}}/{script_rel_to_name.as_posix()}",
			"",
			"# Invoke the python script and forward in given args",
			'"${BASH}" "${PYTHON_TOOL}" "${PYTHON_SCRIPT}" $@',
			"",
			"# Forward exit code",
			"exit $?"
		]

		lines = append_values(lines, "\n")

		with open(out_path, "w", newline="\n") as file:
			file.writelines(lines)

	# Generate batch script
	if generate_file_types["batch"]:

		# Look for the python tool as a final check of repo path validity
		python_tool_path = repo_root.joinpath("tools", "deps", "python.bat")
		if not python_tool_path.exists():
			hubris.log_error(f"Cannot find python tool, repo root path may be invalid. Looked for {python_tool_path}")
			return 1

		out_path = name.with_suffix(".bat")
		lines = [
			"@ECHO OFF",
			"SETLOCAL",
			"",
			":: Path to this script's directory",
			"set SCRIPT_DIR=%~dp0",
			"",
			":: Path to the repo's root directory",
			f"set REPO_ROOT=%SCRIPT_DIR%/{path_to_repo_root.as_posix()}",
			"",
			":: Path to the repo tools directory",
			"set TOOLS_ROOT=%REPO_ROOT%/tools",
			"",
			":: Path to the script this redirect into",
			f"set PYTHON_SCRIPT_PATH=%SCRIPT_DIR%/{script_rel_to_name.as_posix()}",
			"",
			":: Path to the python tool",
			"set USE_PYTHON=%TOOLS_ROOT%/deps/python.bat",
			"",
			":: Invoke the python script",
			"call %USE_PYTHON% %PYTHON_SCRIPT_PATH% %*",
			"exit /B %errorlevel%",
		]
		lines = append_values(lines, "\n")
		
		with open(out_path, "w", newline="\n") as file:
			file.writelines(lines)

	return 0

result = pyredirect(
	py_script_path = args.py_script,
	name = args.name,
	shell = args.shell,
	batch = args.batch,
	repo_root = args.repo_root
)

exit(result)
