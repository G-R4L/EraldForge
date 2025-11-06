#!/data/data/com.termux/files/usr/bin/env python3
# EraldForge - Port Scanner (Ultimate Modern Edition)

import os, subprocess, socket, sys, time, json, csv, ipaddress
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

# ---------------- Banner ASCII ----------------
BANNER_LINES = [
    "·······························································",
    " ____            _     ____                                  ",
    "|  _ \\ ___  _ __| |_  / ___|  ___ __ _ _ __  _ __   ___ _ __ ",
    "| |_) / _ \\| '__| __| \\___ \\ / __/ _` | '_ \\| '_ \\ / _ \\ '__|",
    "|  __/ (_) | |  | |_   ___) | (_| (_| | | | | | |  __/ |   ",
    "|_|   \\___/|_|   \\__| |____/ \\___\\__,_|_| |_|_| |_|\\___|_|   ",
    "·······························································",
]

# ---------------- Warna ----------------
C_NEON = "\033[93m"  # Kuning Neon
C_BOX = "\033[96m"   # Cyan untuk border/info
G = "\033[32m"       # Hijau untuk prompt
R = "\033[91m"       # Merah error
Y = "\033[33m"       # Kuning normal
W = "\033[0m"
BOLD = "\033[1m"
ULINE = "\033[4m"

# ---------------- Konfigurasi ----------------
TARGET = os.environ.get("ERALDFORGE_TARGET", "").strip()
SCAN_LOG = os.path.join(os.path.expanduser("~"), ".eraldforge_portscan.log")
SAVE_DIR = os.path.join(os.path.expanduser("~"), "eraldforge_scans")
os.makedirs(SAVE_DIR, exist_ok=True)

# ---------------- Banner ----------------
def print_banner():
    for line in BANNER_LINES:
        print(C_NEON + line + W)
    print(C_BOX + " ✦ Modern • Professional • Multifungsi • Ultimate ✦" + W)

# ---------------- Utility ----------------
def has_nmap():
    try:
        subprocess.run(["nmap","--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except:
        return False

def run_nmap(tgt, args):
    cmd = ["nmap", "-Pn", "-sS", "--top-ports", "200"] + args + [tgt]
    print(G + "Running: " + " ".join(cmd) + W)
    subprocess.run(cmd)

def socket_scan(tgt, ports, timeout=0.5):
    open_ports=[]
    def scan_port(p):
        try:
            s=socket.socket()
            s.settimeout(timeout)
            s.connect((tgt,p))
            s.close()
            return p
        except:
            return None
    with ThreadPoolExecutor(max_workers=200) as ex:
        for res in ex.map(scan_port, ports):
            if res: open_ports.append(res)
    return sorted(open_ports)

def log_scan(target, ports):
    try:
        with open(SCAN_LOG, "a") as f:
            f.write(f"[{datetime.now()}] {target} -> Open ports: {ports}\n")
    except:
        pass

def save_scan(target, ports, filename=None):
    if not filename:
        filename = f"{target}_{int(time.time())}.json"
    path = os.path.join(SAVE_DIR, filename)
    try:
        with open(path, "w") as f:
            json.dump({"target": target, "open_ports": ports, "timestamp": str(datetime.now())}, f, indent=4)
        print(G + f"Hasil scan disimpan: {path}" + W)
    except Exception as e:
        print(R + f"Gagal menyimpan: {e}" + W)

# ---------------- Menu ----------------
def main_menu():
    print("\n" + C_BOX + BOLD + "1. Scan Top Ports (Default)" + W)
    print(C_BOX + BOLD + "2. Scan Full Range (1-1024)" + W)
    print(C_BOX + BOLD + "3. Scan Custom Ports" + W)
    print(C_BOX + BOLD + "4. Scan UDP Ports (1-1024)" + W)
    print(C_BOX + BOLD + "5. Scan Range IP/Subnet" + W)
    print(C_BOX + BOLD + "6. Exit" + W)

def get_ports_input():
    ports = input(G + "Masukkan port (pisahkan koma, misal 22,80,443): " + W)
    try:
        return [int(p.strip()) for p in ports.split(",") if p.strip().isdigit()]
    except:
        print(R + "Format port salah!" + W)
        return []

def scan_udp(tgt, ports):
    print(Y + f"Scanning UDP {tgt} ... (timeout 1s per port)" + W)
    open_ports=[]
    def scan_port(p):
        try:
            s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
            s.settimeout(1)
            s.sendto(b"",(tgt,p))
            s.recvfrom(1024)
            return p
        except:
            return None
    with ThreadPoolExecutor(max_workers=100) as ex:
        for res in ex.map(scan_port, ports):
            if res: open_ports.append(res)
    return sorted(open_ports)

def scan_range(subnet):
    try:
        net = ipaddress.ip_network(subnet, strict=False)
        for ip in net.hosts():
            print(C_BOX + f"\nScanning {ip} ..." + W)
            ports = [22,80,443,21,23,25,53,110,143,445,3389,3306,8080]
            if has_nmap():
                run_nmap(str(ip), [])
            else:
                opens = socket_scan(str(ip), ports)
                if opens: print(G + f"Open ports: {','.join(map(str,opens))}" + W)
                log_scan(str(ip), opens)
    except Exception as e:
        print(R + f"Format subnet salah: {e}" + W)

# ---------------- Main ----------------
def main():
    global TARGET
    os.system("clear")
    print_banner()

    if not TARGET:
        TARGET = input(G + "Masukkan target IP/domain: " + W).strip()
    if not TARGET:
        print(R + "Target tidak boleh kosong!" + W)
        return

    while True:
        main_menu()
        choice = input(G + "Pilih opsi: " + W).strip()
        if choice == "1":
            ports = [22,80,443,21,23,25,53,110,143,445,3389,3306,8080]
            print(C_BOX + f"Scanning {TARGET} top ports..." + W)
        elif choice == "2":
            ports = list(range(1,1025))
            print(C_BOX + f"Scanning {TARGET} full range 1-1024..." + W)
        elif choice == "3":
            ports = get_ports_input()
            if not ports: continue
        elif choice == "4":
            ports = list(range(1,1025))
            opens = scan_udp(TARGET, ports)
            if opens: print(G + "Open UDP ports: " + ",".join(map(str,opens)) + W)
            save_scan(TARGET, opens, f"{TARGET}_udp.json")
            continue
        elif choice == "5":
            subnet = input(G + "Masukkan subnet (misal 192.168.1.0/24): " + W).strip()
            scan_range(subnet)
            continue
        elif choice == "6":
            print(G + "Keluar dari EraldForge Port Scanner. Sampai jumpa!" + W)
            break
        else:
            print(R + "Pilihan tidak valid!" + W)
            continue

        if has_nmap():
            run_nmap(TARGET, [])
        else:
            opens = socket_scan(TARGET, ports)
            if opens:
                print(G + "Open ports: " + ",".join(map(str,opens)) + W)
            else:
                print(Y + "Tidak ada port terbuka ditemukan." + W)
            log_scan(TARGET, opens)
            save_scan(TARGET, opens)

if __name__=="__main__":
    main()
