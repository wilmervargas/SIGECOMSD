
# 0. Forzar ubicación al directorio del script para evitar errores en System32
$currentDir = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Definition }
if (-not $currentDir) { $currentDir = Get-Location }
Set-Location -Path $currentDir

Write-Host "[SISTEMA] Iniciando configuracion en: $currentDir" -ForegroundColor Cyan

# 1. Permisos para la sesión actual
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force

# 2. Definir y Crear requirements.txt (Ruta absoluta y todas tus librerias)
$reqPath = Join-Path $currentDir "requirements.txt"
$librerias = @"
arabic-reshaper==3.0.0
asgiref==3.11.0
asn1crypto==1.5.1
certifi==2025.11.12
cffi==2.0.0
charset-normalizer==3.4.4
cryptography==46.0.3
cssselect2==0.8.0
Django==6.0
et_xmlfile==2.0.0
freetype-py==2.5.1
html5lib==1.1
idna==3.11
lxml==6.0.2
openpyxl==3.1.5
oscrypto==1.3.0
pillow==12.0.0
pycairo==1.29.0
pycparser==2.23
pyHanko==0.32.0
pyhanko-certvalidator==0.29.0
pypdf==6.4.0
python-bidi==0.6.7
python-dotenv==1.0.1
PyYAML==6.0.3
reportlab==4.4.5
requests==2.32.5
rlPyCairo==0.4.0
six==1.17.0
sqlparse==0.5.4
svglib==1.6.0
tinycss2==1.5.1
tzdata==2025.2
tzlocal==5.3.1
uritools==5.0.0
urllib3==2.5.0
webencodings==0.5.1
xhtml2pdf==0.2.17
"@

try {
    # Guardamos usando la ruta calculada para asegurar que llegue a C:\sigecomsd
    $librerias | Out-File -FilePath $reqPath -Encoding ascii -Force
    Write-Host "[OK] requirements.txt generado con todas las librerias." -ForegroundColor Green
} catch {
    Write-Host "[ERROR] No se pudo crear el archivo en $reqPath. Verifica permisos." -ForegroundColor Red
    pause; exit
}

# 3. Gestión del Entorno Virtual (VENV)
$venvPath = Join-Path $currentDir "venv"
if (!(Test-Path $venvPath)) {
    Write-Host "[INFO] Creando entorno virtual local..." -ForegroundColor Yellow
    python -m venv venv
}

# 4. Activación del entorno (Ruta Absoluta)
Write-Host "[INFO] Activando entorno..." -ForegroundColor Green
$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"

if (Test-Path $activateScript) {
    . $activateScript
} else {
    Write-Host "[CRÍTICO] No se encontró el entorno virtual en $venvPath" -ForegroundColor Red
    pause; exit
}

# 5. Actualización e Instalación
Write-Host "[INFO] Actualizando Pip e instalando librerías (esto puede tardar)..." -ForegroundColor Magenta
python -m pip install --upgrade pip setuptools wheel --quiet
python -m pip install -r $reqPath

# 6. Verificación Final
Write-Host "`n--- VERIFICACIÓN DE INSTALACIÓN ---" -ForegroundColor Cyan
$djVer = python -m django --version 2>$null

if ($djVer) {
    Write-Host "[SISTEMA] Django $djVer instalado correctamente." -ForegroundColor Green
} else {
    Write-Host "[ERROR] Django no se detecta. Revisa los mensajes de error de arriba." -ForegroundColor Red
}

Write-Host "===============================================" -ForegroundColor Cyan
pause