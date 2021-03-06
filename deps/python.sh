#!/usr/bin/env bash
set -e

DEFAULT_PYTHON_TOOL="python3"

# Path to this script's parent directory
SCRIPT_DIR=$(dirname ${BASH_SOURCE})

# Path to the repo's root directory
REPO_ROOT=${SCRIPT_DIR}/../..

# Path to the tools directory
TOOLS_ROOT=${REPO_ROOT}/tools

# Use a reasonable default if no PYTHON env variable is defined
if [[ -z "$PYTHON" ]]; then
	PYTHON_TOOL="${DEFAULT_PYTHON_TOOL}"
else
	# Fix path seperators
	PYTHON_TOOL=${PYTHON//\\//}
fi

# Path to the python script
PYTHON_SCRIPT=${SCRIPT_DIR}/scripts/python.py

# Invoke the python script and forward in given args
"${PYTHON_TOOL}" "${PYTHON_SCRIPT}" $@

# Forward exit code
exit $?
