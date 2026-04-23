@echo off
REM ============================================================
REM Geometry Wars - PyInstaller Derleme Betiği
REM Bu betik oyunu tek dosyalı .exe olarak derler,
REM ardından Inno Setup ile kurulum paketi oluşturur.
REM ============================================================

setlocal enabledelayedexpansion

REM Renk kodları (Windows 10+)
set "GREEN=[92m"
set "RED=[91m"
set "YELLOW=[93m"
set "CYAN=[96m"
set "RESET=[0m"

echo %CYAN%============================================================%RESET%
echo %CYAN%   Geometry Wars - Derleme Sistemi v1.0%RESET%
echo %CYAN%============================================================%RESET%
echo.

REM --- Python kontrolü ---
echo %YELLOW%[1/5] Python kontrol ediliyor...%RESET%
python --version >nul 2>&1
if errorlevel 1 (
    echo %RED%HATA: Python bulunamadi. PATH'e eklendiginden emin olun.%RESET%
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VER=%%i
echo %GREEN%    OK: !PYTHON_VER!%RESET%

REM --- PyInstaller kontrolü ---
echo %YELLOW%[2/5] PyInstaller kontrol ediliyor...%RESET%
python -m PyInstaller --version >nul 2>&1
if errorlevel 1 (
    echo %YELLOW%    PyInstaller bulunamadi. Yukleniyor...%RESET%
    pip install pyinstaller
    if errorlevel 1 (
        echo %RED%HATA: PyInstaller yuklenemedi.%RESET%
        pause
        exit /b 1
    )
)
for /f "tokens=*" %%i in ('python -m PyInstaller --version 2^>^&1') do set PI_VER=%%i
echo %GREEN%    OK: PyInstaller !PI_VER!%RESET%

REM --- pygame kontrolü ---
echo %YELLOW%[3/5] pygame kontrol ediliyor...%RESET%
python -c "import pygame; print(pygame.__version__)" >nul 2>&1
if errorlevel 1 (
    echo %YELLOW%    pygame bulunamadi. Yukleniyor...%RESET%
    pip install pygame
    if errorlevel 1 (
        echo %RED%HATA: pygame yuklenemedi.%RESET%
        pause
        exit /b 1
    )
)
for /f "tokens=*" %%i in ('python -c "import pygame; print(pygame.__version__)" 2^>^&1') do set PG_VER=%%i
echo %GREEN%    OK: pygame !PG_VER!%RESET%

REM --- Çalışma dizinini ayarla ---
cd /d "%~dp0\.."
echo %YELLOW%[4/5] PyInstaller ile derleniyor...%RESET%
echo %CYAN%    Dizin: %CD%%RESET%

REM dist ve build klasörlerini temizle
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "GeometryWars.spec" del /q "GeometryWars.spec"

REM PyInstaller komutu
python -m PyInstaller ^
    --name "GeometryWars" ^
    --onedir ^
    --windowed ^
    --icon=NONE ^
    --add-data "settings.py;." ^
    --add-data "src;src" ^
    --hidden-import "pygame" ^
    --hidden-import "pygame.font" ^
    --hidden-import "pygame.mixer" ^
    --hidden-import "pygame.display" ^
    --hidden-import "src.game" ^
    --hidden-import "src.entities.player" ^
    --hidden-import "src.entities.bullet" ^
    --hidden-import "src.entities.enemies.chaser" ^
    --hidden-import "src.entities.enemies.wanderer" ^
    --hidden-import "src.entities.enemies.shooter" ^
    --hidden-import "src.entities.enemies.splitter" ^
    --hidden-import "src.effects.particle_system" ^
    --hidden-import "src.effects.grid" ^
    --hidden-import "src.managers.wave_manager" ^
    --hidden-import "src.managers.collision_manager" ^
    --hidden-import "src.managers.score_manager" ^
    --hidden-import "src.ui.hud" ^
    --noconfirm ^
    main.py

if errorlevel 1 (
    echo %RED%HATA: PyInstaller derlemesi basarisiz!%RESET%
    pause
    exit /b 1
)
echo %GREEN%    OK: Derleme tamamlandi. dist\GeometryWars\ klasorune bakın.%RESET%

REM --- Inno Setup kontrolü ve kurulum paketi oluşturma ---
echo %YELLOW%[5/5] Inno Setup ile kurulum paketi olusturuluyor...%RESET%

set ISCC_PATH=""
for %%p in (
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
    "C:\Program Files\Inno Setup 6\ISCC.exe"
    "C:\Program Files (x86)\Inno Setup 5\ISCC.exe"
) do (
    if exist %%p set ISCC_PATH=%%p
)

if !ISCC_PATH!=="" (
    echo %YELLOW%    UYARI: Inno Setup bulunamadi. Kurulum paketi olusturulamadi.%RESET%
    echo %YELLOW%    https://jrsoftware.org/isinfo.php adresinden indirin.%RESET%
    echo %YELLOW%    Oyun dist\GeometryWars\ klasoründen calistirılabilir.%RESET%
) else (
    !ISCC_PATH! "installer\installer_script.iss"
    if errorlevel 1 (
        echo %RED%HATA: Inno Setup paketi olusturulamadi!%RESET%
    ) else (
        echo %GREEN%    OK: Kurulum paketi olusturuldu: installer\output\%RESET%
    )
)

echo.
echo %GREEN%============================================================%RESET%
echo %GREEN%   Derleme tamamlandi!%RESET%
echo %GREEN%============================================================%RESET%
echo.
echo %CYAN%Calistirmak icin:%RESET%
echo     dist\GeometryWars\GeometryWars.exe
echo.
pause
