@echo off
powershell -Command "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*manage.py runserver*' } | ForEach-Object { Stop-Process -Id $_.ProcessId }"
echo Servidor detenido.
pause
