@echo off
echo ========================================================
echo        AUTO COMPRA AMAZON - INSTALADOR Y EJECUTOR
echo ========================================================
echo.
echo Verificando si pip esta disponible...
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] No se pudo encontrar 'pip'. 
    echo Asegurate de tener Python instalado y marcar la opcion "Add Python to PATH" durante la instalacion.
    pause
    exit /b
)

echo Instalando / Actualizando dependencias necesarias...
python -m pip install -r requirements.txt
echo.

echo ========================================================
echo Iniciando el bot...
echo ========================================================
python bot.py

pause
