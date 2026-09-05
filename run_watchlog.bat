@echo off
REM ============================================================
REM  WatchLog launcher (Windows)
REM  Double-click this to start watching your WoW combat log.
REM  Leave the window open while you play. Close it (or press
REM  Ctrl+C) when you're done.
REM ============================================================

REM WatchLog will try to auto-detect your WoW Logs folder by
REM checking common install locations. If it can't find yours
REM (a non-default install path or drive), uncomment the second
REM line below and fill in your actual path instead.

python "%~dp0watchlog.py"
REM python "%~dp0watchlog.py" --logs-dir "C:\Program Files (x86)\World of Warcraft\_retail_\Logs"

pause
