"""
OUI (Organizationally Unique Identifier) Database for MAC address vendor lookup.
Includes top computer, router, mobile, IoT, and printer manufacturers,
plus detection for locally administered (randomized) MAC addresses.
"""

OUI_DATABASE = {
    # ASUS
    "E8:9C:25": "ASUSTek Computer",
    "04:D9:F5": "ASUSTek Computer",
    "10:7B:44": "ASUSTek Computer",
    "1C:87:2C": "ASUSTek Computer",
    "2C:4D:54": "ASUSTek Computer",
    "30:5A:3A": "ASUSTek Computer",
    "38:2C:4A": "ASUSTek Computer",
    "40:16:7E": "ASUSTek Computer",
    "50:46:5D": "ASUSTek Computer",
    "60:45:CB": "ASUSTek Computer",
    "70:4D:7B": "ASUSTek Computer",
    "AC:9E:17": "ASUSTek Computer",
    "BC:EE:7B": "ASUSTek Computer",
    "F0:79:59": "ASUSTek Computer",

    # MSI (Micro-Star)
    "04:7C:16": "MSI (Micro-Star)",
    "00:19:DB": "MSI (Micro-Star)",
    "00:21:85": "MSI (Micro-Star)",
    "00:24:21": "MSI (Micro-Star)",
    "00:26:18": "MSI (Micro-Star)",
    "40:8D:5C": "MSI (Micro-Star)",
    "4C:CC:6A": "MSI (Micro-Star)",
    "D8:5E:D3": "MSI (Micro-Star)",
    "DB:5E:D3": "MSI (Micro-Star)",

    # Gigabyte
    "00:23:24": "Gigabyte Technology",
    "00:24:1D": "Gigabyte Technology",
    "10:6F:3F": "Gigabyte Technology",
    "14:D6:4D": "Gigabyte Technology",
    "18:C0:4D": "Gigabyte Technology",
    "24:4B:FE": "Gigabyte Technology",
    "40:8D:5C": "Gigabyte Technology",
    "90:2B:34": "Gigabyte Technology",
    "E0:D5:5E": "Gigabyte Technology",

    # Intel
    "20:1F:3B": "Intel",
    "00:13:02": "Intel",
    "00:13:E8": "Intel",
    "00:15:00": "Intel",
    "00:1B:21": "Intel",
    "00:1E:67": "Intel",
    "00:21:5C": "Intel",
    "34:13:E8": "Intel",
    "3C:F8:62": "Intel",
    "48:4D:7E": "Intel",
    "48:F1:7F": "Intel",
    "5C:80:B6": "Intel",
    "68:05:CA": "Intel",
    "68:EC:C5": "Intel",
    "80:86:F2": "Intel",
    "8C:85:90": "Intel",
    "94:E6:F7": "Intel",
    "A4:4C:C8": "Intel",
    "C8:F7:50": "Intel",
    "DC:53:60": "Intel",
    "E8:B1:FC": "Intel",
    "F8:75:A4": "Intel",

    # Apple
    "50:8B:B9": "Apple",
    "58:D8:12": "Apple",
    "D4:A6:51": "Apple",
    "00:03:93": "Apple",
    "00:05:02": "Apple",
    "00:0A:27": "Apple",
    "00:0A:95": "Apple",
    "00:10:FA": "Apple",
    "00:14:51": "Apple",
    "00:17:F2": "Apple",
    "00:19:E3": "Apple",
    "00:1B:63": "Apple",
    "00:1C:B3": "Apple",
    "00:1E:52": "Apple",
    "00:1E:C2": "Apple",
    "00:21:E9": "Apple",
    "00:22:41": "Apple",
    "00:23:12": "Apple",
    "00:23:32": "Apple",
    "00:23:6C": "Apple",
    "00:24:36": "Apple",
    "00:25:00": "Apple",
    "00:25:4B": "Apple",
    "00:25:BC": "Apple",
    "00:26:08": "Apple",
    "00:26:4A": "Apple",
    "00:26:B0": "Apple",
    "00:3E:E1": "Apple",
    "04:0C:CE": "Apple",
    "04:15:52": "Apple",
    "04:1E:64": "Apple",
    "04:48:9A": "Apple",
    "04:54:53": "Apple",
    "04:DB:56": "Apple",
    "04:E5:36": "Apple",
    "08:66:98": "Apple",
    "0C:74:C2": "Apple",
    "10:93:E9": "Apple",
    "14:10:9F": "Apple",
    "14:20:5E": "Apple",
    "14:7D:C5": "Apple",
    "14:98:77": "Apple",
    "14:99:E2": "Apple",
    "18:AF:61": "Apple",
    "18:EE:69": "Apple",
    "1C:5C:F2": "Apple",
    "20:76:8F": "Apple",
    "24:F6:77": "Apple",
    "28:0B:5C": "Apple",
    "28:6A:BA": "Apple",
    "28:CF:E9": "Apple",
    "28:ED:6A": "Apple",
    "2C:F0:EE": "Apple",
    "30:07:4D": "Apple",
    "34:08:BC": "Apple",
    "38:89:2C": "Apple",
    "3C:07:54": "Apple",
    "40:6C:8F": "Apple",
    "40:98:AD": "Apple",
    "48:43:7C": "Apple",
    "48:A1:95": "Apple",
    "4C:32:75": "Apple",
    "54:E4:3A": "Apple",
    "60:03:08": "Apple",
    "64:B0:A6": "Apple",
    "68:96:7B": "Apple",
    "70:DE:E2": "Apple",
    "74:E1:B6": "Apple",
    "78:7B:8A": "Apple",
    "7C:04:D0": "Apple",
    "80:BE:05": "Apple",
    "84:38:35": "Apple",
    "88:66:5A": "Apple",
    "8C:85:90": "Apple",
    "90:9C:4A": "Apple",
    "94:94:26": "Apple",
    "98:01:A7": "Apple",
    "9C:20:7B": "Apple",
    "A0:99:9B": "Apple",
    "A4:83:E7": "Apple",
    "A8:66:7F": "Apple",
    "AC:BC:32": "Apple",
    "B0:34:95": "Apple",
    "B4:F0:AB": "Apple",
    "B8:78:26": "Apple",
    "BC:52:B7": "Apple",
    "C0:9A:D0": "Apple",
    "C4:2C:03": "Apple",
    "C8:69:CD": "Apple",
    "CC:29:F0": "Apple",
    "D0:81:7A": "Apple",
    "D8:00:4D": "Apple",
    "DC:2B:61": "Apple",
    "E0:AC:CB": "Apple",
    "E4:8B:7F": "Apple",
    "E8:06:88": "Apple",
    "F0:18:98": "Apple",
    "F4:0F:24": "Apple",
    "F8:27:93": "Apple",
    "FC:FC:48": "Apple",

    # Samsung
    "78:8C:B5": "Samsung Electronics",
    "D4:F5:47": "Samsung Electronics",
    "00:07:AB": "Samsung Electronics",
    "00:12:47": "Samsung Electronics",
    "00:15:99": "Samsung Electronics",
    "00:17:D5": "Samsung Electronics",
    "00:1A:8A": "Samsung Electronics",
    "00:1D:25": "Samsung Electronics",
    "00:21:4C": "Samsung Electronics",
    "00:23:D7": "Samsung Electronics",
    "08:37:3D": "Samsung Electronics",
    "14:49:E0": "Samsung Electronics",
    "18:3B:D2": "Samsung Electronics",
    "1C:66:AA": "Samsung Electronics",
    "20:D5:BF": "Samsung Electronics",
    "24:F5:AA": "Samsung Electronics",
    "28:18:78": "Samsung Electronics",
    "30:07:4D": "Samsung Electronics",
    "34:BE:00": "Samsung Electronics",
    "38:01:46": "Samsung Electronics",
    "3C:62:00": "Samsung Electronics",
    "40:0E:85": "Samsung Electronics",
    "44:91:60": "Samsung Electronics",
    "48:44:F7": "Samsung Electronics",
    "4C:BC:A5": "Samsung Electronics",
    "50:01:D9": "Samsung Electronics",
    "54:92:BE": "Samsung Electronics",
    "5C:A3:9D": "Samsung Electronics",
    "60:6C:66": "Samsung Electronics",
    "68:EB:AE": "Samsung Electronics",
    "70:2C:1F": "Samsung Electronics",
    "74:45:CE": "Samsung Electronics",
    "7C:F8:09": "Samsung Electronics",
    "84:25:DB": "Samsung Electronics",
    "88:36:5F": "Samsung Electronics",
    "8C:77:12": "Samsung Electronics",
    "90:18:7C": "Samsung Electronics",
    "94:35:0A": "Samsung Electronics",
    "98:0D:2E": "Samsung Electronics",
    "A0:82:1F": "Samsung Electronics",
    "A8:7C:01": "Samsung Electronics",
    "AC:5F:3E": "Samsung Electronics",
    "B0:C4:E7": "Samsung Electronics",
    "B4:07:F9": "Samsung Electronics",
    "B8:57:D8": "Samsung Electronics",
    "BC:44:86": "Samsung Electronics",
    "C0:BD:D1": "Samsung Electronics",
    "C4:73:1E": "Samsung Electronics",
    "C8:19:F7": "Samsung Electronics",
    "CC:07:AB": "Samsung Electronics",
    "D0:17:6A": "Samsung Electronics",
    "E4:7C:F9": "Samsung Electronics",
    "E8:50:8B": "Samsung Electronics",
    "F0:EE:10": "Samsung Electronics",

    # Xiaomi
    "D0:3F:27": "Xiaomi",
    "2C:AA:8E": "Xiaomi",
    "DC:62:79": "Xiaomi",
    "00:9E:C8": "Xiaomi",
    "04:CF:8C": "Xiaomi",
    "0C:98:38": "Xiaomi",
    "10:2A:B3": "Xiaomi",
    "14:F6:5A": "Xiaomi",
    "18:59:36": "Xiaomi",
    "1C:CD:E5": "Xiaomi",
    "20:82:C0": "Xiaomi",
    "24:69:A5": "Xiaomi",
    "28:6C:07": "Xiaomi",
    "34:80:0D": "Xiaomi",
    "38:A4:ED": "Xiaomi",
    "3C:BD:3E": "Xiaomi",
    "40:31:3C": "Xiaomi",
    "44:23:7C": "Xiaomi",
    "50:64:2B": "Xiaomi",
    "54:48:E6": "Xiaomi",
    "58:44:98": "Xiaomi",
    "5C:02:14": "Xiaomi",
    "64:09:80": "Xiaomi",
    "68:DF:DD": "Xiaomi",
    "74:23:44": "Xiaomi",
    "78:02:F8": "Xiaomi",
    "7C:1C:4E": "Xiaomi",
    "88:C3:97": "Xiaomi",
    "8C:BE:BE": "Xiaomi",
    "94:87:E0": "Xiaomi",
    "98:FA:E3": "Xiaomi",
    "9C:2E:A1": "Xiaomi",
    "A4:44:D1": "Xiaomi",
    "A8:9C:ED": "Xiaomi",
    "B0:E2:35": "Xiaomi",
    "C4:0B:D6": "Xiaomi",
    "D4:97:0B": "Xiaomi",
    "E4:46:DA": "Xiaomi",
    "E8:AB:FA": "Xiaomi",
    "F4:F5:DB": "Xiaomi",

    # Tuya Smart & IoT
    "18:69:D8": "Tuya Smart IoT",
    "10:D5:61": "Tuya Smart IoT",
    "24:DF:A7": "Tuya Smart IoT",
    "50:02:91": "Tuya Smart IoT",
    "70:89:76": "Tuya Smart IoT",
    "7C:F6:66": "Tuya Smart IoT",
    "84:F3:EB": "Tuya Smart IoT",
    "A0:92:08": "Tuya Smart IoT",
    "B4:E6:2D": "Tuya Smart IoT",
    "D4:D2:D6": "Tuya Smart IoT",

    # Espressif (ESP32, ESP8266 - smart home, plugs, sensors)
    "D8:8C:79": "Espressif (ESP32/IoT)",
    "24:0A:C4": "Espressif (ESP32/IoT)",
    "24:6F:28": "Espressif (ESP32/IoT)",
    "24:B2:DE": "Espressif (ESP32/IoT)",
    "2C:3A:E8": "Espressif (ESP32/IoT)",
    "30:AE:A4": "Espressif (ESP32/IoT)",
    "34:85:18": "Espressif (ESP32/IoT)",
    "3C:61:05": "Espressif (ESP32/IoT)",
    "3C:71:BF": "Espressif (ESP32/IoT)",
    "40:22:D8": "Espressif (ESP32/IoT)",
    "48:3F:DA": "Espressif (ESP32/IoT)",
    "48:55:19": "Espressif (ESP32/IoT)",
    "54:43:B2": "Espressif (ESP32/IoT)",
    "5C:CF:7F": "Espressif (ESP32/IoT)",
    "60:01:94": "Espressif (ESP32/IoT)",
    "68:C6:3A": "Espressif (ESP32/IoT)",
    "70:03:9F": "Espressif (ESP32/IoT)",
    "7C:87:CE": "Espressif (ESP32/IoT)",
    "80:7D:3A": "Espressif (ESP32/IoT)",
    "84:0D:8E": "Espressif (ESP32/IoT)",
    "84:CC:A8": "Espressif (ESP32/IoT)",
    "84:F3:EB": "Espressif (ESP32/IoT)",
    "90:97:D5": "Espressif (ESP32/IoT)",
    "94:B5:55": "Espressif (ESP32/IoT)",
    "A0:20:A6": "Espressif (ESP32/IoT)",
    "A4:7B:9D": "Espressif (ESP32/IoT)",
    "A4:CF:12": "Espressif (ESP32/IoT)",
    "AC:67:B2": "Espressif (ESP32/IoT)",
    "B4:E6:2D": "Espressif (ESP32/IoT)",
    "BC:DD:C2": "Espressif (ESP32/IoT)",
    "C4:4F:33": "Espressif (ESP32/IoT)",
    "C8:2B:96": "Espressif (ESP32/IoT)",
    "CC:50:E3": "Espressif (ESP32/IoT)",
    "D8:A0:1D": "Espressif (ESP32/IoT)",
    "DC:4F:22": "Espressif (ESP32/IoT)",
    "E0:98:06": "Espressif (ESP32/IoT)",
    "E8:DB:84": "Espressif (ESP32/IoT)",

    # TP-Link
    "0C:95:05": "TP-Link",
    "00:25:86": "TP-Link",
    "14:CC:20": "TP-Link",
    "18:A6:F7": "TP-Link",
    "1C:3B:F3": "TP-Link",
    "20:F4:1B": "TP-Link",
    "30:B5:C2": "TP-Link",
    "34:E8:94": "TP-Link",
    "50:C7:BF": "TP-Link",
    "54:AF:97": "TP-Link",
    "60:A4:4C": "TP-Link",
    "64:66:B3": "TP-Link",
    "64:70:02": "TP-Link",
    "70:4F:57": "TP-Link",
    "74:DA:38": "TP-Link",
    "90:F6:52": "TP-Link",
    "98:48:27": "TP-Link",
    "A0:F3:C1": "TP-Link",
    "AC:84:C6": "TP-Link",
    "C0:25:E9": "TP-Link",
    "C0:4A:00": "TP-Link",
    "D8:07:B6": "TP-Link",
    "E4:C3:2A": "TP-Link",
    "E8:48:B8": "TP-Link",
    "EC:08:6B": "TP-Link",
    "F4:EC:38": "TP-Link",

    # MikroTik
    "00:0C:42": "MikroTik",
    "08:55:31": "MikroTik",
    "18:FD:74": "MikroTik",
    "2C:C8:1B": "MikroTik",
    "48:8F:5A": "MikroTik",
    "4C:5E:0C": "MikroTik",
    "64:D1:54": "MikroTik",
    "74:4D:28": "MikroTik",
    "B8:69:F4": "MikroTik",
    "C4:AD:34": "MikroTik",
    "CC:2D:E0": "MikroTik",
    "D4:01:C3": "MikroTik",
    "E4:8D:8C": "MikroTik",

    # Ubiquiti
    "00:15:6D": "Ubiquiti Networks",
    "00:27:22": "Ubiquiti Networks",
    "24:A4:3C": "Ubiquiti Networks",
    "44:D9:E7": "Ubiquiti Networks",
    "68:D7:9A": "Ubiquiti Networks",
    "70:A7:41": "Ubiquiti Networks",
    "78:8A:20": "Ubiquiti Networks",
    "80:2A:A8": "Ubiquiti Networks",
    "AC:8B:A9": "Ubiquiti Networks",
    "B4:FB:E4": "Ubiquiti Networks",
    "DC:9F:DB": "Ubiquiti Networks",
    "E0:63:DA": "Ubiquiti Networks",
    "F0:9F:C2": "Ubiquiti Networks",

    # Realtek
    "00:E0:4C": "Realtek Semiconductor",
    "52:54:00": "Realtek (QEMU/Virtual)",

    # Raspberry Pi
    "B8:27:EB": "Raspberry Pi Foundation",
    "DC:A6:32": "Raspberry Pi Foundation",
    "E4:5F:01": "Raspberry Pi Foundation",
    "28:CD:C1": "Raspberry Pi Foundation",

    # Dell
    "00:14:22": "Dell",
    "00:1E:4F": "Dell",
    "18:03:73": "Dell",
    "24:B6:FD": "Dell",
    "34:17:EB": "Dell",
    "74:86:7A": "Dell",
    "B8:2A:72": "Dell",
    "BC:30:5B": "Dell",
    "D4:BE:D9": "Dell",
    "F8:DB:88": "Dell",

    # HP
    "00:1E:0B": "HP",
    "00:25:B3": "HP",
    "10:60:4B": "HP",
    "18:60:24": "HP",
    "2C:59:E5": "HP",
    "3C:D9:2B": "HP",
    "5C:B9:01": "HP",
    "70:5A:0F": "HP",
    "84:34:97": "HP",
    "9C:8E:99": "HP",
    "A0:D3:C1": "HP",
    "C8:D3:FF": "HP",

    # Lenovo
    "00:59:07": "Lenovo",
    "20:76:93": "Lenovo",
    "34:13:E8": "Lenovo",
    "54:EE:75": "Lenovo",
    "70:72:0D": "Lenovo",
    "80:2B:F9": "Lenovo",
    "98:FA:9B": "Lenovo",
    "A4:BB:6D": "Lenovo",
    "C8:5B:76": "Lenovo",
    "E8:6A:64": "Lenovo",

    # Microsoft
    "00:12:5A": "Microsoft",
    "00:15:5D": "Microsoft (Hyper-V)",
    "28:18:78": "Microsoft Surface",
    "48:E9:F1": "Microsoft",
    "7C:ED:8D": "Microsoft Xbox",
    "98:5F:D3": "Microsoft",
    "DC:98:40": "Microsoft",

    # Sony (PlayStation / TVs)
    "00:04:1F": "Sony Interactive / PlayStation",
    "00:13:15": "Sony Interactive / PlayStation",
    "00:1D:0D": "Sony Interactive / PlayStation",
    "00:24:8D": "Sony Interactive / PlayStation",
    "70:9E:29": "Sony Interactive / PlayStation",
    "A8:E2:C1": "Sony Interactive / PlayStation",
    "FC:0F:E6": "Sony Interactive / PlayStation",

    # LG Electronics (Smart TV / Appliances)
    "00:1C:62": "LG Electronics",
    "10:F9:6F": "LG Electronics",
    "20:3D:66": "LG Electronics",
    "34:82:C5": "LG Electronics",
    "58:A2:B5": "LG Electronics",
    "64:99:5D": "LG Electronics",
    "A8:23:FE": "LG Electronics",
    "CC:2D:83": "LG Electronics",
    "E8:5B:5B": "LG Electronics",

    # Synology / QNAP (NAS)
    "00:11:32": "Synology NAS",
    "00:08:9B": "QNAP NAS",
    "24:5E:BE": "QNAP NAS",

    # Printers (Canon, Epson, Brother)
    "00:00:85": "Canon",
    "00:1E:8F": "Canon",
    "18:0C:AC": "Canon",
    "00:00:48": "Epson",
    "00:26:AB": "Epson",
    "44:D2:44": "Epson",
    "00:80:77": "Brother",
    "30:05:5C": "Brother",
    "40:49:0F": "Brother",
}

def is_randomized_mac(mac: str) -> bool:
    """Checks if MAC has the locally administered bit set (often random iOS/Android Wi-Fi address)."""
    try:
        parts = mac.replace('-', ':').split(':')
        first_byte = int(parts[0], 16)
        return bool(first_byte & 0x02)
    except Exception:
        return False

def lookup_vendor(mac: str) -> str:
    """Returns vendor name or device hint based on MAC address."""
    if not mac:
        return "Невідомо"
    clean_mac = mac.upper().replace('-', ':')
    prefix = ':'.join(clean_mac.split(':')[:3])
    
    if prefix in OUI_DATABASE:
        return OUI_DATABASE[prefix]
        
    if is_randomized_mac(clean_mac):
        return "Приватна MAC (Смартфон / iOS / Android)"
        
    return "Невідомий виробник"

def guess_device_type(vendor: str, ip: str, gateway_ip: str, open_ports: list) -> str:
    """Infers category of device for clear UI badges."""
    v_lower = vendor.lower()
    
    if ip == gateway_ip or "asustek" in v_lower and ip.endswith(".1"):
        return "Роутер / Маршрутизатор"
        
    if any(p in open_ports for p in [445, 139, 3389]) or any(k in v_lower for k in ["msi", "micro-star", "gigabyte", "intel", "dell", "hp", "lenovo", "microsoft"]):
        return "Комп'ютер / ПК"
        
    if any(k in v_lower for k in ["tuya", "espressif", "esp32", "iot", "smart"]):
        return "Розумний пристрій (IoT)"
        
    if any(k in v_lower for k in ["apple", "samsung", "xiaomi", "смартфон", "ios", "android"]):
        return "Мобільний / Смартфон"
        
    if any(k in v_lower for k in ["playstation", "xbox", "sony", "lg electronics", "smart tv"]):
        return "Медіа / ТБ / Консоль"
        
    if any(p in open_ports for p in [9100, 515, 631]) or any(k in v_lower for k in ["canon", "epson", "brother"]):
        return "Принтер"
        
    if "synology" in v_lower or "qnap" in v_lower:
        return "Мережеве сховище (NAS)"
        
    if "raspberry" in v_lower:
        return "Мікрокомп'ютер"
        
    if "router" in v_lower or "mikrotik" in v_lower or "tp-link" in v_lower or "ubiquiti" in v_lower:
        return "Мережеве обладнання"
        
    return "Комп'ютер / Пристрій"
