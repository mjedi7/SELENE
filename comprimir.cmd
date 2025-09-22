@echo off
setlocal

rem Obtener fecha y hora en formato compatible para nombre de archivo
for /f "tokens=1-4 delims=/ " %%a in ('date /t') do (
  set fecha=%%c-%%a-%%b
)
for /f "tokens=1-2 delims=:." %%a in ("%time%") do (
  set hora=%%a%%b
)
set hora=%hora: =0%

set zipname=backup_%fecha%_%hora%.zip

rem Comprimir el directorio actual (todo su contenido) en archivo zip
powershell -Command "Compress-Archive -Path * -DestinationPath '%cd%\%zipname%'"

rem Mover el archivo zip a la ruta destino
move "%cd%\%zipname%" "c:\Users\RH-Janeth\OneDrive - CECyTEV\Sistema\2025\backup\"

endlocal
echo Archivo comprimido y movido correctamente.
pause
