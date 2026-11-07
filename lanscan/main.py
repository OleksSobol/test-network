"""
FastAPI application backend for LanScan IP Tracker.
Provides REST and SSE endpoints for network discovery, device tracking,
live scanning streaming, and statistics.
"""

import asyncio
import csv
import io
import json
import time
from typing import Optional, Dict, Any
from fastapi import FastAPI, Request, BackgroundTasks, Query, Response, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from lanscan.scanner import (
    scanner_instance,
    get_network_interfaces,
    get_primary_interface
)
from lanscan.database import (
    record_scan_result,
    get_all_devices,
    update_device_details,
    delete_device,
    get_stats
)

from contextlib import asynccontextmanager

# Auto-scan configuration and background worker
auto_scan_config = {
    "enabled": False,
    "interval_seconds": 300, # default 5 minutes
    "last_run": 0
}

_auto_scan_task = None

async def auto_scan_loop():
    while auto_scan_config["enabled"]:
        try:
            await asyncio.sleep(auto_scan_config["interval_seconds"])
            if not auto_scan_config["enabled"]:
                break
            if not scanner_instance.is_scanning:
                auto_scan_config["last_run"] = time.time()
                primary = get_primary_interface()
                subnet = primary["cidr"] if primary else "192.168.1.0/24"
                
                def bg_scan():
                    broadcast_scan_event({"type": "start", "subnet": subnet, "message": "Авто-сканування мережі..."})
                    try:
                        t0 = time.time()
                        found = scanner_instance.scan(subnet, broadcast_scan_event)
                        dur = time.time() - t0
                        record_scan_result(found, subnet, dur)
                        broadcast_scan_event({"type": "finished", "total_found": len(found), "duration": dur, "stats": get_stats()})
                    except Exception as e:
                        broadcast_scan_event({"type": "error", "error": str(e)})
                        
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, bg_scan)
        except asyncio.CancelledError:
            break
        except Exception:
            pass

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    global _auto_scan_task
    if _auto_scan_task and not _auto_scan_task.done():
        _auto_scan_task.cancel()

app = FastAPI(
    title="LanScan - Мережевий IP-Трекер",
    description="Веб-додаток для сканування та відстеження пристроїв у локальній мережі",
    version="1.0.0",
    lifespan=lifespan
)

# Mount static files and templates
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Real-time event queue for Server-Sent Events (SSE)
subscribers = set()

def broadcast_scan_event(event: Dict[str, Any]):
    """Pushes scan event to all active SSE listeners."""
    msg = f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
    dead = set()
    for q in subscribers:
        try:
            q.put_nowait(msg)
        except Exception:
            dead.add(q)
    for d in dead:
        subscribers.discard(d)

class DeviceUpdateRequest(BaseModel):
    custom_name: Optional[str] = None
    notes: Optional[str] = None
    is_favorite: Optional[bool] = None

class ScanRequest(BaseModel):
    subnet: Optional[str] = None

class AutoScanConfig(BaseModel):
    enabled: bool
    interval_seconds: int

@app.get("/", response_class=HTMLResponse)
async def index_page(request: Request):
    """Renders the main user interface."""
    primary = get_primary_interface()
    interfaces = get_network_interfaces()
    stats = get_stats()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "primary": primary,
        "interfaces": interfaces,
        "stats": stats
    })

@app.get("/api/network-info")
async def get_network_info():
    """Returns detected network adapters, active subnet and gateway."""
    primary = get_primary_interface()
    interfaces = get_network_interfaces()
    return {
        "primary": primary,
        "interfaces": interfaces
    }

@app.get("/api/stats")
async def get_system_stats():
    """Returns current device and scan statistics."""
    return get_stats()

@app.get("/api/devices")
async def list_devices(
    search: str = Query("", description="Search term"),
    status: str = Query("all", description="Filter by status: all, online, offline, computers, favorites")
):
    """Returns tracked devices with applied search and category filters."""
    devices = get_all_devices(search=search, filter_status=status)
    return {"devices": devices, "count": len(devices)}

@app.post("/api/scan")
async def trigger_scan(body: Optional[ScanRequest] = None, background_tasks: BackgroundTasks = BackgroundTasks()):
    """Triggers an asynchronous network scan."""
    if scanner_instance.is_scanning:
        return {
            "status": "already_scanning",
            "message": "Сканування вже триває",
            "progress": scanner_instance.current_progress,
            "scanned": scanner_instance.scanned_count,
            "total": scanner_instance.total_targets
        }

    subnet = body.subnet if body and body.subnet else None
    if not subnet:
        primary = get_primary_interface()
        subnet = primary["cidr"] if primary else "192.168.1.0/24"

    def scan_task():
        broadcast_scan_event({"type": "start", "subnet": subnet, "message": "Початок сканування..."})
        try:
            t0 = time.time()
            found = scanner_instance.scan(
                subnet_cidr=subnet,
                progress_callback=broadcast_scan_event
            )
            duration = time.time() - t0
            record_scan_result(found, subnet, duration)
            broadcast_scan_event({
                "type": "finished",
                "total_found": len(found),
                "duration": round(duration, 2),
                "stats": get_stats()
            })
        except Exception as e:
            broadcast_scan_event({"type": "error", "error": str(e)})

    # Run in thread pool so it does not block the async event loop
    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, scan_task)

    return {"status": "started", "subnet": subnet, "message": "Сканування запущено"}

@app.get("/api/scan/status")
async def get_scan_status():
    """Returns current scanner state for polling clients."""
    return {
        "is_scanning": scanner_instance.is_scanning,
        "progress": scanner_instance.current_progress,
        "scanned": scanner_instance.scanned_count,
        "total": scanner_instance.total_targets,
        "found_count": len(scanner_instance.found_devices)
    }

@app.get("/api/scan/stream")
async def scan_events_stream():
    """Server-Sent Events endpoint streaming real-time scan progress."""
    queue = asyncio.Queue()
    subscribers.add(queue)

    async def event_generator():
        try:
            # Send initial connection ping
            yield "event: ping\ndata: connected\n\n"
            while True:
                msg = await queue.get()
                yield msg
        except asyncio.CancelledError:
            subscribers.discard(queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@app.put("/api/devices/{mac}")
async def update_device(mac: str, data: DeviceUpdateRequest):
    """Updates user-customized name, notes, or favorite status."""
    update_device_details(
        mac=mac,
        custom_name=data.custom_name,
        notes=data.notes,
        is_favorite=data.is_favorite
    )
    return {"status": "success", "message": "Дані пристрою оновлено"}

@app.delete("/api/devices/{mac}")
async def remove_device(mac: str):
    """Deletes a device from tracking history."""
    delete_device(mac)
    return {"status": "success", "message": "Пристрій видалено"}

@app.get("/api/export/csv")
async def export_csv():
    """Exports all tracked devices to a downloadable CSV file."""
    devices = get_all_devices()
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(["IP-адреса", "MAC-адреса", "Назва комп'ютера", "Користувацька назва", "Виробник", "Тип пристрою", "Статус", "Затримка (мс)", "Вперше в мережі", "Останній раз в мережі", "Примітки"])
    
    for d in devices:
        writer.writerow([
            d.get("ip", ""),
            d.get("mac", ""),
            d.get("hostname", ""),
            d.get("custom_name", ""),
            d.get("vendor", ""),
            d.get("device_type", ""),
            "Онлайн" if d.get("is_online") else "Офлайн",
            d.get("last_latency", ""),
            d.get("first_seen", ""),
            d.get("last_seen", ""),
            d.get("notes", "")
        ])
        
    output.seek(0)
    response = Response(content=output.getvalue(), media_type="text/csv; charset=utf-8")
    response.headers["Content-Disposition"] = "attachment; filename=lanscan_devices.csv"
    return response

@app.get("/api/export/json")
async def export_json():
    """Exports all tracked devices as JSON."""
    devices = get_all_devices()
    return JSONResponse(
        content={"devices": devices, "exported_at": time.strftime("%Y-%m-%d %H:%M:%S")},
        headers={"Content-Disposition": "attachment; filename=lanscan_devices.json"}
    )

@app.post("/api/auto-scan")
async def set_auto_scan(config: AutoScanConfig):
    """Configures periodic background auto-scanning."""
    global _auto_scan_task
    auto_scan_config["enabled"] = config.enabled
    auto_scan_config["interval_seconds"] = max(30, config.interval_seconds)

    if _auto_scan_task and not _auto_scan_task.done():
        _auto_scan_task.cancel()

    if auto_scan_config["enabled"]:
        _auto_scan_task = asyncio.create_task(auto_scan_loop())

    return {
        "status": "success",
        "enabled": auto_scan_config["enabled"],
        "interval_seconds": auto_scan_config["interval_seconds"]
    }

@app.get("/api/auto-scan")
async def get_auto_scan_status():
    """Returns current auto-scan settings."""
    return auto_scan_config
