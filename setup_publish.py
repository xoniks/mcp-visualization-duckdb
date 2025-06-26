#!/usr/bin/env python3
"""
Setup script to install publishing dependencies and then publish
"""

import subprocess
import sys
import os


def run_command(command):
    """Run a command and show output"""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True)
    return result.returncode == 0


def main():
    print("🔧 Setting up publishing environment...")
    print("=" * 50)
    
    # Install required tools
    print("📦 Installing build tools...")
    if not run_command("pip install build twine wheel"):
        print("❌ Failed to install build tools")
        return 1
    
    print("✅ Build tools installed successfully!")
    print()
    print("🚀 Now you can run the publisher:")
    print("   python publish.py")
    print()
    print("Or run it automatically now? (y/N): ", end="")
    
    try:
        response = input().strip().lower()
        if response == 'y':
            print("🚀 Running publisher...")
            os.system("python publish.py")
    except KeyboardInterrupt:
        print("\n👋 Setup complete!")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())