@echo off
REM Build script for Stembler Windows application
REM
REM This script builds the Windows .exe using PyInstaller.
REM
REM Requirements:
REM   - Python 3.12+
REM   - uv (Python package manager)
REM   - PyInstaller
REM
REM Usage:
REM   .\packaging\windows\build.bat

setlocal enabledelayedexpansion

echo =====================================
echo   Stembler Windows Build Script
echo =====================================
echo.

cd /d %~dp0\..\..

echo [1/5] Checking environment...

REM Check for uv
where uv >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: uv is not installed
    echo Install from: https://github.com/astral-sh/uv
    exit /b 1
)

REM Check for Python
uv run python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python environment not set up
    echo Run: uv sync
    exit /b 1
)

echo [2/5] Installing PyInstaller...
uv pip install pyinstaller

echo [3/5] Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo [4/5] Building Windows executable...
echo This may take several minutes (especially on first build)...
echo.

REM Run PyInstaller with the spec file
uv run pyinstaller packaging\windows\stembler.spec --clean --noconfirm

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [5/5] Build successful!
    echo.
    echo Application created:
    echo   dist\Stembler\Stembler.exe
    echo.
    echo To test the application:
    echo   dist\Stembler\Stembler.exe
    echo.
    echo To create an MSI installer:
    echo   python packaging\windows\build_msi.py
    echo.
) else (
    echo.
    echo Build failed!
    echo Check the output above for errors.
    exit /b 1
)
