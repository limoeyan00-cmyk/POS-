import sys
import os

# CRITICAL FIX: In PyInstaller --onefile/--windowed mode, the bundle extraction
# directory (sys._MEIPASS) is NOT automatically on sys.path.
# We must add it manually before importing ANY local modules (main, models, database).
if getattr(sys, "frozen", False):
    _bundle_dir = sys._MEIPASS
    if _bundle_dir not in sys.path:
        sys.path.insert(0, _bundle_dir)

import threading
import socket
import time
import logging
import traceback

# Top-level import so PyInstaller analysis traces and bundles main.py
import main as app_module

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("kastompos")

_server_error = None


def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        return s.connect_ex(("127.0.0.1", port)) == 0


def start_server():
    """Run FastAPI/Uvicorn in a daemon thread."""
    global _server_error
    try:
        import uvicorn
        # Use the already-imported app object — no runtime module lookup
        uvicorn.run(
            app_module.app,
            host="127.0.0.1",
            port=8000,
            log_level="info",
        )
    except Exception:
        _server_error = traceback.format_exc()
        log.error("Server failed to start:\n%s", _server_error)


def wait_for_server(port: int, timeout: int = 30) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        if is_port_in_use(port):
            return True
        if _server_error:
            return False
        time.sleep(0.5)
    return False


def show_error_window(title: str, message: str):
    import webview
    html = f"""
    <html>
    <body style="font-family:sans-serif;background:#1a1a2e;color:#eee;padding:30px;margin:0">
      <h2 style="color:#e74c3c">KastomPOS - Startup Error</h2>
      <p style="color:#ccc">{title}</p>
      <pre style="background:#0d0d1a;padding:15px;border-radius:6px;font-size:12px;
                  color:#ff6b6b;overflow:auto;max-height:300px;white-space:pre-wrap">{message}</pre>
      <p style="color:#aaa;font-size:12px">
        Screenshot this error and send to support, then restart the application.
      </p>
    </body>
    </html>
    """
    webview.create_window(title, html=html, width=720, height=500)
    webview.start()


def main():
    if is_port_in_use(8000):
        log.info("Server already running on port 8000 - reusing it.")
    else:
        server_thread = threading.Thread(target=start_server, daemon=True)
        server_thread.start()

        log.info("Waiting for server to start...")
        if not wait_for_server(8000, timeout=30):
            error_detail = _server_error or "Server did not respond within 30 seconds."
            show_error_window("Failed to start internal server", error_detail)
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
