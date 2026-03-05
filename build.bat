@echo off
setlocal EnableDelayedExpansion
title Expense Tracker Pro — Build

echo.
echo ============================================================
echo   💸  Expense Tracker Pro — Windows EXE Builder
echo ============================================================
echo.

REM ── Check Python is available ─────────────────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found.
    echo         Download it from https://python.org
    echo         Make sure to tick "Add Python to PATH" during install.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYVER=%%i
echo [OK] Found %PYVER%

REM ── Upgrade pip quietly ───────────────────────────────────────────────────
echo.
echo [1/5] Upgrading pip...
python -m pip install --upgrade pip --quiet
if errorlevel 1 (
    echo [WARN] pip upgrade failed — continuing anyway
)

REM ── Install app dependencies ──────────────────────────────────────────────
echo [2/5] Installing app dependencies...
pip install flask werkzeug pandas openpyxl reportlab --quiet
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)
echo [OK] Dependencies installed

REM ── Install PyInstaller ───────────────────────────────────────────────────
echo [3/5] Installing PyInstaller...
pip install pyinstaller --quiet
if errorlevel 1 (
    echo [ERROR] Failed to install PyInstaller.
    pause
    exit /b 1
)

REM Verify pyinstaller is callable
pyinstaller --version >nul 2>&1
if errorlevel 1 (
    echo [WARN] 'pyinstaller' not on PATH, trying via python -m...
    set USE_MODULE=1
)
echo [OK] PyInstaller ready

REM ── Clean old build artefacts ─────────────────────────────────────────────
echo [4/5] Cleaning previous build...
if exist dist\ExpenseTrackerPro.exe (
    del /q dist\ExpenseTrackerPro.exe
    echo [OK] Removed old .exe
)
if exist build (
    rmdir /s /q build
)

REM ── Run PyInstaller ───────────────────────────────────────────────────────
echo [5/5] Building EXE (this takes 1-3 minutes)...
echo.

if defined USE_MODULE (
    python -m PyInstaller expense_tracker.spec --noconfirm --clean
) else (
    pyinstaller expense_tracker.spec --noconfirm --clean
)

if errorlevel 1 (
    echo.
    echo [ERROR] Build failed. See output above for details.
    echo.
    echo Common fixes:
    echo   - Run this script as Administrator
    echo   - Temporarily disable antivirus
    echo   - Make sure all source files are present
    pause
    exit /b 1
)

REM ── Confirm output ────────────────────────────────────────────────────────
if exist dist\ExpenseTrackerPro.exe (
    echo.
    echo ============================================================
    echo   BUILD SUCCESSFUL!
    echo ============================================================
    echo.
    for %%A in (dist\ExpenseTrackerPro.exe) do (
        set /a SIZE_MB=%%~zA / 1048576
        echo   Output : dist\ExpenseTrackerPro.exe
        echo   Size   : !SIZE_MB! MB
    )
    echo.
    echo   To test: double-click dist\ExpenseTrackerPro.exe
    echo   To share: upload dist\ExpenseTrackerPro.exe to GitHub Releases
    echo.
) else (
    echo [ERROR] Build appeared to succeed but .exe not found in dist\
    pause
    exit /b 1
)

REM ── Optional: open the dist folder ───────────────────────────────────────
set /p OPEN="Open dist\ folder now? (Y/N): "
if /i "!OPEN!"=="Y" explorer dist

echo Done!
pause
