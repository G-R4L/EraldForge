#!/usr/bin/env python3
# EraldForge WI-FI INFO Tool
# Sebuah utilitas untuk menampilkan informasi jaringan Wi-Fi di lingkungan Termux atau Linux.

import os
import sys
import subprocess
import re
from datetime import datetime

# ---------------- Colors & Style (FULL NEON YELLOW BANNER) ----------------
C_NEON = "\033[93m"     # Neon Yellow (Banner, High Priority)
C_BOX  = "\033[96m"     # Cyan (Box/Headers/Menu, untuk kontras)
G      = "\033[32m"     # Green (Success/Info)
R      = "\033[91m"     # Red (Error/Warning)
Y      = "\033[33m"     # Yellow (General Text)
W      = "\033[0m"      # Reset
BOLD   = "\033[1m"
DIM    = "\033[2m"      # Dim

# ---------------- Banner ASCII (KUNING NEON KESELURUHAN & Fixed Escape) ----------------
# Menggunakan C_NEON untuk semua elemen visual banner.
# Diperbaiki: Menggunakan \\ untuk mengatasi SyntaxWarning pada backslash.
BANNER_LINES = [
    C_NEON + "··························" + W,
    C_NEON + ":" + BOLD + C_NEON + "__        _______  __  " + W + C_NEON + ":" + W,
    C_NEON + ":" + BOLD + C_NEON + "\\\\ \\      / / ____|/ _| " + W + C_NEON + ":" + W, # \ \      / /
    C_NEON + ":" + BOLD + C_NEON + " \\\\ \\ /\\ / / |__ | |_  " + W + C_NEON + ":" + W, #  \ \ /\ / /
    C_NEON + ":" + BOLD + C_NEON + "  \\\\ V  V /|  __||  _| " + W + C_NEON + ":" + W, #   \ V  V /
    C_NEON + ":" + BOLD + C_NEON + "   \\\\_/\\_/ |_|   |_|   " + W + C_NEON + ":" + W, #    \_/\_/
    C_NEON + "··························" + W,
]

def print_banner():
    """Mencetak banner dan header utama aplikasi."""
    os.system("clear")
    for line in BANNER_LINES:
        print(line)
    print(C_BOX + BOLD + "EraldForge WI-FI INFO (Termux/Linux)" + W)
    print(C_BOX + "══════════════════════════════════════════" + W)

# ---------------- Helper Functions ----------------

def run_cmd(command):
    """Menjalankan perintah shell dan mengembalikan output atau None jika gagal."""
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False, # Jangan raise exception untuk non-zero exit code
            encoding='utf-8',
            errors='ignore'
        )
        return result.stdout.strip()
    except FileNotFoundError:
        # Perintah tidak ditemukan (misalnya 'iw' tidak terinstal)
        return None
    except Exception:
        # Error lain (permission, dll.)
        return None

def get_wifi_interface():
    """Mencari nama antarmuka Wi-Fi yang paling mungkin (misalnya wlan0, eth0, atau netcfg/ip)"""
    # 1. Cek dengan 'ip link show'
    ip_output = run_cmd(["ip", "link", "show"])
    if ip_output:
        # Cari pola umum: wlanX, raX, atmlanX, dsb. (kecuali loopback lo)
        interfaces = re.findall(r"(\d+): (wlan\d+|eth\d+|ra\d+|.*lan\d+):", ip_output)
        if interfaces:
            # Mengambil antarmuka pertama selain 'lo'
            for num, name in interfaces:
                if name != "lo":
                    return name

    # 2. Cek dengan 'netcfg' (khusus Termux/Android lama)
    netcfg_output = run_cmd(["netcfg"])
    if netcfg_output:
        # Cari antarmuka dengan alamat IP non-0.0.0.0
        lines = netcfg_output.split('\n')
        for line in lines:
            if "wlan" in line and "0.0.0.0" not in line and "UP" in line:
                return line.split()[0].strip()

    # Default fallback
    return "wlan0" # Interface umum

# ---------------- Core Logic Functions ----------------

def show_network_status(interface):
    """Menampilkan status koneksi dan IP Address saat ini."""
    print(C_BOX + BOLD + f"\n[ 1. STATUS KONEKSI: {interface} ]" + W)
    
    # 1. Mendapatkan status koneksi/IP
    ip_address = run_cmd(["ip", "addr", "show", interface])
    if ip_address:
        # Parse IP Address
        ip_match = re.search(r"inet (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", ip_address)
        if ip_match:
            ip = ip_match.group(1)
            print(f"{G}✅ Status Antarmuka:{W} {BOLD}UP{W}")
            print(f"{G}⭐ IP Address:{W} {ip}")
        else:
            print(f"{R}Status Antarmuka:{W} Down atau IP tidak ditemukan.")

    # 2. Mendapatkan SSID yang terhubung (menggunakan wpa_cli status jika ada)
    ssid = "Tidak Terhubung"
    wpa_status = run_cmd(["wpa_cli", "status"])
    if wpa_status and "wpa_state=COMPLETED" in wpa_status:
        ssid_match = re.search(r"ssid=(.*)", wpa_status)
        bssid_match = re.search(r"bssid=(.*)", wpa_status)
        freq_match = re.search(r"freq=(.*)", wpa_status)

        if ssid_match: ssid = ssid_match.group(1)
        if bssid_match: print(f"{G}⭐ BSSID:{W} {bssid_match.group(1)}")
        if freq_match: print(f"{G}⭐ Frekuensi:{W} {freq_match.group(1)} MHz")
        
    print(f"{G}⭐ SSID Terkoneksi:{W} {BOLD}{ssid}{W}")

def scan_available_networks(interface):
    """Memindai dan menampilkan daftar jaringan Wi-Fi di sekitar."""
    print(C_BOX + BOLD + f"\n[ 2. PEMINDAIAN JARINGAN (Interface: {interface}) ]" + W)
    
    # Coba menggunakan iw (perlu diinstal dan mungkin perlu root)
    scan_output = run_cmd(["iw", interface, "scan"])
    
    if not scan_output:
        # Fallback: Perintah 'iw' gagal/tidak ada, coba dengan 'termux-wifi-scan' (khusus Termux)
        scan_output = run_cmd(["termux-wifi-scan"])
        
        if not scan_output:
             print(f"{R}Perintah 'iw' atau 'termux-wifi-scan' tidak ditemukan atau gagal.{W}")
             print(f"{R}Pastikan Anda telah menginstal 'iw' ({Y}pkg install iw{R}) atau memiliki izin root.{W}")
             return

        # Parsing output termux-wifi-scan (JSON)
        try:
            import json
            scan_data = json.loads(scan_output)
            print(f"{C_BOX}SSID | Signal (dBm) | BSSID{W}")
            print(C_BOX + "-----+--------------+-------------------" + W)
            for ap in scan_data:
                ssid = ap.get("ssid", "<Hidden/N/A>")
                signal = ap.get("signal_level", "N/A")
                bssid = ap.get("bssid", "N/A")
                
                # Highlight berdasarkan kekuatan sinyal
                signal_color = R if signal != "N/A" and int(signal) < -70 else G if signal != "N/A" and int(signal) > -50 else Y
                
                print(f"{Y}{ssid.ljust(4)}{W} | {signal_color}{signal.ljust(12)}{W} | {bssid}")
            return
        except (ImportError, json.JSONDecodeError):
             # Jika JSON parsing gagal atau 'json' tidak tersedia
             print(f"{R}Gagal memparsing output pemindaian. Coba instal 'iw' atau jalankan sebagai root.{W}")
             return


    # Parsing output 'iw <interface> scan' (Standar Linux)
    print(f"{C_BOX}SSID | Signal (dBm) | BSSID | Encryption{W}")
    print(C_BOX + "-----+--------------+------------+-------------------" + W)

    aps = re.split(r'BSS\s+([0-9a-fA-F:]{17})\s+\(on', scan_output)
    
    for i in range(1, len(aps), 2):
        bssid = aps[i]
        details = aps[i+1]
        
        ssid_match = re.search(r'SSID:\s*(.*)', details)
        signal_match = re.search(r'signal:\s*([-\d\.]+)\s*dBm', details)
        encryption_match = re.search(r'RSN|WPA|WEP', details)
        
        ssid = ssid_match.group(1).strip() if ssid_match else "<Hidden>"
        signal = signal_match.group(1).strip() if signal_match else "N/A"
        encryption = "WPA2/3" if "RSN" in details else "WPA" if "WPA" in details else "WEP" if "WEP" in details else "Open"
        
        # Highlight berdasarkan kekuatan sinyal
        signal_color = R
        if signal != "N/A":
            try:
                sig_val = float(signal)
                if sig_val > -50: signal_color = G
                elif sig_val > -70: signal_color = Y
            except ValueError:
                pass # Tetap R jika parsing gagal

        print(
            f"{Y}{ssid.ljust(4)}{W} | "
            f"{signal_color}{signal.ljust(12)}{W} | "
            f"{bssid} | "
            f"{encryption}"
        )

# ---------------- Main Execution ----------------

def main():
    print_banner()
    
    interface = get_wifi_interface()
    
    if not interface:
        print(f"{R}❌ Gagal mendeteksi antarmuka jaringan Wi-Fi yang aktif.{W}")
        print(f"{R}Coba jalankan dengan izin root atau pastikan Wi-Fi aktif.{W}")
        input(f"{C_BOX}Tekan Enter untuk keluar...{W}")
        return

    print(f"{Y}Antarmuka Terdeteksi:{W} {BOLD}{interface}{W}")

    while True:
        try:
            print_banner()
            show_network_status(interface)
            scan_available_networks(interface)

            print(f"\n{C_BOX}{BOLD}===== MENU AKSI =====" + W)
            print(f"{C_BOX}1.{W} {G}r{W}: Refresh Data  | {C_BOX}2.{W} {C_NEON}q{W}: Quit")
            print(C_BOX + "══════════════════════════════════════════" + W)
            
            cmd = input(f"{C_BOX}▶ Pilihan Anda: {W}").strip().lower()

            if cmd in ("r", "refresh", "1"):
                print(f"{C_BOX}Memperbarui data...{W}")
                continue # Kembali ke awal loop untuk refresh
                
            elif cmd in ("q", "quit", "exit", "2"):
                print(f"{C_NEON}Keluar dari EraldForge WI-FI INFO. Sampai jumpa!{W}")
                break
            else:
                print(f"{R}Pilihan tidak dikenal. Masukkan r atau q.{W}")
                input(f"{C_BOX}Tekan Enter untuk melanjutkan...{W}")
                
        except EOFError:
            print(f"\n{C_NEON}Keluar dari EraldForge WI-FI INFO.{W}")
            sys.exit(0)
        except Exception as e:
            print(f"{R}Terjadi error tak terduga: {e}{W}")
            print(f"{Y}Mohon pastikan utilitas jaringan seperti 'ip', 'iw', atau 'netcfg' terinstal.{W}")
            input(f"{C_BOX}Tekan Enter untuk melanjutkan...{W}")

if __name__ == "__main__":
    main()