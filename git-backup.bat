@echo off
REM ===================================================
REM  Backup automático de proyecto Django a GitHub
REM  Autor: Oscar (adaptado por ChatGPT)
REM  Fecha: %date%
REM ===================================================

REM Ir al directorio del proyecto
cd /d "C:\Users\Administrador.WIN-2AMKLNOB857\trabajadores"

echo ===================================================
echo  Iniciando respaldo de proyecto Django a GitHub
echo ===================================================
echo.

REM Mostrar la rama actual
git branch

REM Mostrar cambios pendientes
echo.
git status
echo.

REM Pedir comentario para el commit
set /p COMMIT_MSG=Escribe el comentario del commit: 

REM Agregar todos los cambios
git add .

REM Crear commit
git commit -m "%COMMIT_MSG%"

REM Preguntar nombre del tag
set /p TAG_NAME=Nombre del tag (ej. v20251110-backup): 

REM Crear tag anotado con fecha y comentario
git tag -a %TAG_NAME% -m "%COMMIT_MSG%"

REM Empujar cambios a la rama actual
echo.
echo Subiendo cambios a GitHub...
git push origin HEAD

REM Empujar tags
echo.
echo Subiendo tags a GitHub...
git push origin --tags

echo.
echo ===================================================
echo  Respaldo completado correctamente.
echo  Commit: %COMMIT_MSG%
echo  Tag: %TAG_NAME%
echo ===================================================
pause