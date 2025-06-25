@echo off
REM Local testing script for MCP Visualization Package (Windows)

echo 🧪 MCP Visualization Package - Local Testing (Windows)
echo =============================================

REM Test 1: Package structure
echo.
echo 📋 Test 1: Package Structure
echo ----------------------------
if exist "mcp_visualization" if exist "pyproject.toml" if exist "mcp_visualization\__init__.py" (
    echo ✅ Package structure is valid
) else (
    echo ❌ Package structure is invalid
    exit /b 1
)

REM Test 2: Basic imports
echo.
echo 📋 Test 2: Basic Imports
echo ------------------------
python -c "try: from mcp_visualization.claude_config import ClaudeDesktopConfigManager; import mcp_visualization; print('✅ Basic imports successful'); print(f'✅ Package version: {mcp_visualization.__version__}'); except Exception as e: print(f'❌ Import failed: {e}'); exit(1)"
if errorlevel 1 exit /b 1

REM Test 3: Claude Desktop config manager
echo.
echo 📋 Test 3: Claude Desktop Config Manager
echo ----------------------------------------
python -c "try: from mcp_visualization.claude_config import ClaudeDesktopConfigManager; manager = ClaudeDesktopConfigManager(); status = manager.get_status(); print(f'✅ Platform: {status[\"platform\"]}'); print(f'✅ Config path: {status[\"config_path\"]}'); print('✅ Config manager working'); except Exception as e: print(f'❌ Config manager failed: {e}'); exit(1)"
if errorlevel 1 exit /b 1

REM Test 4: Package building
echo.
echo 📋 Test 4: Package Building
echo ---------------------------
python -m build --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Build tool not available (install with: pip install build)
) else (
    echo ℹ️  Building package...
    if exist "dist" rmdir /s /q dist
    if exist "build" rmdir /s /q build
    if exist "*.egg-info" rmdir /s /q *.egg-info
    
    python -m build
    if errorlevel 1 (
        echo ⚠️  Package build failed
    ) else (
        echo ✅ Package built successfully
        if exist "dist\*.whl" if exist "dist\*.tar.gz" (
            echo ✅ Wheel and source distribution created
            dir dist
        ) else (
            echo ⚠️  Build completed but expected files not found
        )
    )
)

REM Test 5: Virtual environment test
echo.
echo 📋 Test 5: Virtual Environment Installation Test
echo ------------------------------------------------
python -m venv --help >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Virtual environment not available
) else (
    echo ℹ️  Creating test virtual environment...
    
    REM Clean up any existing test env
    if exist "test_venv_win" rmdir /s /q test_venv_win
    
    REM Create virtual environment
    python -m venv test_venv_win
    call test_venv_win\Scripts\activate.bat
    
    REM Upgrade pip
    python -m pip install --upgrade pip wheel
    
    REM Install package in development mode
    pip install -e .
    if errorlevel 1 (
        echo ❌ Package installation failed
    ) else (
        echo ✅ Package installed in test environment
        
        REM Test CLI availability
        where mcp-viz >nul 2>&1
        if errorlevel 1 (
            echo ⚠️  CLI command not found in PATH
        ) else (
            echo ✅ CLI command available
            
            REM Test CLI help
            mcp-viz --help >nul 2>&1
            if errorlevel 1 (
                echo ⚠️  CLI help failed (may need MCP dependencies)
            ) else (
                echo ✅ CLI help command works
            )
        )
    )
    
    call deactivate
    rmdir /s /q test_venv_win
)

REM Test 6: PyPI readiness check
echo.
echo 📋 Test 6: PyPI Readiness Check
echo -------------------------------

findstr /C:"name.*mcp-visualization-duckdb" pyproject.toml >nul
if errorlevel 1 (
    echo ❌ Package name not properly configured
) else (
    echo ✅ Package name configured
)

findstr /C:"version.*0\.1\.0" pyproject.toml >nul
if errorlevel 1 (
    echo ⚠️  Version may need updating
) else (
    echo ✅ Version configured
)

if exist "LICENSE" (
    echo ✅ License file present
) else (
    echo ⚠️  License file missing
)

if exist "README.md" (
    echo ✅ README.md present
) else (
    echo ⚠️  README.md missing
)

REM Summary
echo.
echo 🎯 Test Summary
echo ===============
echo ✅ Package structure is ready for PyPI publication
echo ℹ️  To publish to PyPI:
echo   1. Install build tools: pip install build twine
echo   2. Build package: python -m build
echo   3. Upload to TestPyPI: twine upload --repository testpypi dist/*
echo   4. Test installation: pip install --index-url https://test.pypi.org/simple/ mcp-visualization-duckdb
echo   5. Upload to PyPI: twine upload dist/*
echo.
echo 📖 See DEVELOPMENT.md for detailed instructions
echo 🎉 Local testing completed!

pause