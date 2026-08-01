@echo off
setlocal
title Consola de Servidor "sigecomsd" - Puerto 9000

:: 1. Verificación de privilegios de Administrador
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
if '%errorlevel%' NEQ '0' (
    echo [INFO] Solicitando permisos de administrador...
    goto UACPrompt
) else ( goto gotAdmin )

:UACPrompt
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    echo UAC.ShellExecute "%~s0", "", "", "runas", 1 >> "%temp%\getadmin.vbs"
    "%temp%\getadmin.vbs"
    exit /B

:gotAdmin
    if exist "%temp%\getadmin.vbs" ( del "%temp%\getadmin.vbs" )
    
    :: 2. FORZAR ENTRADA A LA RUTA ESPECÍFICA
    :: Usamos /d para cambiar de unidad (de C: a D:) y de carpeta simultáneamente
    set "PROYECTO_PATH=D:\Shared\Publico\sigecomsd"
    cd /d "%PROYECTO_PATH%"
    echo [INFO] Directorio actual: %cd%

    :: 3. Verificación del Entorno Virtual
    if exist "venv\Scripts\activate.bat" (
        echo [OK] Entorno virtual encontrado. Activando...
        call "venv\Scripts\activate.bat"
	echo [OK] Entorno virtual encontrado. PASO ......
    ) else (
        echo [ERROR] No se encontro la carpeta "venv" en: %PROYECTO_PATH%
        echo Verifica que el entorno virtual este instalado en esa ruta.
        pause
        exit
    )

    :: 4. Lanzar el navegador
    :: Nota: En el servidor se abre localmente, pero otros usuarios usaran la IP del server.
    echo [INFO] Abriendo navegador en http://localhost:9000/
    echo start http://localhost:9000/

    :: 5. Ejecutar Django en el puerto 9000
    echo [INFO] Iniciando servidor Django en el puerto 9000...
    echo [INFO] Accesible en red via: http://[IP_DEL_SERVIDOR]:9000/
    echo Presiona CTRL+C para detener el servidor.
    
    :: 0.0.0.0 permite conexiones externas al Windows Server
    python manage.py runserver 0.0.0.0:9000

    :: 6. Pausa final en caso de error
    echo.
    echo [AVISO] El proceso de Django se ha detenido.
    pause