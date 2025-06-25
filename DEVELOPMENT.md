# 🧪 Local Testing & PyPI Publishing Guide

## 🏠 Local Testing

### Step 1: Install Build Tools

```bash
# Install required build and publishing tools
pip install build twine pytest wheel

# For development testing
pip install -e .
```

### Step 2: Local Development Installation

```bash
# Navigate to your project directory
cd /path/to/mcp-visualization-duckdb

# Install package in development mode (editable)
pip install -e .

# This allows you to edit code and test immediately
```

### Step 3: Test CLI Commands

```bash
# Test that CLI is available
mcp-viz --help

# Test configuration (dry run)
mcp-viz status

# Test interactive configuration
mcp-viz configure

# Test all functionality
mcp-viz test
```

### Step 4: Build and Test Distribution

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info/

# Build the package
python -m build

# This creates:
# dist/mcp_visualization_duckdb-0.1.0.tar.gz  (source distribution)
# dist/mcp_visualization_duckdb-0.1.0-py3-none-any.whl  (wheel)
```

### Step 5: Test Installation from Built Package

```bash
# Create a fresh virtual environment for testing
python -m venv test_env
source test_env/bin/activate  # Linux/Mac
# OR
test_env\Scripts\activate     # Windows

# Install from wheel file
pip install dist/mcp_visualization_duckdb-0.1.0-py3-none-any.whl

# Test that it works
mcp-viz --help
mcp-viz status
```

### Step 6: Run Package Tests

```bash
# Run the validation script
python test_package.py

# Run pytest if you have tests
pytest tests/ -v
```

## 📦 Publishing to PyPI

### Step 1: Create PyPI Account

1. **Register at PyPI**: https://pypi.org/account/register/
2. **Register at TestPyPI** (for testing): https://test.pypi.org/account/register/
3. **Enable 2FA**: Highly recommended for security

### Step 2: Configure API Tokens

```bash
# Create API token on PyPI (Account Settings > API tokens)
# Store in ~/.pypirc for convenience

cat > ~/.pypirc << 'EOF'
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YourActualAPITokenHere

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YourTestAPITokenHere
EOF

chmod 600 ~/.pypirc
```

### Step 3: Test Upload to TestPyPI First

```bash
# Build fresh package
python -m build

# Upload to TestPyPI first (for testing)
twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ mcp-visualization-duckdb
```

### Step 4: Upload to Real PyPI

```bash
# If TestPyPI worked well, upload to real PyPI
twine upload dist/*

# Your package will be available at:
# https://pypi.org/project/mcp-visualization-duckdb/
```

## 🔧 Pre-Publication Checklist

### Code Quality

```bash
# Format code
black mcp_visualization/
isort mcp_visualization/

# Type checking (if using mypy)
mypy mcp_visualization/

# Run tests
pytest tests/ -v
python test_package.py
```

### Package Information

- [ ] **Version number** updated in `pyproject.toml` and `__init__.py`
- [ ] **Description** accurate and compelling
- [ ] **Keywords** relevant for discovery
- [ ] **URLs** point to correct repository
- [ ] **License** properly specified
- [ ] **README.md** comprehensive and up-to-date

### Testing

- [ ] **Local installation** works: `pip install -e .`
- [ ] **CLI commands** all functional: `mcp-viz --help`
- [ ] **Configuration** works on your platform
- [ ] **Build succeeds**: `python -m build`
- [ ] **Package validation** passes: `python test_package.py`

## 🚀 Complete Local Testing Workflow

```bash
#!/bin/bash
# Complete testing script

echo "🧪 Starting comprehensive local testing..."

# 1. Clean environment
echo "🧹 Cleaning build artifacts..."
rm -rf dist/ build/ *.egg-info/

# 2. Install in development mode
echo "📦 Installing in development mode..."
pip install -e .

# 3. Test CLI
echo "🔧 Testing CLI commands..."
mcp-viz --help || exit 1
mcp-viz status || exit 1

# 4. Build package
echo "🏗️ Building package..."
python -m build || exit 1

# 5. Test fresh installation
echo "🆕 Testing fresh installation..."
python -m venv fresh_test_env
source fresh_test_env/bin/activate
pip install dist/*.whl
mcp-viz --help || exit 1
mcp-viz test || exit 1
deactivate
rm -rf fresh_test_env

# 6. Run validation tests
echo "✅ Running validation tests..."
python test_package.py || exit 1

echo "🎉 All tests passed! Ready for publication."
```

## 📈 Publishing Workflow

### Version Management

```bash
# Update version in pyproject.toml
# Update version in mcp_visualization/__init__.py

# Example version bump
sed -i 's/version = "0.1.0"/version = "0.1.1"/' pyproject.toml
sed -i 's/__version__ = "0.1.0"/__version__ = "0.1.1"/' mcp_visualization/__init__.py
```

### Git Workflow

```bash
# Commit changes
git add .
git commit -m "v0.1.1: Add new features and improvements"

# Tag release
git tag v0.1.1
git push origin main --tags
```

### Automated Publishing Script

```bash
#!/bin/bash
# publish.sh - Automated publishing script

set -e  # Exit on any error

VERSION=$1
if [ -z "$VERSION" ]; then
    echo "Usage: ./publish.sh <version>"
    echo "Example: ./publish.sh 0.1.1"
    exit 1
fi

echo "🚀 Publishing version $VERSION to PyPI..."

# Update version
sed -i "s/version = \".*\"/version = \"$VERSION\"/" pyproject.toml
sed -i "s/__version__ = \".*\"/__version__ = \"$VERSION\"/" mcp_visualization/__init__.py

# Clean and build
rm -rf dist/ build/ *.egg-info/
python -m build

# Test upload to TestPyPI first
echo "📤 Testing upload to TestPyPI..."
twine upload --repository testpypi dist/*

# Wait for user confirmation
read -p "TestPyPI upload successful. Proceed with real PyPI? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📤 Uploading to PyPI..."
    twine upload dist/*
    
    # Git operations
    git add .
    git commit -m "v$VERSION: Release to PyPI"
    git tag "v$VERSION"
    git push origin main --tags
    
    echo "🎉 Successfully published version $VERSION!"
    echo "📦 Available at: https://pypi.org/project/mcp-visualization-duckdb/$VERSION/"
else
    echo "❌ Publication cancelled."
fi
```

## 🛠️ Troubleshooting

### Common Issues

**Build Failures:**
```bash
# Missing build dependencies
pip install build wheel setuptools

# Clean rebuild
rm -rf dist/ build/ *.egg-info/
python -m build
```

**Upload Failures:**
```bash
# Check credentials
twine check dist/*

# Test connection
twine upload --repository testpypi dist/* --verbose
```

**Import Errors:**
```bash
# Check package structure
python -c "import mcp_visualization; print('OK')"

# Check entry points
pip show -f mcp-visualization-duckdb
```

### Testing Different Python Versions

```bash
# Using pyenv or conda
pyenv install 3.8.16 3.9.16 3.10.10 3.11.3
pyenv local 3.8.16

# Test installation
pip install dist/*.whl
mcp-viz test
```

## 🎯 Quick Commands Reference

```bash
# Development cycle
pip install -e .                    # Install for development
mcp-viz test                        # Test functionality
python -m build                     # Build package
python test_package.py              # Validate package

# Publishing cycle  
twine upload --repository testpypi dist/*  # Test upload
twine upload dist/*                         # Real upload

# After publishing
pip install mcp-visualization-duckdb       # Test installation
mcp-viz configure                          # Test end-user experience
```

Your package is now ready for local testing and PyPI publication! 🚀