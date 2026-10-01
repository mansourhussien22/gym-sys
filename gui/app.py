import sys
import time
import socket
import threading
import webview
from server import app


def is_port_in_use(port: int) -> bool:
    """Check if Flask server is already running."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0


def run_flask():
    """Start Flask background server for desktop GUI."""
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)


def launch_gui():
    # 1. Start server if not running
    if not is_port_in_use(5000):
        t = threading.Thread(target=run_flask, daemon=True)
        t.start()
        time.sleep(1.2)

    # 2. Open Desktop window inheriting directly from the web app
    window = webview.create_window(
        title="FitZone Pro — Elite Gym Platform",
        url="http://127.0.0.1:5000",
        width=1400,
        height=900,
        min_size=(1080, 720),
        background_color="#080b12",
        confirm_close=True
    )

    webview.start(private_mode=False)


if __name__ == "__main__":
    launch_gui()