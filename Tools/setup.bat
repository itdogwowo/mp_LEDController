@echo off
powershell -Command "Start-Process powershell -Verb runAs"
py -m venv venv
call .\venv\Scripts\activate.bat
pip list 
pip install -r requirement.txt
pip list 
pause