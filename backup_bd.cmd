@echo off
"C:\Program Files\PostgreSQL\17\bin\pg_dump.exe" -h localhost -U postgres -F c -b -v -f ".\todos_trabajadores.backup" todos_trabajadores
rem Mover el archivo zip a la ruta destino
move "todos_trabajadores.backup" "c:\Users\RH-Janeth\OneDrive - CECyTEV\Sistema\2025\backup\"
pause