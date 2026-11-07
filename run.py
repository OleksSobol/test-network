"""
Simple single-command launcher for LanScan.
Runs the FastAPI server and automatically opens the user's default browser.
"""

import os
import webbrowser
import threading
import time
import uvicorn

port = int(os.environ.get("PORT", 8050))

def open_browser():
    time.sleep(1.2)
    webbrowser.open(f"http://localhost:{port}")

if __name__ == "__main__":
    print("=" * 60)
    print("  LanScan - Мережевий Сканер & IP-Трекер")
    print(f"  Веб-сайт доступний за адресою: http://localhost:{port}")
    print("=" * 60)
    threading.Thread(target=open_browser, daemon=True).start()
    uvicorn.run("lanscan.main:app", host="0.0.0.0", port=port, reload=False)
