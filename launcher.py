import sys
import os
import threading
import socket
import time
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("kastompos")


def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        return s.connect_ex(("127.0.0.1", port)) == 0


def set_app_dir():
    """
    Point the working directory at the right place so templates/static
    are found whether we are running frozen (PyInstaller) or from source.
    """
    if getattr(sys, "frozen", False):
        # PyInstaller extracts everything to sys._MEIPASS at runtime
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base)


def start_server():
    """Run FastAPI/Uvicorn in a daemon thread (NOT a subprocess).
    Using threads avoids the Windows multiprocessing re-spawn bug where
    PyInstaller frozen exes re-execute __main__ instead of the target fn.
    """
    import uvicorn
    # Import app here so PyInstaller can trace all dependencies
    import main  # noqa: F401  (side-effect: registers routes / models)
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        log_level="warning",  # keep console quiet in windowed mode
    )


def wait_for_server(port: int, timeout: int = 30) -> bool:
    """Block until the server accepts connections or timeout expires."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        if is_port_in_use(port):
            return True
        time.sleep(0.5)
    return False


def main():
    set_app_dir()

    if is_port_in_use(8000):
        log.info("Server already running on port 8000 - reusing it.")
    else:
        # Daemon thread: dies automatically when the main window closes
        server_thread = threading.Thread(target=start_server, daemon=True)
        server_thread.start()

        log.info("Waiting for server to start...")
        if not wait_for_server(8000, timeout=30):
            # Show a user-friendly error if the server never came up
            import webview
            webview.create_window(
                "KastomPOS - Startup Error",
                html=(
                    "<h2 style='font-family:sans-serif;color:#c0392b;padding:40px'>"
                    "KastomPOS failed to start the internal server.<br>"
                    "<small>Please restart the application.<br>"
                    "If the problem persists, check that port 8000 is not in use.</small>"
                    "</h2>"
                ),
                width=600,
                height=250,
            )
            import webview as wv
            wv.start()
            sys.exit(1)

    import webview
    webview.create_window(
        "KastomPOS - ERP & Point of Sale",
        "http://127.0.0.1:8000",
        width=1280,
        height=800,
        min_size=(1024, 768),
        confirm_close=True,
        text_select=True,
    )
    webview.start()
    sys.exit(0)


if __name__ == "__main__":
    main()
