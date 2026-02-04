@echo off
setlocal
cd /d %~dp0

REM Copy example config if missing
if not exist config.ini (
  copy config.ini.example config.ini >nul
)

REM Usage:
REM   run_cli.bat input\my.mp4
REM   run_cli.bat "input\*.mp4"

set IN=%1
if "%IN%"=="" (
  echo Please pass input mp4 path or glob.
  exit /b 2
)

python app\main_cli.py --config config.ini --input %IN% --out out
