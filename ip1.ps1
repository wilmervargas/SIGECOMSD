# 1. Definir la versión (puedes cambiarla si necesitas otra)
$version = "3.14.3"
$url = "https://www.python.org/ftp/python/$version/python-$version-amd64.exe"
$outPath = "$env:TEMP\python_installer.exe"

# 2. Descargar el archivo
Write-Host "Descargando Python $version desde el sitio oficial..." -ForegroundColor Cyan
Invoke-WebRequest -Uri $url -OutFile $outPath

# 3. Instalación silenciosa
# InstallAllUsers=1 instala en C:\Program Files
# PrependPath=1 lo agrega a las variables de entorno (PATH)
Write-Host "Instalando... Esto tardará un minuto." -ForegroundColor Yellow
Start-Process -FilePath $outPath -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1" -Wait

# 4. Limpieza
Remove-Item $outPath
Write-Host "¡Listo! Cierra y vuelve a abrir tu terminal para usar 'python'." -ForegroundColor Green