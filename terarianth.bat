@echo off
setlocal

set "GAME_DIR=%~dp0"
set "BOOTSTRAP=%GAME_DIR%terarianth_bootstrap.py"

where py >nul 2>nul
if not errorlevel 1 (
    py -3 "%BOOTSTRAP%" %*
    exit /b %errorlevel%
)

where python >nul 2>nul
if not errorlevel 1 (
    python "%BOOTSTRAP%" %*
    exit /b %errorlevel%
)

echo Python 3 was not found. Trying to install it with winget...

where winget >nul 2>nul
if not errorlevel 1 (
    winget install --id Python.Python.3.12 -e --accept-package-agreements --accept-source-agreements

    where py >nul 2>nul
    if not errorlevel 1 (
        py -3 "%BOOTSTRAP%" %*
        exit /b %errorlevel%
    )

    where python >nul 2>nul
    if not errorlevel 1 (
        python "%BOOTSTRAP%" %*
        exit /b %errorlevel%
    )
)

echo Python 3 is required to launch terarianth.
echo Install Python 3 and run terarianth.bat again.
exit /b 1
