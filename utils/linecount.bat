@ECHO OFF
SETLOCAL

:: Path to this script's directory
set SCRIPT_DIR=%~dp0

:: Path to the repo's root directory
set REPO_ROOT=%SCRIPT_DIR%/../..

:: Path to the repo tools directory
set TOOLS_ROOT=%REPO_ROOT%/tools

:: Path to the script this redirect into
set PYTHON_SCRIPT_PATH=%SCRIPT_DIR%/scripts/linecount.py

:: Path to the python tool
set USE_PYTHON=%TOOLS_ROOT%/deps/python.bat

:: Invoke the python script
call %USE_PYTHON% %PYTHON_SCRIPT_PATH% %*
exit /B %errorlevel%
