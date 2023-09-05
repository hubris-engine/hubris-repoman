import os
from pathlib import Path
import shutil
import subprocess
import argparse
import sys
import hubris

import webbrowser

import hubris.doxy as doxy
from hubris.doxy.doxy import Doxygen

# Path is relative to the repo root
_DOXYGEN_DEFAULT_CONFIG_PATH=Path.cwd().joinpath("tools/doxy/config.doxy")
_DOXYGEN_DEFAULT_OUTPUT_ROOT=Path.cwd().joinpath("_doxygen")

def open_html_file(path : Path):
	hubris.log_debug(f"Opening HTML file {str(path)}")
	
	new = 2 # open in a new tab, if possible
	# open an HTML file on my own (Windows) computer
	url = f"file://{str(path.resolve())}"

	return webbrowser.open(url,new=new)

parser = argparse.ArgumentParser(description="Runs doxygen")
parser.add_argument("doxygen_config_path", help="Path to the doxygen config file", default=_DOXYGEN_DEFAULT_CONFIG_PATH, type=Path)
parser.add_argument("--no_clean", help="Prevents cleaning the generated doxygen output", action="store_true", default=False)
parser.add_argument("--open", help="Causes the generated doxygen to be opened in the browers (only tested on windows)",
	action="store_true")
parser.add_argument("--show_output", help="Causes doxygen output messages to be written to the terminal.",
	action="store_true")
args = parser.parse_args()

out_root = Path.cwd().joinpath("_doxygen")


# If output root exists and we are allowed to clean it, clean it.
if out_root.exists():
	if not args.no_clean:
		shutil.rmtree(out_root)

# Make sure output root exists
if not out_root.exists():
	os.makedirs(out_root)



doxygen = doxy.Doxygen()

doxygen_config_path = Path(args.doxygen_config_path)
if not doxygen_config_path.exists():
	hubris.log_error(f"Doxygen config doesn't exist! Path = {str(_DOXYGEN_DEFAULT_CONFIG_PATH)}")
	exit(1)

doxygen_config = doxy.DoxygenConfig(doxygen_config_path)
doxygen_generated_config_path = _DOXYGEN_DEFAULT_OUTPUT_ROOT.joinpath(doxygen_config_path.name)

doxygen_output_root = _DOXYGEN_DEFAULT_OUTPUT_ROOT
doxygen_log_file_path = doxygen_output_root.joinpath("log.txt")
doxygen_warn_log_file_path = doxygen_log_file_path.with_name("warning_log.txt")


doxygen_config.set("OUTPUT_DIRECTORY", str(doxygen_output_root.as_posix()))
doxygen_config.set("WARN_LOGFILE", str(doxygen_warn_log_file_path.as_posix()))

doxygen_config.set_path(doxygen_generated_config_path)
doxygen_config.save()

doxygen_html_output_path = "".join(doxygen_config.get_value("HTML_OUTPUT"))
doxygen_html_output_path = doxygen_output_root.joinpath(doxygen_html_output_path, "index.html").resolve()
hubris.log_debug(doxygen_html_output_path)

log_file = open(doxygen_log_file_path, "w")
proc_result = doxygen.generate(doxygen_config, stdout=log_file)

if not proc_result:
	hubris.log_error(f"Doxygen generate step failed! Log file path = {str(doxygen_warn_log_file_path)}")
	exit(1)

if args.open:
	open_html_file(doxygen_html_output_path)

exit(proc_result)
