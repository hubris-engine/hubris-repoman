from subprocess import Popen
from argparse import ArgumentParser
from pathlib import Path
import os
import hubris

# CLI argument help messages
_ARGUMENT_HELP_TARGET = "The target that the link will point to"
_ARGUMENT_HELP_LINK_NAME = "The path/name of the link to create"
_ARGUMENT_HELP_QUIET = "Silences output"
_ARGUMENT_HELP_IGNORE_PERMS = "If the required permissions to create a simlink are not held, the error will be supressed"

# Define the CLI
parser = ArgumentParser(description="Creates a symbolic link")
parser.add_argument("target", type=Path, help = _ARGUMENT_HELP_TARGET)
parser.add_argument("link_name", type=Path, help = _ARGUMENT_HELP_LINK_NAME)
parser.add_argument("--quiet", "-q", action="store_true", help = _ARGUMENT_HELP_QUIET)
parser.add_argument("--ignore_perms", action="store_true", help = _ARGUMENT_HELP_IGNORE_PERMS)

# Parse the command line
args = parser.parse_args()

# Alias local args
target = Path(args.target).resolve()
link_name = Path(args.link_name).resolve()
quiet = args.quiet


# Lower logging level to errors only if quiet mode is on
if quiet:
	hubris.set_log_level(hubris.LogLevel.error)

if not target.exists():
	hubris.log_error(f"Cannot create link as target does not exist. Target = {str(target)}")
	exit(1)

is_dir = False
if target.is_dir():
	is_dir = True

try:
	os.symlink(src = target, dst = link_name, target_is_directory = is_dir)
except FileExistsError:
	hubris.log_warn(f'Link already exists. "{target}" -> "{link_name}"')
except OSError:
	if _ARGUMENT_HELP_IGNORE_PERMS:
		hubris.log_warn("Missing permissions to create symlink")
	else:
		hubris.log_error("Missing permissions to create symlink")
		exit(1)
