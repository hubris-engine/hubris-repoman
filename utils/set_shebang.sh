#!/usr/bin/env bash
set -e

# Path to this script's parent directory
SCRIPT_DIR=$(dirname ${BASH_SOURCE})

# Path to the repo's root directory
REPO_ROOT=${SCRIPT_DIR}/../..

# Path to the tools directory
TOOLS_ROOT=${REPO_ROOT}/tools

# Path to the python tool
PYTHON_TOOL=${TOOLS_ROOT}/deps/python.sh

# Path to the python script
PYTHON_SCRIPT=${SCRIPT_DIR}/scripts/set_shebang.py

# Invoke the python script and forward in given args
"${BASH}" "${PYTHON_TOOL}" "${PYTHON_SCRIPT}" $@

# Forward exit code
exit $?
