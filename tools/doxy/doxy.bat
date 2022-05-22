@echo off

set USE_PYTHON=tools/deps/python.bat
set SCRIPT=tools/doxy/scripts/doxy_cli.py

call %USE_PYTHON% %SCRIPT% %*
if %errorlevel% == 1 ( goto on_fail )

:on_pass
exit /B 0

:on_fail
exit /B 1
