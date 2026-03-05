"""
Expense Tracker Pro — Desktop Launcher
Starts a local Flask server then opens the browser.
Works both as a plain Python script and as a PyInstaller .exe
"""
import sys
import os
import threading
import time
import webbrowser
import socket

# ── PyInstaller resource path helper ─────────────────────────────────────────
def resource_path(relative: str) -> str:
    """Return the absolute path to a bundled resource.
    When frozen by PyInstaller, files live in sys._MEIPASS.
    When running from source, they live next to this file.
    """
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative)

# Tell Flask where templates and static files are BEFORE importing app
os.environ["FLASK_TEMPLATE_FOLDER"] = resource_path("templates")
os.environ["FLASK_STATIC_FOLDER"]   = resource_path("static")

# ── Import the Flask app ──────────────────────────────────────────────────────
from app import app

# ── Pick a free port ──────────────────────────────────────────────────────────
def find_free_port(start: int = 5000) -> int:
    for port in range(start, start + 20):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
    return start  # fallback

PORT = find_free_port()
URL  = f"http://127.0.0.1:{PORT}"

# ── Open browser after server is up ──────────────────────────────────────────
def open_browser():
    time.sleep(1.6)
    webbrowser.open(URL)

# ── Entry point ───────────────────────────────────────────────────────────────
def main():
    print("\n" + "=" * 52)
    print("  💸  Expense Tracker Pro")
    print("=" * 52)
    print(f"  Local URL : {URL}")
    print(f"  Data dir  : ~/.expense_tracker_web/")
    print(f"  Stop      : close this window or Ctrl+C")
    print("=" * 52 + "\n")

    threading.Thread(target=open_browser, daemon=True).start()

    app.run(
        host="127.0.0.1",
        port=PORT,
        debug=False,
        use_reloader=False,   # must be False inside a frozen exe
        threaded=True,
    )

if __name__ == "__main__":
    main()
