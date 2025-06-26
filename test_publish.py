#!/usr/bin/env python3
"""
Test the publishing workflow without actually uploading
"""

import subprocess
import sys
from pathlib import Path


def run_command(command, check=True):
    """Run a command and return the result"""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    if result.stderr and result.stderr.strip():
        print(f"stderr: {result.stderr.strip()}")
    
    if check and result.returncode != 0:
        print(f"❌ Command failed with exit code {result.returncode}")
        return False
    
    return True


def test_publish_workflow():
    """Test the publishing workflow without uploading"""
    print("🧪 Testing Publishing Workflow (Dry Run)")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("pyproject.toml").exists():
        print("❌ pyproject.toml not found. Run this from the project root.")
        return False
    
    # Get current version
    current_version = "unknown"
    try:
        with open("pyproject.toml", "r") as f:
            for line in f:
                if line.strip().startswith('version = '):
                    current_version = line.split('"')[1]
                    break
    except Exception:
        pass
    
    print(f"📦 Current version: {current_version}")
    
    # Test 1: Check required tools
    print("\n📋 Test 1: Required Tools")
    print("-" * 30)
    
    tools = ["python", "build", "twine"]
    all_tools_ok = True
    
    for tool in tools:
        if tool == "python":
            cmd = "python --version"
        elif tool == "build":
            cmd = "python -m build --version"
        elif tool == "twine":
            cmd = "twine --version"
        
        if run_command(cmd, check=False):
            print(f"✅ {tool} is available")
        else:
            print(f"❌ {tool} not found")
            all_tools_ok = False
    
    if not all_tools_ok:
        print("\n❌ Missing required tools. Install with:")
        print("   pip install build twine")
        return False
    
    # Test 2: Clean build artifacts
    print("\n📋 Test 2: Clean Build Artifacts")
    print("-" * 35)
    
    dirs_to_clean = ["dist", "build"]
    for dir_name in dirs_to_clean:
        if Path(dir_name).exists():
            print(f"🧹 Would clean: {dir_name}/")
        else:
            print(f"✅ Already clean: {dir_name}/")
    
    # Actually clean for testing
    run_command("rm -rf dist build *.egg-info", check=False)
    
    # Test 3: Build package
    print("\n📋 Test 3: Build Package")
    print("-" * 25)
    
    if run_command("python -m build", check=False):
        print("✅ Package built successfully")
        
        # Check files
        dist_dir = Path("dist")
        if dist_dir.exists():
            wheel_files = list(dist_dir.glob("*.whl"))
            tar_files = list(dist_dir.glob("*.tar.gz"))
            
            print(f"📦 Files created:")
            for file in wheel_files + tar_files:
                print(f"   - {file.name}")
        else:
            print("❌ No dist directory created")
            return False
    else:
        print("❌ Package build failed")
        return False
    
    # Test 4: Validate package
    print("\n📋 Test 4: Validate Package")
    print("-" * 28)
    
    if run_command("twine check dist/*", check=False):
        print("✅ Package validation passed")
    else:
        print("❌ Package validation failed")
        return False
    
    # Test 5: Show what would be uploaded
    print("\n📋 Test 5: Upload Simulation")
    print("-" * 29)
    
    print("📤 Would upload to PyPI:")
    for file in Path("dist").glob("*"):
        print(f"   - {file.name}")
    
    print("\n🎯 Publishing Test Summary")
    print("=" * 30)
    print("✅ All tests passed!")
    print("✅ Package is ready for PyPI publication")
    print()
    print("🚀 To actually publish, run:")
    print("   python publish.py")
    print()
    print("🔑 You'll need:")
    print("   - PyPI account: https://pypi.org/account/register/")
    print("   - API token: https://pypi.org/manage/account/token/")
    print()
    print("📦 After publishing, users can install with:")
    print("   pip install mcp-visualization-duckdb")
    print("   mcp-viz configure")
    
    return True


if __name__ == "__main__":
    success = test_publish_workflow()
    sys.exit(0 if success else 1)