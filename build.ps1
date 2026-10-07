$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
python create_icon.py
if ($LASTEXITCODE -ne 0) { throw 'Icon generation failed' }
python -m unittest discover -s tests -v
if ($LASTEXITCODE -ne 0) { throw 'Conversion tests failed' }
python -m PyInstaller --noconfirm --clean --onefile --windowed --name 'mohamadmilad hadad' --icon assets/app.ico --version-file version_info.txt --add-data 'assets/app.ico;assets' app.py
if ($LASTEXITCODE -ne 0) { throw 'EXE build failed' }
