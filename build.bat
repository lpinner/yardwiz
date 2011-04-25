@echo off
rmdir /S /Q %~dp0build
rmdir /S /Q %~dp0dist
python.exe %~dp0setup.py py2exe
python.exe %~dp0setup.py sdist
rmdir /S /Q %~dp0build
pause
