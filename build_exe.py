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

    # Define the separator based on the platform
    separator = ';' if sys.platform.startswith('win') else ':'
    
    added_files = [
        f'templates{separator}templates',
    ]
    
    # Only add .env if it exists
    if os.path.exists('.env'):
        added_files.append(f'.env{separator}.')
    
    # Include static folder or create a placeholder
    if os.path.exists('static') and os.listdir('static'):
        added_files.append(f'static{separator}static')
    else:
        os.makedirs('build_static', exist_ok=True)
        added_files.append(f'build_static{separator}static')

    # Detect if we have an icon
    icon_args = []
    icon_candidates = ['static/favicon.ico', 'icon.ico']
    for ic in icon_candidates:
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
        '--hidden-import=main',
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
        # pywebview Windows backend
        '--hidden-import=webview.platforms.winforms',
        '--hidden-import=clr',
        '--hidden-import=pythonnet',
        # SQLAlchemy dialects
        '--hidden-import=sqlalchemy.dialects.sqlite',
        # FastAPI internals
        '--hidden-import=fastapi.routing',
        '--hidden-import=multipart',
        # Collect full packages
        '--collect-all=webview',
        '--collect-all=uvicorn',
        '--collect-all=jinja2',
        '--collect-all=sqlalchemy',
        # Exclude unused heavy packages to keep EXE lean
        '--exclude-module=tkinter',
        '--exclude-module=matplotlib',
        '--exclude-module=numpy',
        '--exclude-module=pandas',
        '--exclude-module=scipy',
    ]

    args += icon_args

    # Add data files
    for file_mapping in added_files:
        args.append(f'--add-data={file_mapping}')

    print(f"Running PyInstaller with {len(args)} arguments...")
    PyInstaller.__main__.run(args)
    
    print("\nBUILD COMPLETE!")
    print("   Standalone EXE -> dist/KastomPOS.exe")
    print("   Run the Inno Setup compiler on installer.iss to create the Setup wizard.")

if __name__ == "__main__":
    build()
