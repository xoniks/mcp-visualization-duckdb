# 🪟 Windows Setup Guide

## 🚀 Quick Setup for Windows Users

### Step 1: Install Python Build Tools

```cmd
# Install required tools
pip install build twine wheel
```

### Step 2: Test the Package

```cmd
# Run Windows-compatible test
test_local.bat

# Or run Python verification
python verify_package.py
```

### Step 3: Build and Publish

```cmd
# Build the package
python -m build

# Publish (automated script)
publish.bat 0.1.0
```

## 🔧 Windows-Specific Considerations

### Line Endings
- ✅ Added `.gitattributes` to handle line endings automatically
- ✅ Shell scripts (`.sh`) use LF endings
- ✅ Batch files (`.bat`) use CRLF endings
- ✅ Python files use LF endings for consistency

### Virtual Environments
```cmd
# Create virtual environment (Windows)
python -m venv venv
venv\Scripts\activate

# Install package
pip install -e .

# Test CLI
mcp-viz --help
```

### Path Issues
Windows paths work correctly with the package:
- ✅ Claude Desktop config: `%APPDATA%\Claude\claude_desktop_config.json`
- ✅ Python paths: Automatic detection of `Scripts\python.exe`
- ✅ Database paths: Uses forward slashes in JSON for compatibility

## 🎯 Publishing Commands

### Test Upload
```cmd
# Upload to TestPyPI
twine upload --repository testpypi dist\*
```

### Production Upload  
```cmd
# Upload to PyPI
twine upload dist\*
```

### Automated Publishing
```cmd
# Use the provided script
publish.bat 0.1.0
```

## 🛠️ Troubleshooting Windows Issues

### "Command not found" errors
```cmd
# Ensure Python Scripts directory is in PATH
python -m pip install --user --upgrade pip
```

### Git line ending warnings
```cmd
# Configure git for Windows (one-time setup)
git config --global core.autocrlf true
git config --global core.eol crlf
```

### Virtual environment issues  
```cmd
# Use full path if activation fails
C:\path\to\your\project\venv\Scripts\activate.bat
```

## ✅ Windows Testing Checklist

- [ ] `test_local.bat` runs successfully
- [ ] `python verify_package.py` passes all checks
- [ ] `python -m build` creates dist files
- [ ] `mcp-viz --help` works after installation
- [ ] Claude Desktop config path detected correctly

Your package is fully Windows-compatible! 🎉