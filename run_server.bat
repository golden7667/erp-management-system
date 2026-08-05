@echo off
title Smart College ERP - Development Server
echo ========================================================
echo         Smart College ERP - Starting Django Server      
echo ========================================================
echo.
python manage.py runserver 0.0.0.0:8000
pause
