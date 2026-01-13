#!/usr/bin/env python3
"""
Build LCARS Framework as standalone EXE
Usage: python build_exe.py
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def main():
    print("""
        LCARS Framework - PyInstaller Build Script           
        Creating standalone EXE (one-file executable)         
    """)
    
    root_dir = Path(__file__).parent
    os.chdir(root_dir)
    
    # Clean previous builds
    print("🧹 Cleaning previous builds...")
    for path in ['dist', 'build', '*.spec']:
        if path == '*.spec':
            for spec_file in root_dir.glob('*.spec'):
                if spec_file.name not in ['lcars_framework.spec']:
                    spec_file.unlink()
        else:
            dir_path = root_dir / path
            if dir_path.exists():
                shutil.rmtree(dir_path)
    
    print("✓ Cleaned")
    
    # Build with PyInstaller
    print("\n🔨 Building with PyInstaller...")
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',
        '--windowed',
        '--name', 'LCARS-Framework',
        '--hidden-import=vispy',
        '--hidden-import=OpenGL',
        '--hidden-import=PyQt6',
        '--hidden-import=pandas',
        '--hidden-import=numpy',
        '--hidden-import=matplotlib',
        '--hidden-import=scipy',
        '--hidden-import=dotenv',
        'run.py',
    ]
    
    result = subprocess.run(cmd, capture_output=False)
    
    if result.returncode != 0:
        print("\n❌ Build FAILED")
        return 1
    
    print("\n✓ Build successful!")
    
    # Check result
    exe_path = root_dir / 'dist' / 'LCARS-Framework' / 'LCARS-Framework.exe'
    if not exe_path.exists():
        exe_path = root_dir / 'dist' / 'LCARS-Framework.exe'
    
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"\n📦 EXE created: {exe_path}")
        print(f"   Size: {size_mb:.1f} MB")
        print(f"   Run: {exe_path}")
    else:
        print("❌ EXE not found in expected location")
        return 1
    
    print("\n✅ Build Complete!")
    print("""
    Next steps:                                                   
    1. Run the EXE: dist/LCARS-Framework.exe                     
    2. Copy EXE to any Windows machine (Python NOT required!)    
    3. Share with others - it's portable!                        
    4. For debugging, run with console by removing --windowed flag  
    5. Enjoy the LCARS experience!
    """)
    return 0

if __name__ == '__main__':
    sys.exit(main())
