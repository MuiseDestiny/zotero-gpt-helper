@echo off
setlocal enabledelayedexpansion

python -m pip freeze > .temp

for /F "usebackq delims=" %%i in ("requirements.txt") do (
    set "pkg_name=%%i"
    REM echo Checking if !pkg_name! is installed...
    findstr /I /C:"!pkg_name!" .temp > nul || (
        REM echo !pkg_name! is not installed
        python -m pip install -r requirements.txt
        exit /B 1
    )
)
del .temp

python main.py
