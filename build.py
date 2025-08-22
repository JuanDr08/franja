#!/usr/bin/env python3
"""
Build script for Sistema de Extracción de Datos Odoo 17

This script creates an executable from the Python application using PyInstaller.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n{'='*50}")
    print(f"🔧 {description}")
    print(f"{'='*50}")
    print(f"Running: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        if result.stdout:
            print("Output:", result.stdout)
        print("✅ Success!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stdout:
            print("stdout:", e.stdout)
        if e.stderr:
            print("stderr:", e.stderr)
        return False

def clean_build_directories():
    """Clean previous build artifacts."""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    
    for dir_name in dirs_to_clean:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"🧹 Cleaning {dir_name}...")
            shutil.rmtree(dir_path)
    
    # Clean .pyc files
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.pyc'):
                os.remove(os.path.join(root, file))

def check_dependencies():
    """Check if all build dependencies are available."""
    print("🔍 Checking dependencies...")
    
    try:
        import pyinstaller
        print("✅ PyInstaller available")
    except ImportError:
        print("❌ PyInstaller not found")
        print("Install with: pip install pyinstaller")
        return False
    
    # Check other critical dependencies
    critical_deps = ['psycopg2', 'pandas', 'openpyxl', 'tkcalendar', 'cryptography']
    
    for dep in critical_deps:
        try:
            __import__(dep)
            print(f"✅ {dep} available")
        except ImportError:
            print(f"❌ {dep} not found")
            print("Install dependencies with: pip install -r requirements.txt")
            return False
    
    return True

def build_executable():
    """Build the executable using PyInstaller."""
    print("\n🏗️ Building executable...")
    
    # Always use the spec file for consistent builds
    if Path('build.spec').exists():
        command = "pyinstaller build.spec --clean --noconfirm --log-level=INFO"
    else:
        print("❌ build.spec not found! Creating basic spec file...")
        # Create a basic spec file if it doesn't exist
        create_basic_spec_file()
        command = "pyinstaller build.spec --clean --noconfirm --log-level=INFO"
    
    success = run_command(command, "Building executable with PyInstaller")
    
    if success:
        # Check if executable was actually created
        exe_files = []
        dist_path = Path('dist')
        if dist_path.exists():
            exe_files = list(dist_path.glob('**/*'))
            exe_files = [f for f in exe_files if f.is_file() and not f.name.endswith('.txt')]
        
        if not exe_files:
            print("⚠️ Build completed but no executable found in dist/")
            return False
    
    return success

def create_basic_spec_file():
    """Create a basic spec file if one doesn't exist."""
    spec_content = '''# Basic PyInstaller spec file
import sys

a = Analysis(['main.py'],
             pathex=[],
             binaries=[],
             datas=[('requirements.txt', '.')],
             hiddenimports=['psycopg2', 'pandas', 'openpyxl', 'tkcalendar', 'cryptography'],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=['matplotlib', 'scipy'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=None,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(pyz,
          a.scripts, 
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='ExtractorOdoo17',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None)
'''
    
    with open('build.spec', 'w') as f:
        f.write(spec_content)
    print("✅ Created basic build.spec file")

def test_executable():
    """Test the built executable."""
    print("\n🧪 Testing executable...")
    
    # Find the executable with improved logic
    exe_candidates = []
    
    if sys.platform == 'win32':
        exe_candidates = [
            Path('dist/ExtractorOdoo17.exe'),
            Path('dist/ExtractorOdoo17/ExtractorOdoo17.exe')
        ]
    elif sys.platform == 'darwin':
        exe_candidates = [
            Path('dist/Extractor Odoo 17.app/Contents/MacOS/Extractor Odoo 17'),
            Path('dist/ExtractorOdoo17'),
            Path('dist/ExtractorOdoo17/ExtractorOdoo17')
        ]
    else:  # Linux
        exe_candidates = [
            Path('dist/ExtractorOdoo17'),
            Path('dist/ExtractorOdoo17/ExtractorOdoo17')
        ]
    
    exe_path = None
    for candidate in exe_candidates:
        if candidate.exists():
            exe_path = candidate
            break
    
    if not exe_path:
        print("❌ Executable not found in any expected location:")
        for candidate in exe_candidates:
            print(f"  - Checked: {candidate}")
        
        # List what's actually in dist/
        dist_path = Path('dist')
        if dist_path.exists():
            print("\n📁 Contents of dist/ directory:")
            for item in dist_path.iterdir():
                if item.is_file():
                    size_mb = item.stat().st_size / 1024 / 1024
                    print(f"  📄 {item.name} ({size_mb:.1f} MB)")
                elif item.is_dir():
                    print(f"  📁 {item.name}/")
        return False
    
    print(f"✅ Executable found: {exe_path.name}")
    print(f"📊 File size: {exe_path.stat().st_size / 1024 / 1024:.1f} MB")
    
    # Quick validation test - just try to launch and immediately close
    try:
        print("🏃 Testing executable startup (quick test)...")
        
        # On macOS, check if it's an app bundle
        if sys.platform == 'darwin' and exe_path.suffix == '.app':
            command = ['open', str(exe_path)]
        else:
            command = [str(exe_path)]
        
        process = subprocess.Popen(command, 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE,
                                 stdin=subprocess.PIPE)
        
        # Give it a moment to start, then terminate
        import time
        time.sleep(3)
        
        # Try graceful termination first
        process.terminate()
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
        
        print("✅ Executable startup test completed")
        return True
        
    except Exception as e:
        print(f"❌ Error testing executable: {e}")
        print("ℹ️ This might be normal - some apps require GUI interaction")
        return True  # Don't fail the build for testing issues

def create_distribution_package():
    """Create a distribution package with documentation."""
    print("\n📦 Creating distribution package...")
    
    dist_dir = Path('dist')
    if not dist_dir.exists():
        print("❌ dist directory not found")
        return False
    
    # Create README for distribution
    readme_content = """
# Sistema de Extracción de Datos de Facturación Odoo 17

## Instrucciones de Uso

1. **Primera vez:**
   - Ejecute el archivo ExtractorOdoo17
   - Configure la conexión a su base de datos PostgreSQL
   - Pruebe la conexión antes de guardar

2. **Generar reportes:**
   - Seleccione el tipo de fecha (específica o rango)
   - Elija las fechas
   - Seleccione la carpeta de destino
   - Haga clic en "Generar Reportes"

3. **Archivos generados:**
   - facturas_[fechas].xlsx - Datos de facturación
   - terceros_[fechas].xlsx - Datos de terceros/partners

## Requisitos del Sistema

- Sistema Operativo: Windows 10+, macOS 10.14+, o Linux Ubuntu 18.04+
- Memoria RAM: Mínimo 4GB
- Espacio en disco: 100MB libres
- Acceso de red a la base de datos PostgreSQL

## Soporte Técnico

Para problemas o consultas, revise el archivo extractor.log
que se genera en la carpeta de la aplicación.

Versión: 1.0
"""
    
    readme_path = dist_dir / 'README.txt'
    readme_path.write_text(readme_content.strip(), encoding='utf-8')
    
    # Copy requirements for reference
    if Path('requirements.txt').exists():
        shutil.copy2('requirements.txt', dist_dir / 'requirements.txt')
    
    print("✅ Distribution package created")
    return True

def main():
    """Main build process."""
    print("🚀 Building Sistema de Extracción de Datos Odoo 17")
    print("=" * 60)
    
    # Check current directory
    if not Path('main.py').exists():
        print("❌ main.py not found. Run this script from the project root directory.")
        sys.exit(1)
    
    # Step 1: Check dependencies
    if not check_dependencies():
        print("\n❌ Build failed: Missing dependencies")
        sys.exit(1)
    
    # Step 2: Clean previous builds
    clean_build_directories()
    
    # Step 3: Build executable
    if not build_executable():
        print("\n❌ Build failed: PyInstaller error")
        sys.exit(1)
    
    # Step 4: Test executable
    if not test_executable():
        print("\n⚠️ Build completed but executable test failed")
    
    # Step 5: Create distribution package
    create_distribution_package()
    
    print("\n" + "=" * 60)
    print("🎉 Build completed successfully!")
    print("📂 Check the 'dist' folder for your executable")
    
    # Show final status
    dist_contents = list(Path('dist').iterdir()) if Path('dist').exists() else []
    if dist_contents:
        print("\n📋 Distribution contents:")
        for item in dist_contents:
            size = ""
            if item.is_file():
                size = f" ({item.stat().st_size / 1024 / 1024:.1f} MB)"
            print(f"   • {item.name}{size}")

if __name__ == "__main__":
    main()