"""
High-speed network scanner for local subnets.
Utilizes Windows SendARP API for rapid, firewall-resilient device detection,
coupled with hostname resolution, port probing, and vendor identification.
"""

import ctypes
import socket
import struct
import ipaddress
import time
import sys
import os
import subprocess
import psutil
from typing import List, Dict, Any, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed

from lanscan.oui_data import lookup_vendor, guess_device_type

COMMON_PORTS = [80, 443, 445, 139, 22, 8080, 9100]

def is_windows() -> bool:
    return sys.platform.startswith("win")

def send_arp_windows(ip_str: str) -> Optional[str]:
    """Sends hardware ARP request using iphlpapi.dll on Windows."""
    try:
        dest_ip = struct.unpack('<I', socket.inet_aton(ip_str))[0]
        mac_addr = (ctypes.c_byte * 6)()
        mac_len = ctypes.c_ulong(6)
        res = ctypes.windll.iphlpapi.SendARP(dest_ip, 0, ctypes.byref(mac_addr), ctypes.byref(mac_len))
        if res == 0:
            return ':'.join(f'{b & 0xff:02X}' for b in mac_addr)
    except Exception:
        pass
    return None

def get_linux_arp_mac(ip_str: str) -> Optional[str]:
    """Reads Linux kernel /proc/net/arp table for resolved MAC address."""
    try:
        if os.path.exists("/proc/net/arp"):
            with open("/proc/net/arp", "r") as f:
                for line in f.readlines()[1:]:
                    parts = line.split()
                    if len(parts) >= 4 and parts[0] == ip_str:
                        mac = parts[3].upper()
                        if mac != "00:00:00:00:00:00" and parts[2] != "0x0":
                            return mac
    except Exception:
        pass
    return None

def ping_host_linux(ip_str: str) -> bool:
    """Sends a fast ICMP ping to trigger Linux kernel ARP resolution."""
    try:
        res = subprocess.run(
            ["ping", "-c", "1", "-W", "1", ip_str],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=1.2
        )
        return res.returncode == 0
    except Exception:
        return False

def check_tcp_port(ip_str: str, port: int, timeout: float = 0.25) -> bool:
    """Tests if a specific TCP port is open."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            return s.connect_ex((ip_str, port)) == 0
    except Exception:
        return False

def resolve_hostname(ip_str: str, timeout: float = 0.4) -> str:
    """Attempts quick reverse DNS lookup for hostname."""
    try:
        # Set temporary default socket timeout
        old_timeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(timeout)
        hostname = socket.gethostbyaddr(ip_str)[0]
        socket.setdefaulttimeout(old_timeout)
        return hostname
    except Exception:
        return ""

def probe_open_ports(ip_str: str) -> List[int]:
    """Probes a selection of common ports to identify device function."""
    open_p = []
    for port in COMMON_PORTS:
        if check_tcp_port(ip_str, port, timeout=0.15):
            open_p.append(port)
    return open_p

def get_network_interfaces() -> List[Dict[str, Any]]:
    """Discovers all active network interfaces and candidate subnets."""
    interfaces = []
    stats = psutil.net_if_stats()
    addrs = psutil.net_if_addrs()

    for iface_name, addr_list in addrs.items():
        # Check if interface is UP
        if iface_name in stats and not stats[iface_name].isup:
            continue
            
        for a in addr_list:
            if a.family == socket.AF_INET:
                ip = a.address
                netmask = a.netmask or "255.255.255.0"
                # Filter out loopback, auto-ip (169.254), or docker virtuals
                if ip.startswith("127.") or ip.startswith("169.254."):
                    continue
                try:
                    net = ipaddress.IPv4Network(f"{ip}/{netmask}", strict=False)
                    # Calculate estimated gateway (usually .1)
                    gateway = str(list(net.hosts())[0]) if len(list(net.hosts())) > 0 else ""
                    
                    interfaces.append({
                        "name": iface_name,
                        "ip": ip,
                        "netmask": netmask,
                        "cidr": str(net),
                        "gateway": gateway,
                        "total_hosts": net.num_addresses - 2 if net.num_addresses > 2 else 1,
                        "is_primary": not iface_name.lower().startswith("tailscale") and not iface_name.lower().startswith("wg")
                    })
                except Exception:
                    continue

    # If inside Docker or DEFAULT_SUBNET is provided, ensure home subnets are available
    custom_sub = os.environ.get("DEFAULT_SUBNET")
    if custom_sub:
        try:
            c_net = ipaddress.IPv4Network(custom_sub, strict=False)
            interfaces.insert(0, {
                "name": "Головна мережа (LAN)",
                "ip": str(list(c_net.hosts())[0]),
                "netmask": str(c_net.netmask),
                "cidr": str(c_net),
                "gateway": str(list(c_net.hosts())[0]),
                "total_hosts": c_net.num_addresses - 2,
                "is_primary": True
            })
        except Exception:
            pass
    elif os.path.exists("/.dockerenv") or any(i.get("ip", "").startswith("172.") for i in interfaces):
        # Add typical home network subnets as convenient options inside Docker
        for fallback_cidr, fallback_label in [
            ("192.168.1.0/24", "Домашня мережа (192.168.1.0/24)"),
            ("192.168.0.0/24", "Домашня мережа (192.168.0.0/24)"),
            ("192.168.50.0/24", "Домашня мережа (192.168.50.0/24)")
        ]:
            if not any(i["cidr"] == fallback_cidr for i in interfaces):
                interfaces.append({
                    "name": fallback_label,
                    "ip": fallback_cidr.replace(".0/24", ".1"),
                    "netmask": "255.255.255.0",
                    "cidr": fallback_cidr,
                    "gateway": fallback_cidr.replace(".0/24", ".1"),
                    "total_hosts": 254,
                    "is_primary": False
                })

    # Sort primary interfaces first
    interfaces.sort(key=lambda x: (not x["is_primary"], x["name"]))
    return interfaces

def get_primary_interface() -> Optional[Dict[str, Any]]:
    """Returns the primary active LAN interface or a fallback default."""
    ifaces = get_network_interfaces()
    for iface in ifaces:
        if iface.get("is_primary"):
            return iface
    return ifaces[0] if ifaces else None

class NetworkScanner:
    def __init__(self):
        self.is_scanning = False
        self.current_progress = 0
        self.total_targets = 0
        self.scanned_count = 0
        self.found_devices: List[Dict[str, Any]] = []
        self.start_time: float = 0.0

    def scan(self, subnet_cidr: str, progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None) -> List[Dict[str, Any]]:
        """
        Scans all hosts in the specified CIDR subnet.
        Reports real-time progress via progress_callback.
        """
        if self.is_scanning:
            return self.found_devices

        self.is_scanning = True
        self.scanned_count = 0
        self.found_devices = []
        self.start_time = time.time()

        try:
            net = ipaddress.IPv4Network(subnet_cidr, strict=False)
            hosts = list(net.hosts())
            self.total_targets = len(hosts)
            gateway_ip = str(hosts[0]) if hosts else ""
        except Exception as e:
            self.is_scanning = False
            raise ValueError(f"Невірний формат підмережі '{subnet_cidr}': {str(e)}")

        def scan_single_host(ip_obj):
            ip_str = str(ip_obj)
            t_start = time.perf_counter()
            mac = None

            if is_windows():
                mac = send_arp_windows(ip_str)
            else:
                # On Linux / Docker: trigger kernel ARP resolution
                alive = ping_host_linux(ip_str)
                mac = get_linux_arp_mac(ip_str)
                if alive and not mac:
                    mac = "Активний (ICMP)"

            # Fallback TCP ping if ARP did not respond yet
            if not mac:
                for p in [445, 80, 443, 22, 139, 8080]:
                    if check_tcp_port(ip_str, p, timeout=0.18):
                        if not is_windows():
                            mac = get_linux_arp_mac(ip_str)
                        if not mac:
                            mac = "Невідома (TCP)"
                        break

            latency = round((time.perf_counter() - t_start) * 1000, 1)
            
            if mac:
                vendor = lookup_vendor(mac) if mac != "Невідома (TCP)" else "Мережевий пристрій"
                open_ports = probe_open_ports(ip_str)
                hostname = resolve_hostname(ip_str, timeout=0.35)
                device_type = guess_device_type(vendor, ip_str, gateway_ip, open_ports)
                
                device_info = {
                    "ip": ip_str,
                    "mac": mac,
                    "hostname": hostname,
                    "vendor": vendor,
                    "device_type": device_type,
                    "latency": latency,
                    "open_ports": open_ports,
                    "is_online": True,
                    "found_at": time.strftime("%H:%M:%S")
                }
                return device_info
            return None

        # Execute multi-threaded scan (75 workers gives ideal balance of speed and stability)
        workers = min(75, max(20, self.total_targets // 3))
        with ThreadPoolExecutor(max_workers=workers) as executor:
            future_to_ip = {executor.submit(scan_single_host, h): h for h in hosts}
            
            for future in as_completed(future_to_ip):
                self.scanned_count += 1
                self.current_progress = int((self.scanned_count / self.total_targets) * 100)
                
                try:
                    result = future.result()
                    if result:
                        self.found_devices.append(result)
                        if progress_callback:
                            progress_callback({
                                "type": "device_found",
                                "device": result,
                                "scanned": self.scanned_count,
                                "total": self.total_targets,
                                "percent": self.current_progress
                            })
                    else:
                        if progress_callback and self.scanned_count % 5 == 0:
                            progress_callback({
                                "type": "progress",
                                "scanned": self.scanned_count,
                                "total": self.total_targets,
                                "percent": self.current_progress
                            })
                except Exception:
                    pass

        self.is_scanning = False
        duration = round(time.time() - self.start_time, 2)
        
        # Sort found devices naturally by IP
        self.found_devices.sort(key=lambda d: [int(x) for x in d['ip'].split('.')])

        if progress_callback:
            progress_callback({
                "type": "complete",
                "total_found": len(self.found_devices),
                "duration": duration,
                "devices": self.found_devices
            })

        return self.found_devices

# Global scanner instance
scanner_instance = NetworkScanner()
