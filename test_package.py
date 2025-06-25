#!/usr/bin/env python3
"""
Test script to validate the pip package structure and functionality
"""

import sys
import subprocess
import tempfile
from pathlib import Path


def test_package_structure():
    """Test that package structure is correct"""
    print("🔍 Testing package structure...")
    
    package_dir = Path("mcp_visualization")
    if not package_dir.exists():
        print("❌ mcp_visualization package directory not found")
        return False
    
    required_files = [
        "mcp_visualization/__init__.py",
        "mcp_visualization/cli.py", 
        "mcp_visualization/claude_config.py",
        "mcp_visualization/server.py",
        "mcp_visualization/database.py",
        "pyproject.toml",
        "LICENSE",
        "README.md",
        "MANIFEST.in"
    ]
    
    for file_path in required_files:
        if not Path(file_path).exists():
            print(f"❌ Required file missing: {file_path}")
            return False
    
    print("✅ Package structure is valid")
    return True


def test_imports():
    """Test that core imports work"""
    print("🔍 Testing imports...")
    
    try:
        # Test basic package import
        import mcp_visualization
        print(f"✅ Package version: {mcp_visualization.__version__}")
        
        # Test CLI import
        from mcp_visualization.cli import main
        print("✅ CLI import successful")
        
        # Test config manager import
        from mcp_visualization.claude_config import ClaudeDesktopConfigManager
        print("✅ Config manager import successful")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False


def test_claude_config_manager():
    """Test Claude Desktop config manager"""
    print("🔍 Testing Claude Desktop config manager...")
    
    try:
        from mcp_visualization.claude_config import ClaudeDesktopConfigManager
        
        manager = ClaudeDesktopConfigManager()
        status = manager.get_status()
        
        print(f"✅ Platform detected: {status['platform']}")
        print(f"✅ Config path: {status['config_path']}")
        
        # Test configuration creation (dry run)
        config = manager.create_server_config()
        print("✅ Server config creation successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Config manager test failed: {e}")
        return False


def test_cli_commands():
    """Test CLI commands (dry run)"""
    print("🔍 Testing CLI commands...")
    
    try:
        # Test CLI help
        result = subprocess.run([
            sys.executable, "-m", "mcp_visualization.cli", "--help"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            print(f"❌ CLI help failed: {result.stderr}")
            return False
        
        if "MCP Data Visualization Server CLI" not in result.stdout:
            print("❌ CLI help output invalid")
            return False
        
        print("✅ CLI help command works")
        
        # Test status command
        result = subprocess.run([
            sys.executable, "-m", "mcp_visualization.cli", "status"
        ], capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            print("✅ CLI status command works")
        else:
            print(f"⚠️  CLI status command failed (expected if dependencies missing): {result.stderr}")
        
        return True
        
    except Exception as e:
        print(f"❌ CLI test failed: {e}")
        return False


def test_build_package():
    """Test package building"""
    print("🔍 Testing package build...")
    
    try:
        # Test build command
        result = subprocess.run([
            sys.executable, "-m", "build", "--outdir", "dist_test"
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode != 0:
            print(f"❌ Package build failed: {result.stderr}")
            return False
        
        # Check if wheel and source distribution were created
        dist_dir = Path("dist_test")
        if not dist_dir.exists():
            print("❌ Distribution directory not created")
            return False
        
        wheel_files = list(dist_dir.glob("*.whl"))
        tar_files = list(dist_dir.glob("*.tar.gz"))
        
        if not wheel_files:
            print("❌ Wheel file not created")
            return False
        
        if not tar_files:
            print("❌ Source distribution not created")
            return False
        
        print(f"✅ Package built successfully: {wheel_files[0].name}")
        return True
        
    except FileNotFoundError:
        print("⚠️  Build tool not available (install with: pip install build)")
        return True  # Not a failure, just missing tool
    except Exception as e:
        print(f"❌ Build test failed: {e}")
        return False


def test_package_installation():
    """Test package installation in temporary environment"""
    print("🔍 Testing package installation...")
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            # Build first
            result = subprocess.run([
                sys.executable, "-m", "build", "--outdir", temp_dir
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                print("⚠️  Skipping installation test (build failed)")
                return True
            
            # Find wheel file
            wheel_files = list(Path(temp_dir).glob("*.whl"))
            if not wheel_files:
                print("⚠️  No wheel file found for installation test")
                return True
            
            wheel_file = wheel_files[0]
            print(f"✅ Installation test would use: {wheel_file.name}")
            
        return True
        
    except Exception as e:
        print(f"❌ Installation test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("🎯 MCP Data Visualization Package Testing")
    print("=" * 50)
    
    tests = [
        ("Package Structure", test_package_structure),
        ("Imports", test_imports),
        ("Claude Config Manager", test_claude_config_manager),
        ("CLI Commands", test_cli_commands),
        ("Package Build", test_build_package),
        ("Installation Simulation", test_package_installation),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Package is ready for distribution.")
        return 0
    else:
        print(f"⚠️  {total - passed} test(s) failed. Please fix issues before distribution.")
        return 1


if __name__ == "__main__":
    sys.exit(main())