import sys
import os
import multiprocessing
import uvicorn
import webview
import socket
from time import sleep

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def start_server():
    """Start the FastAPI server using Uvicorn."""
    # Ensure we are in the correct directory if bundled
    if getattr(sys, 'frozen', False):
        os.chdir(sys._MEIPASS)
    
    # Import main to ensure PyInstaller traces all database models and dependencies
    import main
    uvicorn.run("main:app", host="127.0.0.1", port=8000, log_level="info")

def main():
    # Fix for multiprocessing in PyInstaller
    multiprocessing.freeze_support()

    # Check if server is already running
    if is_port_in_use(8000):
        print("Server already running on port 8000. Opening window...")
    else:
        # Start server in a separate process
        server_process = multiprocessing.Process(target=start_server)
        server_process.daemon = True
        server_process.start()
        
        # Wait for server to start
        retries = 10
        while not is_port_in_use(8000) and retries > 0:
            sleep(1)
            retries -= 1

    # Create and open the webview window
    # We use a premium-looking title and window configuration
    webview.create_window(
        'KastomPOS - ERP & Point of Sale',
        'http://127.0.0.1:8000',
        width=1280,
        height=800,
        min_size=(1024, 768),
        confirm_close=True,
        text_select=True
    )

    # Start the webview GUI
    webview.start()

    # If the window is closed, we should ideally cleanup
    # Note: In some environments, the main process exit will kill daemon children anyway
    sys.exit()

if __name__ == "__main__":
    main()
