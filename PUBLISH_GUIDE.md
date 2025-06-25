# 🚀 Complete PyPI Publishing Guide

## ✅ Current Status

Your package is **ready for publication**! The local tests confirm:
- ✅ Package structure is valid
- ✅ Basic imports work correctly  
- ✅ Claude Desktop config manager functional
- ✅ Version and metadata configured

## 🛠️ Setup for Publishing

### Step 1: Install Required Tools

```bash
# Install publishing tools
pip install build twine wheel

# For development (optional)
pip install black isort mypy pytest
```

### Step 2: Create PyPI Accounts

1. **Main PyPI Account**: https://pypi.org/account/register/
2. **Test PyPI Account**: https://test.pypi.org/account/register/

### Step 3: Generate API Tokens

1. Go to **PyPI Account Settings** → **API tokens**
2. Create token with scope: "Entire account" or specific project
3. Copy the token (starts with `pypi-`)

## 📦 Local Testing & Building

### Test Installation Locally

```bash
# Clone and enter your project
cd mcp-visualization-duckdb

# Install in development mode
pip install -e .

# Test CLI (basic functions)
python -c "from mcp_visualization.claude_config import ClaudeDesktopConfigManager; print('✅ Works!')"
```

### Build the Package

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info/

# Build source and wheel distributions
python -m build

# Verify files created
ls -la dist/
# Should show:
# mcp_visualization_duckdb-0.1.0.tar.gz
# mcp_visualization_duckdb-0.1.0-py3-none-any.whl
```

### Validate Package

```bash
# Check package integrity
twine check dist/*

# Should output: "PASSED" for all files
```

## 🧪 Test Upload to TestPyPI

### Configure Credentials

```bash
# Option 1: Command line (one-time)
twine upload --repository testpypi dist/* --username __token__ --password pypi-YourTestTokenHere

# Option 2: Config file (persistent)
cat > ~/.pypirc << 'EOF'
[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YourTestTokenHere
EOF
```

### Upload to TestPyPI

```bash
# Upload to test repository
twine upload --repository testpypi dist/*

# You should see:
# Uploading distributions to https://test.pypi.org/legacy/
# Uploading mcp_visualization_duckdb-0.1.0-py3-none-any.whl
# Uploading mcp_visualization_duckdb-0.1.0.tar.gz
```

### Test Installation from TestPyPI

```bash
# Create fresh environment
python -m venv test_install
source test_install/bin/activate  # Linux/Mac
# test_install\Scripts\activate   # Windows

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ mcp-visualization-duckdb

# Test the installation
python -c "import mcp_visualization; print(f'Version: {mcp_visualization.__version__}')"

# Test CLI (if dependencies available)
mcp-viz --help

# Clean up
deactivate
rm -rf test_install/
```

## 🌟 Publish to Real PyPI

### Final Checks

- [ ] ✅ Version number updated in `pyproject.toml` and `__init__.py`
- [ ] ✅ README.md is comprehensive and accurate
- [ ] ✅ All tests pass locally
- [ ] ✅ TestPyPI upload and installation successful
- [ ] ✅ No sensitive information in code

### Upload to PyPI

```bash
# Add PyPI credentials to ~/.pypirc
cat >> ~/.pypirc << 'EOF'
[pypi]
username = __token__
password = pypi-YourRealTokenHere
EOF

# Upload to real PyPI
twine upload dist/*

# Success message:
# Uploading distributions to https://upload.pypi.org/legacy/
# Uploading mcp_visualization_duckdb-0.1.0-py3-none-any.whl
# Uploading mcp_visualization_duckdb-0.1.0.tar.gz
```

### Verify Publication

```bash
# Check package page
# Visit: https://pypi.org/project/mcp-visualization-duckdb/

# Test installation from PyPI
pip install mcp-visualization-duckdb

# Test end-to-end functionality
mcp-viz configure --auto
```

## 🔄 Version Updates

### For Future Releases

```bash
# 1. Update version numbers
sed -i 's/version = "0.1.0"/version = "0.1.1"/' pyproject.toml
sed -i 's/__version__ = "0.1.0"/__version__ = "0.1.1"/' mcp_visualization/__init__.py

# 2. Build new version
rm -rf dist/ build/ *.egg-info/
python -m build

# 3. Upload
twine upload dist/*
```

## 🎯 Quick Publishing Script

Create `publish.sh`:

```bash
#!/bin/bash
set -e

VERSION=${1:-"0.1.0"}
echo "🚀 Publishing mcp-visualization-duckdb v$VERSION"

# Update versions
sed -i "s/version = \".*\"/version = \"$VERSION\"/" pyproject.toml
sed -i "s/__version__ = \".*\"/__version__ = \"$VERSION\"/" mcp_visualization/__init__.py

# Clean and build
rm -rf dist/ build/ *.egg-info/
python -m build

# Validate
twine check dist/*

# Upload to TestPyPI first
echo "📤 Uploading to TestPyPI..."
twine upload --repository testpypi dist/*

# Confirm before real upload
read -p "TestPyPI successful? Upload to real PyPI? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📤 Uploading to PyPI..."
    twine upload dist/*
    echo "🎉 Published successfully!"
    echo "📦 https://pypi.org/project/mcp-visualization-duckdb/$VERSION/"
fi
```

Usage:
```bash
chmod +x publish.sh
./publish.sh 0.1.0
```

## 🛠️ Troubleshooting

### Common Issues

**"Package already exists"**
```bash
# Increment version number and rebuild
# PyPI doesn't allow overwriting existing versions
```

**"Invalid credentials"**
```bash
# Check API token is correct
# Ensure token has appropriate scope
twine upload dist/* --username __token__ --password pypi-YourTokenHere
```

**"Missing dependencies during install"**
```bash
# Users might need to install MCP separately
# This is expected - your package focuses on configuration
pip install mcp>=1.0.0  # Users install this separately
```

### Package Structure Issues

**Import errors after installation**
```bash
# Check MANIFEST.in includes all necessary files
# Rebuild package with python -m build
```

## 📈 Post-Publication

### Monitoring

- **Download stats**: https://pypistats.org/packages/mcp-visualization-duckdb
- **Package health**: https://pypi.org/project/mcp-visualization-duckdb/
- **Issues**: Monitor GitHub issues for user feedback

### Documentation Updates

- Update README.md with PyPI installation instructions
- Add badges: ![PyPI version](https://badge.fury.io/py/mcp-visualization-duckdb.svg)
- Link to PyPI in project documentation

## 🎉 Success Indicators

After successful publication, users can:

```bash
# One-command installation
pip install mcp-visualization-duckdb

# Automatic configuration
mcp-viz configure

# Ready to use with Claude Desktop!
```

**Your package is ready for PyPI! 🚀**

The core functionality is working, and the package structure is properly configured for distribution.