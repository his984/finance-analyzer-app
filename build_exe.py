#!/usr/bin/env python3
"""
Build script for Finance Analyzer executable.
This script automates the process of creating a standalone executable.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = ['pyinstaller', 'matplotlib', 'pandas', 'customtkinter']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"Missing required packages: {', '.join(missing_packages)}")
        print("Please install them using: pip install " + " ".join(missing_packages))
        return False
    
    return True

def clean_build_directories():
    """Clean previous build artifacts."""
    directories_to_clean = ['build', 'dist', '__pycache__']
    
    for directory in directories_to_clean:
        if os.path.exists(directory):
            print(f"Cleaning {directory}...")
            shutil.rmtree(directory)
    
    # Clean .spec files except the main one
    for spec_file in Path('.').glob('*.spec'):
        if spec_file.name != 'finance_analyzer.spec':
            spec_file.unlink()

def build_executable():
    """Build the executable using PyInstaller."""
    try:
        print("Building executable...")
        
        # Use the spec file
        cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--clean',
            'finance_analyzer.spec'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Executable built successfully!")
            print(f"Output location: {os.path.abspath('dist')}")
            return True
        else:
            print("❌ Build failed!")
            print("Error output:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Build failed with exception: {e}")
        return False

def verify_executable():
    """Verify the executable was created and is accessible."""
    exe_path = Path('dist') / 'Finance Analyzer.exe'
    
    if exe_path.exists():
        print(f"✅ Executable found at: {exe_path}")
        print(f"Size: {exe_path.stat().st_size / (1024*1024):.1f} MB")
        return True
    else:
        print("❌ Executable not found!")
        return False

def main():
    """Main build process."""
    print("🚀 Finance Analyzer - Executable Builder")
    print("=" * 50)
    
    # Check dependencies
    print("1. Checking dependencies...")
    if not check_dependencies():
        return False
    
    # Clean previous builds
    print("2. Cleaning previous builds...")
    clean_build_directories()
    
    # Build executable
    print("3. Building executable...")
    if not build_executable():
        return False
    
    # Verify executable
    print("4. Verifying executable...")
    if not verify_executable():
        return False
    
    print("\n🎉 Build completed successfully!")
    print("\nNext steps:")
    print("1. Test the executable in the 'dist' folder")
    print("2. Test on a clean system without Python")
    print("3. Check that all features work correctly")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1) 