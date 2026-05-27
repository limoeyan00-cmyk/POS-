import PyInstaller.__main__
import os
import shutil
import sys

def build():
    print("Starting build process for KastomPOS Desktop...")
    
    # Remove previous build folders
    for folder in ['build', 'dist']:
        if os.path.exists(folder):
            print(f"Cleaning up {folder}...")
            shutil.rmtree(folder)

    separator = ';' if sys.platform.startswith('win') else ':'
    added_files = []

    # Include .env if it exists
    if os.path.exists('.env'):
        added_files.append(f'.env{separator}.')

    # Detect icon
    icon_args = []
    for ic in ['static/favicon.ico', 'icon.ico']:
        if os.path.exists(ic):
            icon_args = [f'--icon={ic}']
            print(f"Using icon: {ic}")
            break

    args = [
        'main.py',
        '--name=KastomPOS',
        '--onefile',
        '--windowed',
        # hidden imports for SQLAlchemy SQLite
        '--hidden-import=sqlalchemy.dialects.sqlite',
        # hidden imports for local package structures
        '--hidden-import=app',
        '--hidden-import=app.core',
        '--hidden-import=app.core.models',
        '--hidden-import=app.services',
        '--hidden-import=app.services.database',
        '--hidden-import=app.ui',
        '--hidden-import=app.ui.login',
        '--hidden-import=app.ui.main_window',
        '--hidden-import=app.ui.dashboard',
        '--hidden-import=app.ui.customers',
        '--hidden-import=app.ui.staff',
        # Collect full package metadata
        '--collect-all=sqlalchemy',
    ]

    args += icon_args

    for file_mapping in added_files:
        args.append(f'--add-data={file_mapping}')

    print(f"Running PyInstaller with {len(args)} arguments...")
    PyInstaller.__main__.run(args)

    print("\nBUILD COMPLETE!")
    print("   Standalone EXE -> dist/KastomPOS.exe")
    print("   Run the Inno Setup compiler on installer.iss to create the Setup wizard.")

if __name__ == "__main__":
    build()
