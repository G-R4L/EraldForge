# Membuat Python script lengkap dengan banner ASCII yang telah diperbaiki.
# Skrip ini berfungsi untuk menampilkan informasi jaringan Wi-Fi di lingkungan Termux atau Linux.

import os
import sys
import subprocess
import re
from datetime import datetime
import json # Diperlukan untuk memproses output termux-wifi-scan

# ---------------- Colors & Style (FULL NEON YELLOW BANNER) ----------------
C_NEON = "\033[93m"      # Neon Yellow (Banner, High Priority)
C_BOX  = "\033[96m"      # Cyan (Box/Headers/Menu, untuk kontras)
G      = "\033[32m"      # Green (Success/Info)
R      = "\033[91m"      # Red (Error/Warning)
Y      = "\033[33m"      # Yellow (General Text)
W      = "\033[0m"       # Reset
BOLD   = "\033[1m"
DIM    = "\033[2m"       # Dim

# Variabel warna placeholder (untuk memastikan kompatibilitas)
C_NEON = '\033[93m' 
W = '\033[0m'      
BOLD = '\033[1m'   

# TOTAL LEBAR BINGKAI = 44 KARAKTER
# TOTAL LEBAR KONTEN (antara ':') = 42 KARAKTER
BANNER_LINES = [
    C_NEON + "············································" + W,
    # Baris 1: Diperbaiki agar total 42 karakter
    C_NEON + BOLD + ":__      ___  __ _  ___        __          " + C_NEON + ":", 
    # Baris 2: Diperbaiki agar total 42 karakter
    C_NEON + BOLD + ":\ \      / (_)/ _(_) |_ _|_ __  / _| ___   " + C_NEON + ":", 
    # Baris 3: Diperbaiki agar total 42 karakter
    C_NEON + BOLD + ": \ \ /\ / /| | |_| |  | || '_ \| |_ / _ \  " + C_NEON + ":", 
    # Baris 4: Diperbaiki agar total 42 karakter
    C_NEON + BOLD + ":  \ V  V / | |  _| |  | || | | |  _| (_) | " + C_NEON + ":", 
    # Baris 5: Diperbaiki agar total 42 karakter
    C_NEON + BOLD + ":   \_/\_/  |_|_| |_| |___|_| |_|_|  \___/  " + C_NEON + ":", 
    C_NEON + "············································" + W,
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

def check_tool_available(tool_name):
    """Mengecek ketersediaan tool di PATH."""
    try:
        # Menjalankan perintah dengan output ke /dev/null
        subprocess.run(["which", tool_name], capture_output=True, check=True, timeout=5)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError, TimeoutError):
        # Jika perintah tidak ditemukan atau mengembalikan error
        return False
    except Exception:
        # Error umum
        return False

def get_wifi_interface():
    """Mencari nama antarmuka Wi-Fi yang paling mungkin (misalnya wlan0, eth0, atau netcfg/ip)"""
    # 1. Cek dengan 'ip link show'
    ip_output = run_cmd(["ip", "link", "show"])
    if ip_output:
        # Cari pola umum: wlanX, ethX, dsb. (kecuali loopback lo)
        # Regex diperbaiki agar lebih fleksibel mencari nama interface (contoh: wlan0:)
        interfaces = re.findall(r"\d+: ([\w\d]+):", ip_output)
        if interfaces:
            for name in interfaces:
                # Prioritaskan antarmuka nirkabel umum
                if name.startswith("wlan") or name.startswith("ra"):
                    return name
                # Fallback ke ethernet/interface aktif lainnya selain loopback
                if name != "lo":
                    return name

    # 2. Cek dengan 'netcfg' (khusus Termux/Android lama)
    netcfg_output = run_cmd(["netcfg"])
    if netcfg_output:
        lines = netcfg_output.split('\n')
        for line in lines:
            if "wlan" in line and "0.0.0.0" not in line and "UP" in line:
                return line.split()[0].strip()

    # Default fallback
    return "wlan0"

# ---------------- Core Logic Functions ----------------

def show_instructions():
    """Menampilkan panduan langkah-langkah penggunaan dan instalasi."""
    os.system("clear")
    print_banner()

    print(C_BOX + BOLD + "[ 3. PANDUAN LANGKAH-LANGKAH & INSTALASI ]" + W)
    print(C_BOX + "========================================" + W)
    print(f"{G}Selamat datang di EraldForge WI-FI INFO!{W} Ini adalah alat untuk melihat status jaringan dan memindai Wi-Fi di lingkungan Termux/Linux.\n")

    # --- Bagian 1: Persiapan Awal (Prasyarat) ---
    print(C_NEON + BOLD + "## 1. PRASYARAT DAN INSTALASI ##" + W)
    print(Y + "Pastikan Anda memiliki Termux (untuk Android) atau lingkungan Linux (Ubuntu/Kali) dan Python 3 terinstal." + W)
    
    print(BOLD + "\n[A] Instalasi di Termux (Android):" + W)
    print(f"{Y}1. Perbarui sistem:{W} {G}pkg update && pkg upgrade{W}")
    print(f"{Y}2. Instal Python:{W} {G}pkg install python{W}")
    print(f"{Y}3. Instal Utilitas Jaringan Dasar:{W} {G}pkg install iproute2 iw{W}")
    print(f"{Y}4. (PENTING) Untuk Pemindaian Wi-Fi, instal Termux API:{W}")
    print(f"   {G}pkg install termux-api{W}")
    print(f"   {G}termux-setup-storage{W} (Izinkan akses penyimpanan jika diminta)")
    
    print(BOLD + "\n[B] Instalasi di Linux (Debian/Ubuntu/Kali):" + W)
    print(f"{Y}1. Instal Python 3 dan PIP:{W} {G}sudo apt update && sudo apt install python3 python3-pip{W}")
    print(f"{Y}2. Instal Utilitas Jaringan:{W} {G}sudo apt install iproute2 iw wpasupplicant{W}")

    # --- Bagian 2: Cara Menjalankan Skrip ---
    print(C_NEON + BOLD + "\n## 2. CARA MENJALANKAN ##" + W)
    print(Y + "Asumsikan nama file skrip ini adalah 'wifi_tool.py':" + W)
    print(f"{Y}1. Simpan kode di atas ke file ({G}wifi_tool.py{Y}).{W}")
    print(f"{Y}2. Beri izin eksekusi (Opsional, tapi disarankan):{W} {G}chmod +x wifi_tool.py{W}")
    print(f"{Y}3. Jalankan skrip:{W} {G}python wifi_tool.py{W}")
    
    # --- Bagian 3: Penjelasan Menu ---
    print(C_NEON + BOLD + "\n## 3. PENJELASAN MENU ##" + W)
    print(Y + "Layar akan menampilkan 3 bagian laporan otomatis dan Menu Aksi di bawah:" + W)
    
    print(f"{BOLD}\n[A] Laporan Otomatis:{W}")
    print(f"   {G}1. STATUS KONEKSI:{W} Status Antarmuka (UP/DOWN), IP Address, BSSID, dan SSID yang sedang terhubung.")
    print(f"   {G}2. PEMINDAIAN JARINGAN:{W} Daftar jaringan Wi-Fi di sekitar (SSID, kekuatan sinyal, BSSID, dan Enkripsi).")
    print(f"   {G}3. DIAGNOSTIK SISTEM:{W} (Hanya ditampilkan setelah memilih 'd') Memeriksa ketersediaan alat penting seperti 'ip' dan 'iw'.")

    print(f"{BOLD}\n[B] Menu Aksi:{W}")
    print(f"   {G}[r] Refresh:{W} Memuat ulang semua data status dan pemindaian di layar.")
    print(f"   {R}[d] Diagnostik:{W} Menjalankan pemeriksaan ketersediaan alat (direkomendasikan jika ada error).")
    print(f"   {Y}[h] Panduan/Help:{W} Menampilkan layar panduan ini.")
    print(f"   {C_NEON}[q] Quit:{W} Keluar dari aplikasi.")
    
    print("\n" + C_BOX + "========================================" + W)
    input(f"{C_BOX}Tekan Enter untuk kembali ke Menu Utama...{W}")

def check_system_diagnostics():
    """Mengecek ketersediaan utilitas jaringan yang diperlukan."""
    print(C_BOX + BOLD + "\n[ 3. DIAGNOSTIK SISTEM ]" + W)
    print(C_BOX + "=========================" + W)
    
    tools = {
        "ip": "Utilitas dasar IP (PENTING)",
        "iw": "Pemindaian/Informasi Wi-Fi tingkat lanjut (ROOT/Termux-IW)",
        "wpa_cli": "Status koneksi Wi-Fi",
        "termux-wifi-scan": "Pemindaian Wi-Fi (Alternatif Termux)"
    }
    
    all_available = True

    for tool, desc in tools.items():
        available = check_tool_available(tool)
        status = f"{G}✅ TERSEDIA" if available else f"{R}❌ TIDAK DITEMUKAN"
        print(f"[{status}{W}] {BOLD}{tool:<20}{W}{Y}{desc}{W}")
        if not available and tool in ["ip", "iw"]:
            all_available = False
            
    if not all_available:
        print(f"\n{R}PERINGATAN:{W} Beberapa alat penting tidak ditemukan.")
        print(f"{R}Coba instal 'iproute2', 'iw' atau pastikan Termux API diinstal. Ketik '{Y}h{R}' untuk panduan.{W}")
    else:
        print(f"\n{G}✅ SEMUA ALAT PENTING TERSEDIA. Skrip seharusnya berjalan lancar.{W}")


def show_network_status(interface):
    """Menampilkan status koneksi dan IP Address saat ini."""
    print(C_BOX + BOLD + f"\n[ 1. STATUS KONEKSI: {interface} ]" + W)
    
    # 1. Mendapatkan status koneksi/IP
    ip_address = run_cmd(["ip", "addr", "show", interface])
    
    ip = "N/A"
    mac_address = "N/A"
    
    if ip_address and "UP" in ip_address:
        # Parse IP Address
        ip_match = re.search(r"inet (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", ip_address)
        if ip_match:
            ip = ip_match.group(1)
        
        # Parse MAC Address
        mac_match = re.search(r"link/\w+ (([0-9a-fA-F]{2}[:-])+([0-9a-fA-F]{2}))", ip_address)
        if mac_match:
            mac_address = mac_match.group(1)

        print(f"{G}✅ Status Antarmuka:{W} {BOLD}UP{W}")
        print(f"{G}⭐ IP Address:{W} {ip}")
        print(f"{G}⭐ MAC Address:{W} {mac_address}")
        
    else:
        print(f"{R}Status Antarmuka:{W} Down atau informasi gagal diambil.")
        print(f"{R}IP Address:{W} N/A")

    # 2. Mendapatkan SSID yang terhubung (menggunakan wpa_cli status jika ada)
    ssid = "Tidak Terhubung"
    wpa_status = run_cmd(["wpa_cli", "status"])
    
    # Cek apakah wpa_cli tersedia dan berhasil mendapatkan status
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
    
    scan_output = run_cmd(["termux-wifi-scan"])
    is_json_scan = False

    if scan_output and scan_output.startswith('['):
        is_json_scan = True
        
    if not is_json_scan:
        # Fallback: Coba menggunakan iw (Standar Linux/ROOT)
        scan_output = run_cmd(["iw", interface, "scan"])
        
        if not scan_output:
              print(f"{R}Perintah 'iw' atau 'termux-wifi-scan' tidak ditemukan atau gagal.{W}")
              print(f"{R}Pastikan Anda telah menginstal 'iw' dan 'termux-api'. Ketik '{Y}h{R}' untuk panduan instalasi.{W}")
              return

    if is_json_scan:
        # Parsing output termux-wifi-scan (JSON)
        try:
            scan_data = json.loads(scan_output)
            print(f"{C_BOX}SSID | Signal (dBm) | BSSID{W}")
            print(C_BOX + "-----+--------------+-------------------" + W)
            
            # Sortir data berdasarkan kekuatan sinyal (level)
            scan_data.sort(key=lambda x: x.get('level', -100), reverse=True)
            
            for ap in scan_data:
                ssid = ap.get("ssid", "<Hidden/N/A>")
                signal = ap.get("level", "N/A")  # Termux API: 'level' is used
                if signal == "N/A":
                    signal = ap.get("signal_level", "N/A")
                
                bssid = ap.get("bssid", "N/A")
                
                signal_color = R 
                if signal != "N/A":
                    try:
                        sig_val = int(signal)
                        if sig_val > -50: signal_color = G
                        elif sig_val > -70: signal_color = Y
                    except ValueError: pass
                
                print(f"{Y}{ssid:<4}{W} | {signal_color}{str(signal):<12}{W} | {bssid}")
            return
        except json.JSONDecodeError:
             print(f"{R}Gagal memparsing output pemindaian Termux API. Pastikan Termux API diinstal dan izin diberikan.{W}")
             return
    
    # Parsing output 'iw <interface> scan' (Standar Linux Fallback)
    print(f"{C_BOX}SSID | Signal (dBm) | BSSID | Encryption{W}")
    print(C_BOX + "-----+--------------+------------+-------------------" + W)

    aps = re.split(r'BSS\s+([0-9a-fA-F:]{17})\s+\(on', scan_output)
    
    # Karena output iw scan tidak terstruktur, ini adalah parsing dasar
    for i in range(1, len(aps), 2):
        bssid = aps[i]
        details = aps[i+1]
        
        ssid_match = re.search(r'SSID:\s*(.*)', details)
        signal_match = re.search(r'signal:\s*([-\d\.]+)\s*dBm', details)
        encryption = "Open"
        
        # Deteksi Enkripsi
        if "RSN" in details:
            encryption = "WPA2/3"
        elif "WPA" in details:
            encryption = "WPA"
        elif "WEP" in details:
            encryption = "WEP"
        
        ssid = ssid_match.group(1).strip() if ssid_match else "<Hidden>"
        signal = signal_match.group(1).strip() if signal_match else "N/A"
        
        signal_color = R
        if signal != "N/A":
            try:
                sig_val = float(signal)
                if sig_val > -50: signal_color = G
                elif sig_val > -70: signal_color = Y
            except ValueError: pass

        print(
            f"{Y}{ssid:<4}{W} | "
            f"{signal_color}{signal:<12}{W} | "
            f"{bssid} | "
            f"{encryption}"
        )

# ---------------- Main Execution ----------------

def main():
    
    interface = get_wifi_interface()
    
    if not interface:
        print_banner()
        print(f"{R}❌ Gagal mendeteksi antarmuka jaringan Wi-Fi yang aktif.{W}")
        print(f"{R}Coba jalankan dengan izin root atau pastikan Wi-Fi aktif.{W}")
        input(f"{C_BOX}Tekan Enter untuk keluar...{W}")
        return

    while True:
        try:
            print_banner()
            print(f"{Y}Antarmuka Terdeteksi:{W} {BOLD}{interface}{W}")

            show_network_status(interface)
            scan_available_networks(interface)
            
            print(f"\n{C_BOX}{BOLD}===== MENU AKSI =====" + W)
            # Menu baru: 1:Refresh, 2:Diagnostik, 3:Panduan/Help, 4:Quit
            print(f"{C_BOX}1.{W} {G}r{W}: Refresh | {C_BOX}2.{W} {R}d{W}: Diagnostik | {C_BOX}3.{W} {Y}h{W}: Panduan/Help | {C_BOX}4.{W} {C_NEON}q{W}: Quit")
            print(C_BOX + "══════════════════════════════════════════" + W)
            
            cmd = input(f"{C_BOX}▶ Pilihan Anda: {W}").strip().lower()

            if cmd in ("r", "refresh", "1"):
                print(f"{C_BOX}Memperbarui data...{W}")
                continue
                
            elif cmd in ("d", "diag", "diagnostik", "2"):
                os.system("clear")
                print_banner()
                check_system_diagnostics()
                input(f"\n{C_BOX}Tekan Enter untuk kembali ke menu utama...{W}")
                continue
                
            elif cmd in ("h", "help", "panduan", "3"): # Menampilkan panduan baru
                show_instructions()
                continue

            elif cmd in ("q", "quit", "exit", "4"):
                print(f"{C_NEON}Keluar dari EraldForge WI-FI INFO. Sampai jumpa!{W}")
                break
            else:
                print(f"{R}Pilihan tidak dikenal. Masukkan r, d, h, atau q.{W}")
                input(f"{C_BOX}Tekan Enter untuk melanjutkan...{W}")
                
        except EOFError:
            print(f"\n{C_NEON}Keluar dari EraldForge WI-FI INFO.{W}")
            sys.exit(0)
        except Exception as e:
            print(f"{R}Terjadi error tak terduga: {e}{W}")
            print(f"{Y}Mohon periksa kembali konfigurasi sistem Anda. Ketik '{G}h{Y}' untuk melihat panduan.{W}")
            input(f"{C_BOX}Tekan Enter untuk melanjutkan...{W}")

if __name__ == "__main__":
    main()