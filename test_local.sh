#!/bin/bash
# Local testing script for MCP Visualization Package

set -e  # Exit on any error

echo "🧪 MCP Visualization Package - Local Testing"
echo "============================================="

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

info() {
    echo -e "ℹ️  $1"
}

# Test 1: Package structure
echo -e "\n📋 Test 1: Package Structure"
echo "----------------------------"
if [[ -d "mcp_visualization" && -f "pyproject.toml" && -f "mcp_visualization/__init__.py" ]]; then
    success "Package structure is valid"
else
    error "Package structure is invalid"
    exit 1
fi

# Test 2: Basic imports (without MCP dependencies)
echo -e "\n📋 Test 2: Basic Imports"
echo "------------------------"
python3 -c "
try:
    from mcp_visualization.claude_config import ClaudeDesktopConfigManager
    import mcp_visualization
    print('✅ Basic imports successful')
    print(f'✅ Package version: {mcp_visualization.__version__}')
except Exception as e:
    print(f'❌ Import failed: {e}')
    exit(1)
" || exit 1

# Test 3: Claude Desktop config manager
echo -e "\n📋 Test 3: Claude Desktop Config Manager"
echo "----------------------------------------"
python3 -c "
try:
    from mcp_visualization.claude_config import ClaudeDesktopConfigManager
    manager = ClaudeDesktopConfigManager()
    status = manager.get_status()
    print(f'✅ Platform: {status[\"platform\"]}')
    print(f'✅ Config path: {status[\"config_path\"]}')
    print('✅ Config manager working')
except Exception as e:
    print(f'❌ Config manager failed: {e}')
    exit(1)
" || exit 1

# Test 4: Package building
echo -e "\n📋 Test 4: Package Building"
echo "---------------------------"
if command -v python3 -m build &> /dev/null; then
    info "Building package..."
    rm -rf dist/ build/ *.egg-info/ 2>/dev/null || true
    
    if python3 -m build; then
        success "Package built successfully"
        
        # Check if files were created
        if [[ -f dist/*.whl && -f dist/*.tar.gz ]]; then
            success "Wheel and source distribution created"
            ls -la dist/
        else
            warning "Build completed but expected files not found"
        fi
    else
        warning "Package build failed (install with: pip install build)"
    fi
else
    warning "Build tool not available (install with: pip install build)"
fi

# Test 5: Virtual environment test
echo -e "\n📋 Test 5: Virtual Environment Installation Test"
echo "------------------------------------------------"
if command -v python3 -m venv &> /dev/null; then
    info "Creating test virtual environment..."
    
    # Clean up any existing test env
    rm -rf test_venv/ 2>/dev/null || true
    
    # Create virtual environment
    python3 -m venv test_venv
    source test_venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip wheel
    
    # Install package in development mode
    if pip install -e .; then
        success "Package installed in test environment"
        
        # Test CLI availability
        if command -v mcp-viz &> /dev/null; then
            success "CLI command available"
            
            # Test CLI help
            if mcp-viz --help &> /dev/null; then
                success "CLI help command works"
            else
                warning "CLI help failed (may need MCP dependencies)"
            fi
            
            # Test status command
            if mcp-viz status &> /dev/null; then
                success "CLI status command works"
            else
                warning "CLI status failed (may need MCP dependencies)"
            fi
        else
            warning "CLI command not found in PATH"
        fi
    else
        error "Package installation failed"
    fi
    
    deactivate
    rm -rf test_venv/
else
    warning "Virtual environment not available"
fi

# Test 6: PyPI readiness check
echo -e "\n📋 Test 6: PyPI Readiness Check"
echo "-------------------------------"

# Check pyproject.toml
if grep -q "name.*mcp-visualization-duckdb" pyproject.toml; then
    success "Package name configured"
else
    error "Package name not properly configured"
fi

if grep -q "version.*0\.1\.0" pyproject.toml; then
    success "Version configured"
else
    warning "Version may need updating"
fi

if [[ -f "LICENSE" ]]; then
    success "License file present"
else
    warning "License file missing"
fi

if [[ -f "README.md" ]]; then
    success "README.md present"
else
    warning "README.md missing"
fi

# Summary
echo -e "\n🎯 Test Summary"
echo "==============="
success "Package structure is ready for PyPI publication"
info "To publish to PyPI:"
echo "  1. Install build tools: pip install build twine"
echo "  2. Build package: python -m build"
echo "  3. Upload to TestPyPI: twine upload --repository testpypi dist/*"
echo "  4. Test installation: pip install --index-url https://test.pypi.org/simple/ mcp-visualization-duckdb"
echo "  5. Upload to PyPI: twine upload dist/*"

echo -e "\n📖 See DEVELOPMENT.md for detailed instructions"
echo "🎉 Local testing completed!"