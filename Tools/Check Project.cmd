@echo off
setlocal
set "TASK_PY=%LOCALAPPDATA%\Python\pythoncore-3.11-64\python.exe"
if not exist "%TASK_PY%" set "TASK_PY=python"
"%TASK_PY%" "%~dp0quality_check.py" %*
set "TASK_RESULT=%ERRORLEVEL%"
echo.
echo The report path is printed above. Nothing was uploaded or started on the robot.
pause
exit /b %TASK_RESULT%
