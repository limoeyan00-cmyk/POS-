import PyInstaller.__main__
import os
import shutil
import sys

def build():
    print("Starting build process for KastomPOS...")
    
    # Remove previous build folders
    for folder in ['build', 'dist', 'build_static']:
        if os.path.exists(folder):
            print(f"Cleaning up {folder}...")
            shutil.rmtree(folder)

    separator = ';' if sys.platform.startswith('win') else ':'

    # ------------------------------------------------------------------
    # DATA FILES
    # We include main.py, models.py, database.py as raw data files
    # (destination = '.', i.e. the root of sys._MEIPASS).
    # This is the only reliable way to make local scripts importable
    # from a PyInstaller --onefile --windowed bundle on Windows.
    # ------------------------------------------------------------------
    local_modules = ['main.py', 'models.py', 'database.py']
    added_files = []

    for mod in local_modules:
        if os.path.exists(mod):
            added_files.append(f'{mod}{separator}.')
            print(f"Adding local module: {mod}")
        else:
            print(f"WARNING: {mod} not found — bundle may fail!")

    added_files.append(f'templates{separator}templates')

    if os.path.exists('.env'):
        added_files.append(f'.env{separator}.')

    if os.path.exists('static') and os.listdir('static'):
        added_files.append(f'static{separator}static')
    else:
        os.makedirs('build_static', exist_ok=True)
        added_files.append(f'build_static{separator}static')

    # Detect icon
    icon_args = []
    for ic in ['static/favicon.ico', 'icon.ico']:
        if os.path.exists(ic):
            icon_args = [f'--icon={ic}']
            print(f"Using icon: {ic}")
            break

    args = [
        'launcher.py',
        '--name=KastomPOS',
        '--onefile',
        '--windowed',
        # Uvicorn internals
        '--hidden-import=uvicorn.logging',
        '--hidden-import=uvicorn.loops',
        '--hidden-import=uvicorn.loops.auto',
        '--hidden-import=uvicorn.protocols',
        '--hidden-import=uvicorn.protocols.http',
        '--hidden-import=uvicorn.protocols.http.auto',
        '--hidden-import=uvicorn.protocols.websockets',
        '--hidden-import=uvicorn.protocols.websockets.auto',
        '--hidden-import=uvicorn.lifespan',
        '--hidden-import=uvicorn.lifespan.on',
        # SQLAlchemy
        '--hidden-import=sqlalchemy.dialects.sqlite',
        # FastAPI
        '--hidden-import=fastapi.routing',
        '--hidden-import=multipart',
        # Collect full packages
        '--collect-all=uvicorn',
        '--collect-all=jinja2',
        '--collect-all=sqlalchemy',
        # Trim unused heavy packages
        '--exclude-module=tkinter',
        '--exclude-module=matplotlib',
        '--exclude-module=numpy',
        '--exclude-module=pandas',
        '--exclude-module=scipy',
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
