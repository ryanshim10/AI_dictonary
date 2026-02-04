@echo off
setlocal
cd /d %~dp0

REM Copy example config if missing
if not exist config.ini (
  copy config.ini.example config.ini >nul
)

python app\main_gui.py
