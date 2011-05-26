@echo off
rmdir /S /Q %~dp0dist
python.exe %~dp0setup.py py2exe
python.exe %~dp0setup.py sdist
python.exe %~dp0build-yardwiz-linux.py
pause
