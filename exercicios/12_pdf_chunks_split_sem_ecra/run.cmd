@echo off
setlocal
cd /d "%~dp0"
call run_jupyter.cmd %*
