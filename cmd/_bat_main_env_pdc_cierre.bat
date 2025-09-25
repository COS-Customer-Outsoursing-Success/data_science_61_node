@echo off
echo ========================================
echo Activando el entorno virtual...
echo ========================================

REM Activar el entorno virtual
call "C:\Users\Emerson.Aguilar\Documents\git_hub\PDC_data_science_61\.venv\Scripts\activate.bat"

IF ERRORLEVEL 1 (
    echo ❌ Error al activar el entorno virtual.
    pause
    exit /b 1
) ELSE (
    echo ✅ Entorno virtual activado correctamente.
)

REM Mostrar qué Python se está usando
echo ----------------------------------------
echo Python actualmente en uso:
where python
echo ----------------------------------------

echo ========================================
echo Ejecutando script de Python...
echo ========================================

REM Ejecutar el script de Python
python "C:\Users\Emerson.Aguilar\Documents\git_hub\PDC_data_science_61\src\_main_process_excel_pdc_cierre.py"

IF ERRORLEVEL 1 (
    echo ❌ Error al ejecutar el script.
) ELSE (
    echo ✅ Script ejecutado correctamente.
)

echo Cerrando .bat en 5 segundos proceso finalizado...
timeout /t 5 /nobreak

echo ========================================
quit()
