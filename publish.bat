@echo off
REM Windows publishing script for MCP Visualization Package

if "%1"=="" (
    set VERSION=0.1.0
) else (
    set VERSION=%1
)

echo 🚀 Publishing mcp-visualization-duckdb v%VERSION%

REM Update versions
powershell -Command "(Get-Content pyproject.toml) -replace 'version = \".*\"', 'version = \"%VERSION%\"' | Set-Content pyproject.toml"
powershell -Command "(Get-Content mcp_visualization\__init__.py) -replace '__version__ = \".*\"', '__version__ = \"%VERSION%\"' | Set-Content mcp_visualization\__init__.py"

REM Clean and build
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build
for /d %%i in (*.egg-info) do rmdir /s /q "%%i"

echo 🏗️ Building package...
python -m build
if errorlevel 1 (
    echo ❌ Build failed
    exit /b 1
)

REM Validate
echo 🔍 Validating package...
twine check dist/*
if errorlevel 1 (
    echo ❌ Package validation failed
    exit /b 1
)

REM Upload to TestPyPI first
echo 📤 Uploading to TestPyPI...
twine upload --repository testpypi dist/*
if errorlevel 1 (
    echo ❌ TestPyPI upload failed
    exit /b 1
)

echo ✅ TestPyPI upload successful!
echo 📦 Test at: https://test.pypi.org/project/mcp-visualization-duckdb/%VERSION%/

REM Confirm before real upload
set /p REPLY="Upload to real PyPI? (y/N): "
if /i "%REPLY%"=="y" (
    echo 📤 Uploading to PyPI...
    twine upload dist/*
    if errorlevel 1 (
        echo ❌ PyPI upload failed
        exit /b 1
    )
    echo 🎉 Published successfully!
    echo 📦 https://pypi.org/project/mcp-visualization-duckdb/%VERSION%/
) else (
    echo ❌ Publication cancelled.
)

pause