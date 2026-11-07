import sys
import os
import io
import csv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lanscan.database import (
    init_db,
    record_scan_result,
    get_all_devices,
    update_device_details,
    delete_device,
    get_stats
)
from lanscan.scanner import get_network_interfaces, get_primary_interface
from lanscan.oui_data import lookup_vendor, guess_device_type

def test_all():
    print("1. Testing OUI lookup & Device type classification...")
    assert lookup_vendor("E8:9C:25:00:00:00") == "ASUSTek Computer"
    assert lookup_vendor("04:7C:16:00:00:00") == "MSI (Micro-Star)"
    assert lookup_vendor("50:8B:B9:00:00:00") == "Apple"
    
    dev_type = guess_device_type("ASUSTek Computer", "192.168.50.1", "192.168.50.1", [80])
    assert "Роутер" in dev_type
    
    dev_type = guess_device_type("MSI (Micro-Star)", "192.168.50.249", "192.168.50.1", [445])
    assert "Комп'ютер" in dev_type
    print("   [OK] OUI and device typing passed")

    print("2. Testing Network Interface discovery...")
    ifaces = get_network_interfaces()
    primary = get_primary_interface()
    assert len(ifaces) > 0, "No network interfaces found"
    assert primary is not None, "No primary interface detected"
    print(f"   [OK] Found {len(ifaces)} interfaces, primary is {primary['name']} ({primary['cidr']})")

    print("3. Testing Database CRUD and Scan Tracking...")
    # Add dummy device
    test_devices = [
        {
            "ip": "192.168.50.1",
            "mac": "E8:9C:25:68:84:30",
            "hostname": "router.asus.com",
            "vendor": "ASUSTek Computer",
            "device_type": "Роутер / Маршрутизатор",
            "latency": 1.2,
            "open_ports": [80, 443]
        },
        {
            "ip": "192.168.50.249",
            "mac": "04:7C:16:50:A6:2F",
            "hostname": "DESKTOP-MAIN",
            "vendor": "MSI (Micro-Star)",
            "device_type": "Комп'ютер / ПК",
            "latency": 0.2,
            "open_ports": [445]
        }
    ]
    record_scan_result(test_devices, "192.168.50.0/24", 2.5)
    
    devs = get_all_devices()
    assert len(devs) >= 2, f"Expected at least 2 devices, got {len(devs)}"
    stats = get_stats()
    assert stats["online"] >= 2, f"Expected online >= 2, got {stats['online']}"
    assert stats["computers"] >= 1, f"Expected computers >= 1, got {stats['computers']}"
    print(f"   [OK] DB tracking passed: Total={stats['total']}, Online={stats['online']}, Computers={stats['computers']}")

    print("4. Testing User Customizations (Rename, Notes, Favorites)...")
    update_device_details("04:7C:16:50:A6:2F", custom_name="Головний робочий ПК", notes="Підключений кабелем", is_favorite=1)
    devs = get_all_devices(search="Головний")
    assert len(devs) == 1, "Failed to search by custom name"
    assert devs[0]["custom_name"] == "Головний робочий ПК"
    assert devs[0]["is_favorite"] == 1
    print("   [OK] User customization (rename/notes/favorites) passed")

    print("\n==============================================")
    print("  ALL CORE BACKEND & DATABASE TESTS PASSED!   ")
    print("==============================================")

if __name__ == "__main__":
    test_all()
