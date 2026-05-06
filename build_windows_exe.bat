@echo off
setlocal

cd /d "%~dp0"

echo [1/4] Checking Python...
where py >nul 2>nul
if %ERRORLEVEL%==0 (
    set "PY_CMD=py -3"
) else (
    where python >nul 2>nul
    if not %ERRORLEVEL%==0 (
        echo Python is not installed. Install Python 3.10+ and run this script again.
        exit /b 1
    )
    set "PY_CMD=python"
)

echo [2/4] Installing build dependencies...
%PY_CMD% -m pip install --upgrade pip
%PY_CMD% -m pip install -r requirements.txt
%PY_CMD% -m pip install pyinstaller

echo [3/4] Cleaning previous build output...
if exist "build" rmdir /s /q "build"
if exist "dist\GAME" rmdir /s /q "dist\GAME"

echo [4/4] Building standalone game...
%PY_CMD% -m PyInstaller --noconfirm "GAME.spec"
if not %ERRORLEVEL%==0 (
    echo Build failed.
    exit /b 1
)

echo.
echo Build complete.
echo Run: dist\GAME\GAME.exe
echo.
endlocal
