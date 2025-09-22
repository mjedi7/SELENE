@echo off
echo Iniciando backup de todos_trabajadores...

set PG_PATH="C:\Program Files\PostgreSQL\17\bin"
set BACKUP_DIR="c:\Users\RH-Janeth\OneDrive - CECyTEV\Sistema\2025\backup"

:: Formatear fecha y hora de forma segura
for /f "tokens=1-4 delims=/ " %%a in ('date /t') do (
    set YYYY=%%d
    set MM=%%b
    set DD=%%c
)
for /f "tokens=1-2 delims=: " %%a in ("%time%") do (
    set HH=%%a
    set Min=%%b
)

:: Eliminar espacios en horas menores a 10
if "%HH:~0,1%"==" " set HH=0%HH:~1,1%

set FECHA=%YYYY%-%MM%-%DD%_%HH%-%Min%

echo Generando archivo: todos_trabajadores_%FECHA%.backup

%PG_PATH%\pg_dump.exe -h localhost -U postgres -F c -b -v -f %BACKUP_DIR%\todos_trabajadores_%FECHA%.backup todos_trabajadores

echo Backup completado en %BACKUP_DIR%.
pause