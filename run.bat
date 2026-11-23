@echo off
cd /d "%~dp0"
where py >nul 2>&1
if %errorlevel%==0 (set "PY=py -3") else (set "PY=python")
%PY% -c "import PIL" >nul 2>&1 || %PY% -m pip install --quiet pillow
%PY% ascii.py %*
pause
