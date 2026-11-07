@echo off
chcp 65001 >nul
title LanScan - IP Tracker

echo =======================================================
echo          LanScan - Мережевий IP-Трекер
echo =======================================================
echo.

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ПОМИЛКА] Python не знайдено в системі!
    echo Будь ласка, встановіть Python 3.9+ з https://www.python.org/
    echo та обов'язково поставте галочку "Add Python to PATH".
    pause
    exit /b 1
)

echo [1/2] Запуск сервера LanScan на http://localhost:8050 ...
start "" http://localhost:8050

echo [2/2] Сервер працює! Щоб зупинити, закрийте це вікно або натисніть Ctrl+C.
echo.
python -m uvicorn lanscan.main:app --host 0.0.0.0 --port 8050
if %errorlevel% neq 0 (
    echo.
    echo [УВАГА] Перевірте наявність необхідних бібліотек:
    echo pip install -r requirements.txt
    pause
)
