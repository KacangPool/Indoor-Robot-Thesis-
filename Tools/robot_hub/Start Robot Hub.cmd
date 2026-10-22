@echo off
setlocal
set "hub_python=%LOCALAPPDATA%\Python\pythoncore-3.11-64\python.exe"
if exist "%hub_python%" goto run
set "hub_python=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
if exist "%hub_python%" goto run
set "hub_python=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if exist "%hub_python%" goto run
echo Python 3.11 with Tkinter was not found. Install the normal Windows Python distribution, then try again.
pause
exit /b 1
:run
"%hub_python%" "%~dp0bootstrap.py" %*
if errorlevel 1 pause
