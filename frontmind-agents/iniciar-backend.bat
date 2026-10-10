@echo off
cd /d "%~dp0"
call venv\Scripts\activate
set FRONTMIND_ENV=development
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8001
pause
