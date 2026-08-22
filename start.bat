@echo off
chcp 65001 > nul
echo ===================================================
echo   Запуск Telegram-бота та веб-додатка для Марії
echo ===================================================
echo.

if not exist venv (
    echo [1/3] Перевірка залежностей...
    python -m pip install -r requirements.txt
)

echo [2/3] Запуск сервера та бота...
python main.py

pause
