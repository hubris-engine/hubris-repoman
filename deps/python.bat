@ECHO OFF
SETLOCAL

:: Path to this script's directory
set SCRIPT_DIR=%~dp0

:: Path to the repo's root directory
set REPO_ROOT=%SCRIPT_DIR%/../..

:: Path to the repo tools directory
set TOOLS_ROOT=%REPO_ROOT%/tools

:: Path to the script this redirect into
set PYTHON_SCRIPT_PATH=%SCRIPT_DIR%/scripts/python.py

:: Use a reasonable default if no PYTHON env variable is defined
IF "%PYTHON%"=="" ( 
    set PYTHON_TOOL=python3
) ELSE (
	set PYTHON_TOOL=%PYTHON%
)

:: Invoke the python script
call %PYTHON_TOOL% %PYTHON_SCRIPT_PATH% %*
exit /B %errorlevel%
