"""
Simple single-command launcher for LanScan.
Runs the FastAPI server and automatically opens the user's default browser.
"""

import webbrowser
import threading
import time
import uvicorn

def open_browser():
    time.sleep(1.2)
    webbrowser.open("http://localhost:8000")

if __name__ == "__main__":
    print("=" * 60)
    print("  LanScan - Мережевий Сканер & IP-Трекер")
    print("  Веб-сайт доступний за адресою: http://localhost:8000")
    print("=" * 60)
    threading.Thread(target=open_browser, daemon=True).start()
    uvicorn.run("lanscan.main:app", host="0.0.0.0", port=8000, reload=False)
