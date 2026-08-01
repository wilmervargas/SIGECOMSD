@echo off
setlocal enabledelayedexpansion

:: 1. Definir rutas basadas en la ubicación actual del script
:: %~dp0 es la carpeta actual donde reside este archivo .bat
set "RECURSOS=%~dp0"
set "DESTINO=C:\sigecomsd"
set "ARCHIVO_RAR=sigecomsd.rar"

:: Definición de archivos origen y destino
set "COMPRIMIDO_ORIGEN=%RECURSOS%%ARCHIVO_RAR%"
set "COMPRIMIDO_DESTINO=%DESTINO%\%ARCHIVO_RAR%"
set "INSTALADOR_ORIGEN=%~f0"
set "INSTALADOR_DESTINO=%DESTINO%\instalar_sigecomsd.bat"

:: Rutas de los scripts que se extraerán
set "PS1_PYTHON=%DESTINO%\ip1.ps1"
set "PS2_LIBS=%DESTINO%\ip2.ps1"

echo ===========================================
echo    INICIANDO INSTALADOR SIGECOMSD
echo ===========================================

:: 2. Crear carpeta de destino
if not exist "%DESTINO%" (
    echo [1/8] Creando carpeta de sistema en %DESTINO%...
    mkdir "%DESTINO%"
)

:: 3. COPIAR EL ARCHIVO .BAT A LA CARPETA DE INSTALACIÓN (Nuevo)
echo [2/8] Copiando instalador a la carpeta de destino...
copy /Y "%INSTALADOR_ORIGEN%" "%INSTALADOR_DESTINO%" >nul

:: 4. COPIAR EL ARCHIVO RAR DESDE LA CARPETA ACTUAL A C:\
echo [3/8] Buscando %ARCHIVO_RAR% en %RECURSOS%...
if exist "%COMPRIMIDO_ORIGEN%" (
    echo [4/8] Copiando archivo comprimido a %DESTINO%...
    copy /Y "%COMPRIMIDO_ORIGEN%" "%COMPRIMIDO_DESTINO%" >nul
    if !errorlevel! equ 0 (
        echo [OK] Archivo copiado exitosamente.
    ) else (
        echo [ERROR] No se pudo copiar el archivo. Ejecute como Administrador.
        pause
        exit /b
    )
) else (
    echo [ERROR] No se encontro el archivo %ARCHIVO_RAR% al lado de este instalador.
    echo Asegurese de que el archivo .rar y este .bat esten en la misma carpeta.
    pause
    exit /b
)

:: 5. DESCOMPRESIÓN LOCAL
echo [5/8] Descomprimiendo archivos en %DESTINO%...
if exist "C:\Program Files\WinRAR\WinRAR.exe" (
    "C:\Program Files\WinRAR\WinRAR.exe" x -y "%COMPRIMIDO_DESTINO%" "%DESTINO%\" >nul
) else if exist "C:\Program Files\7-Zip\7z.exe" (
    "C:\Program Files\7-Zip\7z.exe" x "%COMPRIMIDO_DESTINO%" -o"%DESTINO%\" -y >nul
) else (
    echo [AVISO] No se detecto WinRAR o 7-Zip. Usando herramienta nativa...
    powershell -Command "Expand-Archive -Path '%COMPRIMIDO_DESTINO%' -DestinationPath '%DESTINO%' -Force" 2>nul
)

:: 6. VALIDACIÓN DE SCRIPTS EXTRAÍDOS
echo [6/8] Validando scripts de instalacion...
if not exist "%PS1_PYTHON%" (
    echo [ERROR] No se encontro %PS1_PYTHON% tras descomprimir.
    pause
    exit /b
)

:: 7. EJECUCIÓN DE SCRIPTS POWERSHELL (ADMIN)
echo [7/8] Instalando Python (ip1.ps1)...
powershell -Command "Start-Process powershell -ArgumentList '-NoProfile -ExecutionPolicy Bypass -File \"%PS1_PYTHON%\"' -Verb RunAs -Wait"

echo [8/8] Instalando librerias y dependencias (ip2.ps1)...
powershell -Command "Start-Process powershell -ArgumentList '-NoProfile -ExecutionPolicy Bypass -File \"%PS2_LIBS%\"' -WorkingDirectory \"%DESTINO%\" -Verb RunAs -Wait"

:: 8. ACCESO DIRECTO EN EL ESCRITORIO
echo Creando acceso directo en el escritorio...
set "KEY_REG=HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
for /f "tokens=2,*" %%A in ('reg query "%KEY_REG%" /v Desktop') do set "DESKTOP_RAW=%%B"
for /f "delims=" %%i in ('echo %DESKTOP_RAW%') do set "REAL_DESKTOP=%%i"

if exist "%DESTINO%\ejecutar_sigecomsd.bat" (
    copy /Y "%DESTINO%\ejecutar_sigecomsd.bat" "%REAL_DESKTOP%\" >nul
    echo [OK] Instalacion finalizada con exito.
) else (
    echo [AVISO] No se encontro el lanzador para el escritorio.
)

echo.
echo ===========================================
echo    PROCESO COMPLETADO EXITOSAMENTE
echo ===========================================
pause