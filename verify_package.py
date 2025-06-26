#!/usr/bin/env python3
"""
Quick verification that package is ready for PyPI publication
"""

import sys
from pathlib import Path


def check_file_exists(file_path, description):
    """Check if a file exists"""
    if Path(file_path).exists():
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description} missing: {file_path}")
        return False


def check_package_structure():
    """Verify package structure"""
    print("📦 Checking package structure...")
    
    required_files = [
        ("pyproject.toml", "Package configuration"),
        ("LICENSE", "License file"),
        ("README.md", "Documentation"),
        ("MANIFEST.in", "Package manifest"),
        ("mcp_visualization/__init__.py", "Package init"),
        ("mcp_visualization/cli.py", "CLI module"),
        ("mcp_visualization/claude_config.py", "Config manager"),
        ("mcp_visualization/server.py", "Server entry point"),
    ]
    
    all_good = True
    for file_path, description in required_files:
        if not check_file_exists(file_path, description):
            all_good = False
    
    return all_good


def check_package_metadata():
    """Check package metadata"""
    print("\n📋 Checking package metadata...")
    
    try:
        with open("pyproject.toml", "r") as f:
            content = f.read()
        
        checks = [
            ("name = \"mcp-visualization-duckdb\"", "Package name"),
            ("version = \"0.0.2\"", "Version number"),
            ("description = ", "Description"),
            ("MIT", "License"),
            ("mcp-viz = ", "CLI entry point"),
        ]
        
        all_good = True
        for check, description in checks:
            if check in content:
                print(f"✅ {description} configured")
            else:
                print(f"❌ {description} missing or incorrect")
                all_good = False
        
        return all_good
        
    except Exception as e:
        print(f"❌ Error reading pyproject.toml: {e}")
        return False


def test_basic_imports():
    """Test that basic imports work"""
    print("\n🔍 Testing basic imports...")
    
    try:
        # Test package import
        import mcp_visualization
        print(f"✅ Package version: {mcp_visualization.__version__}")
        
        # Test config manager
        from mcp_visualization.claude_config import ClaudeDesktopConfigManager
        manager = ClaudeDesktopConfigManager()
        status = manager.get_status()
        print(f"✅ Config manager working on {status['platform']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False


def check_git_status():
    """Check git repository status"""
    print("\n🔧 Git repository check...")
    
    if Path(".git").exists():
        print("✅ Git repository initialized")
        
        # Check if we have a .gitignore
        if Path(".gitignore").exists():
            print("✅ .gitignore file present")
        else:
            print("⚠️  .gitignore file missing (recommended)")
        
        return True
    else:
        print("⚠️  Not a git repository (recommended for PyPI)")
        return False


def main():
    """Run all verification checks"""
    print("🎯 MCP Visualization Package - Publication Readiness Check")
    print("=" * 60)
    
    checks = [
        ("Package Structure", check_package_structure),
        ("Package Metadata", check_package_metadata),
        ("Basic Imports", test_basic_imports),
        ("Git Repository", check_git_status),
    ]
    
    results = []
    for check_name, check_func in checks:
        result = check_func()
        results.append(result)
    
    print("\n" + "=" * 60)
    print("📊 Verification Summary")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print("🎉 ALL CHECKS PASSED! Package is ready for PyPI publication.")
        print("\n📖 Next steps:")
        print("   1. Read PUBLISH_GUIDE.md for detailed instructions")
        print("   2. Install build tools: pip install build twine")
        print("   3. Build package: python -m build")
        print("   4. Test upload: twine upload --repository testpypi dist/*")
        print("   5. Real upload: twine upload dist/*")
        print("\n🚀 Your package will be available at:")
        print("   https://pypi.org/project/mcp-visualization-duckdb/")
        
    else:
        print(f"⚠️  {total - passed} check(s) failed. Please fix before publication.")
        print("\n🔧 See error messages above for details.")
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())