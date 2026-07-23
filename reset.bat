@echo off
echo [*] Buscando implant por conexion al C2 (puerto 443)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":443 "') do (
    if not "%%a"=="0" (
        echo     Matando PID %%a
        taskkill /F /PID %%a 2>nul
    )
)

echo [*] Matando por nombres conocidos...
taskkill /F /IM kkkk.exe    2>nul
taskkill /F /IM penesot.exe 2>nul
taskkill /F /IM XD.exe      2>nul

echo [*] Limpiando Downloads...
for %%f in (
    "%USERPROFILE%\Downloads\kkkk.exe"
    "%USERPROFILE%\Downloads\kkkk (1).exe"
    "%USERPROFILE%\Downloads\kkkk (2).exe"
    "%USERPROFILE%\Downloads\penesot.exe"
    "%USERPROFILE%\Downloads\XD.exe"
) do del /F /Q "%%f" 2>nul

echo [OK] Listo. Descarga y ejecuta el nuevo exe.
pause
