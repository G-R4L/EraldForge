#!/data/data/com.termux/files/usr/bin/env python3
# EraldForge - Port Scanner (Erald Edition Upgraded)
# By Gerald (G-R4L) — enhanced: banner, menu, nmap detection, socket fallback, logging, auto-scan

import os
import subprocess
import socket
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
import argparse

# ---------------- Configuration (Variables Global) ----------------
# Ambil nilai dari environment Termux/Linux atau gunakan default
SCAN_LOG = Path.home() / ".eraldforge_portscan.log"
# Gunakan mekanisme env var agar mudah diubah dari luar
DEFAULT_TIMEOUT = float(os.environ.get("ERALDFORGE_SCAN_TIMEOUT", "0.45"))
MAX_WORKERS = int(os.environ.get("ERALDFORGE_SCAN_WORKERS", "120"))
# Global TARGET untuk diisi dari Environment Variable ERALDFORGE_TARGET
TARGET = os.environ.get("ERALDFORGE_TARGET", "").strip()

# ---------------- Colors (neon yellow banner + accents) ----------------
C_NEON = "\033[93m"    # yellow/neon for banner
C_BOX  = "\033[96m"   # cyan for boxes/info
G     = "\033[32m"    # green success / prompts
R     = "\033[91m"    # red error
Y     = "\033[33m"    # yellow normal
W     = "\033[0m"     # reset
BOLD  = "\033[1m"

# ---------------- Banner ASCII ----------------
BANNER_LINES = [
    "·····························································",
    C_NEON + ": ____            _     ____                                  " + W + C_NEON + ":",
    C_NEON + ":|  _ \\ ___  _ __| |_  / ___|  ___ __ _ _ __  _ __   ___ _ __ " + W + C_NEON + ":",
    C_NEON + ":| |_) / _ \\| '__| __| \\___ \\ / __/ _` | '_ \\| '_ \\ / _ \\ '__|" + W + C_NEON + ":",
    C_NEON + ":|  __/ (_) | |  | |_   ___) | (_| (_| | | | | | | |  __/ |   " + W + C_NEON + ":",
    C_NEON + ":|_|   \\___/|_|   \\__| |____/ \\___\\__,_|_| |_|_| |_|\\___|_|   " + W + C_NEON + ":",
    "·····························································",
]

def print_banner():
    os.system("clear")
    for line in BANNER_LINES:
        print(line)
    print(C_BOX + BOLD + "EraldForge Port Scanner — Modern • Professional" + W)
    print(C_BOX + "════════════════════════════════════════════════════════════════" + W)

# ---------------- Utilities ----------------
def has_nmap():
    """Cek apakah Nmap terpasang"""
    try:
        # check=True akan memunculkan error jika Nmap tidak ditemukan
        subprocess.run(["nmap", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except Exception:
        return False

def run_nmap(target, extra_args=None):
    """Menjalankan Nmap sebagai proses eksternal"""
    extra_args = extra_args or []
    # Default args: Ping scan (-Pn), SYN scan (-sS), Top 200 ports
    cmd = ["nmap", "-Pn", "-sS", "--top-ports", "200"] + extra_args + [target]
    print(G + "Menjalankan nmap: " + " ".join(cmd) + W)
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print(R + "\nDibatalkan oleh pengguna." + W)
    except Exception as e:
        print(R + "Error menjalankan nmap: " + str(e) + W)

def socket_scan_single(target, port, timeout):
    """Cek koneksi ke satu port"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            s.connect((target, int(port)))
            return int(port)
    except Exception:
        return None

def socket_scan(target, ports, timeout, workers, verbose=False):
    """Scan port menggunakan multithreading socket"""
    open_ports = []
    try:
        ports = sorted(set(int(p) for p in ports if 1 <= int(p) <= 65535))
    except ValueError:
        print(R + "Error: Ports harus berupa angka." + W)
        return []
    
    if not ports:
        return open_ports

    print(C_BOX + f"Socket-scan: {len(ports)} port, timeout {timeout}s, workers {workers}" + W)

    with ThreadPoolExecutor(max_workers=workers) as pool:
        # Pastikan timeout yang digunakan adalah nilai yang di-pass, bukan default global
        futures = {pool.submit(socket_scan_single, target, p, timeout): p for p in ports}
        
        for fut in as_completed(futures):
            try:
                res = fut.result()
                if res:
                    open_ports.append(res)
                    if verbose:
                        print(G + f"  [OPEN] {res}" + W)
            except Exception:
                pass
                
    return sorted(open_ports)

def log_scan(target, ports, mode="socket"):
    """Menyimpan hasil scan ke file log"""
    try:
        with open(SCAN_LOG, "a") as f:
            f.write(f"[{datetime.now().isoformat()}] mode={mode} target={target} open={ports}\n")
    except Exception:
        pass

def parse_ports_text(text):
    """Mengurai input port kustom (misal: 22,80,443 atau 20-25)"""
    out = set()
    for part in text.split(","):
        part = part.strip()
        if not part: continue
        if "-" in part:
            try:
                a, b = map(int, part.split("-", 1))
                if a > b: a, b = b, a 
                for x in range(max(1, a), min(65535, b) + 1):
                    out.add(x)
            except Exception:
                pass
        else:
            try:
                out.add(int(part))
            except Exception:
                pass
    return sorted(out)

# ---------------- Menu / Interaction ----------------
def print_header(target, using_nmap):
    print()
    print(C_BOX + BOLD + "Target: " + C_NEON + f"{target}" + W)
    print(C_BOX + "Waktu : " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + W)
    print(C_BOX + "Engine: " + (G + "nmap (detected)" + W if using_nmap else Y + "socket fallback" + W))
    print(C_BOX + "════════════════════════════════════════════════════════════════" + W)

def show_main_menu():
    print()
    print(C_BOX + BOLD + "PILIH MODE SCAN (masukkan angka lalu Enter):" + W)
    print(f"  {C_NEON}1{W} - Top ports (recommended, cepat)")
    print(f"  {C_NEON}2{W} - Range 1-1024 (lebih lama)")
    print(f"  {C_NEON}3{W} - Custom ports / rentang")
    print(f"  {C_NEON}4{W} - Auto scan top ports langsung (tanpa input)")
    print(f"  {C_NEON}5{W} - Set timeout / workers")
    print(f"  {C_NEON}6{W} - Tampilkan log scan terakhir")
    print(f"  {C_NEON}7{W} - Keluar")
    print()

def show_log_tail(lines=40):
    if not SCAN_LOG.exists():
        print(Y + "Belum ada log scan." + W)
        return
    try:
        with open(SCAN_LOG, "r") as f:
            data = f.readlines()[-lines:]
        print(C_BOX + "===== Scan log (tail) =====" + W)
        for r in data:
            print(r.rstrip())
        print(C_BOX + "===========================" + W)
    except Exception as e:
        print(R + "Gagal baca log: " + str(e) + W)

def perform_scan(target, using_nmap, mode, ports=None, nmap_args=None):
    """Menjalankan pemindaian berdasarkan mode yang dipilih"""
    global DEFAULT_TIMEOUT, MAX_WORKERS
    
    if ports is None and mode in ("top", "auto"):
        ports = [22,80,443,21,23,25,53,110,143,445,3389,3306,8080]
    elif ports is None and mode == "range_1024":
        ports = list(range(1, 1025))

    start = time.time()
    print(C_BOX + f"Mulai scan mode '{mode}' -> {len(ports)} ports" + W)

    if using_nmap:
        # Jika Nmap terdeteksi, gunakan Nmap (dengan argumen yang sesuai)
        final_args = nmap_args if nmap_args is not None else []
        if mode in ("range_1024", "custom"):
            # Untuk range/custom, Nmap perlu argumen port spesifik
            port_str = ",".join(map(str, ports))
            final_args = ["-p", port_str] + final_args
        run_nmap(target, final_args)
        opens = [] # Tidak bisa mendapatkan hasil dari output nmap dengan mudah
    else:
        # Fallback ke Socket Scan
        opens = socket_scan(target, ports, timeout=DEFAULT_TIMEOUT, workers=MAX_WORKERS, verbose=mode=="custom")
        if opens:
            print(G + "Open ports: " + ", ".join(map(str, opens)) + W)
        else:
            print(Y + "Tidak ada port terbuka terdeteksi." + W)
        
    if opens:
        log_scan(target, opens, mode=f"socket_{mode}")
    
    print(C_BOX + f"Selesai. Durasi: {time.time()-start:.1f}s" + W)
    return opens

# ---------------- Main Interactive ----------------
def interactive_main(auto_target=None):
    global TARGET, DEFAULT_TIMEOUT, MAX_WORKERS
    
    print_banner()
    using_nmap = has_nmap()

    # Ambil target dari argparse, env var, atau minta input
    TARGET = auto_target or TARGET
    if not TARGET:
        TARGET = input(G + "Masukkan target IP/domain: " + W).strip()
        if not TARGET:
            print(R + "Tidak ada target. Keluar." + W)
            return
    
    print_header(TARGET, using_nmap)
    
    # Jika dipanggil dengan --target, langsung jalankan auto scan (Mode 4)
    if auto_target:
        print(C_BOX + "Mode Auto-Scan (dari CLI Argument)" + W)
        perform_scan(TARGET, using_nmap, "auto")
        sys.exit(0) # Keluar setelah auto scan

    while True:
        show_main_menu()
        choice = input(G + "Pilihan [1-7]: " + W).strip()
        
        if choice == "1":
            perform_scan(TARGET, using_nmap, "top")
        elif choice == "2":
            perform_scan(TARGET, using_nmap, "range_1024")
        elif choice == "3":
            raw = input(G + "Masukkan ports (contoh: 22,80,443 atau 20-25): " + W).strip()
            ports = parse_ports_text(raw)
            if not ports:
                print(R + "Tidak ada port valid." + W)
                continue
            perform_scan(TARGET, using_nmap, "custom", ports=ports)
        elif choice == "4":
            perform_scan(TARGET, using_nmap, "auto")
        elif choice == "5":
            print(C_BOX + f"Timeout saat ini: {DEFAULT_TIMEOUT}s, Workers: {MAX_WORKERS}" + W)
            t = input(G + "Set timeout (Enter = tetap): " + W).strip()
            w = input(G + "Set workers (Enter = tetap): " + W).strip()
            if t:
                try: DEFAULT_TIMEOUT = float(t); print(G + f"Timeout diubah menjadi {DEFAULT_TIMEOUT}s" + W)
                except: print(R + "Format timeout tidak valid." + W)
            if w:
                try: MAX_WORKERS = int(w); print(G + f"Workers diubah menjadi {MAX_WORKERS}" + W)
                except: print(R + "Format workers tidak valid." + W)
        elif choice == "6":
            show_log_tail(40)
        elif choice == "7":
            print(G + "Keluar dari EraldForge. Sampai jumpa!" + W)
            break
        else:
            print(R + "Pilihan tidak valid. Masukkan angka 1-7." + W)

# ---------------- Entrypoint ----------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="EraldForge Port Scanner")
    parser.add_argument("--target", help="Target IP/domain untuk auto scan")
    args = parser.parse_args()
    try:
        # Jika 'eraldforge.py' memanggil ini, ia akan mengisi TARGET dari env var, 
        # jika tidak, ia akan meminta input.
        interactive_main(auto_target=args.target)
    except KeyboardInterrupt:
        print("\n" + R + "Dibatalkan oleh pengguna." + W)
        sys.exit(1)