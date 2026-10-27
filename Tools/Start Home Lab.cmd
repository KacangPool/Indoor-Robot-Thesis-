@echo off
setlocal
cd /d "%~dp0"
set "FahadLabPython=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if exist "%FahadLabPython%" (
  "%FahadLabPython%" home_lab.py --serve
) else (
  py -3.11 home_lab.py --serve
)
pause
