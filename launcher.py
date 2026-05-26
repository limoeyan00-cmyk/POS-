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
    from PyQt6.QtWidgets import QApplication, QMessageBox
    app = QApplication.instance() or QApplication(sys.argv)
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Icon.Critical)
    msg.setText("KastomPOS - Startup Error")
    msg.setInformativeText(title)
    msg.setDetailedText(message)
    msg.setWindowTitle("Startup Error")
    msg.exec()


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

    from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    from PyQt6.QtCore import QUrl

    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("KastomPOS - ERP & Point of Sale")
            self.resize(1280, 800)
            self.setMinimumSize(1024, 768)

            self.browser = QWebEngineView()
            self.browser.setUrl(QUrl("http://127.0.0.1:8000"))
            self.setCentralWidget(self.browser)

        def closeEvent(self, event):
            reply = QMessageBox.question(
                self,
                "Exit KastomPOS",
                "Are you sure you want to exit KastomPOS?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                event.accept()
            else:
                event.ignore()

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
