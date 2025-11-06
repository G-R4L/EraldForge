#!/data/data/com.termux/files/usr/bin/env python3
# EraldForge - WiFi Info (Professional Scanner)
# Menampilkan dan menganalisis hasil pemindaian Wi-Fi dengan detail, sortir, dan fitur canggih.

import os, json, subprocess
import sys
from pathlib import Path
from datetime import datetime

# ---------------- Global State & Configuration ----------------
# Data OUI/Vendor (Simplified & Partial)
OUI_VENDORS = {
    "00:1A:11": "Cisco Systems", "00:0C:F1": "Dell Inc.", 
    "F4:F2:6D": "TP-Link Tech", "60:A4:4C": "Netgear", 
    "C8:3A:35": "Apple, Inc.", "3C:37:86": "Xiaomi Comm.",
    "10:7B:44": "Samsung", "A4:20:66": "Huawei Tech",
    "00:00:00": "Private/Reserved", "5C:6A:8F": "Google, Inc."
}

# Global state untuk sorting
CURRENT_SORT = "level" # 'level', 'ssid', 'freq'

# ---------------- Colors & Style ----------------
def get_colors(theme):
    """Mendapatkan set warna berdasarkan tema yang dipilih."""
    if theme == "hacker":
        return {
            # Hijau (G) untuk tema Hacker
            "G": "\033[32m", "W": "\033[0m", "Y": "\033[33m", "C_NEON": "\033[93m",
            "C_BOX": "\033[96m", "R": "\033[91m", "BOLD": "\033[1m", "DIM": "\033[2m"
        }
    else: # clean/default
        return {
            # Biru (G) untuk tema Clean
            "G": "\033[34m", "W": "\033[0m", "Y": "\033[33m", "C_NEON": "\033[93m",
            "C_BOX": "\033[96m", "R": "\033[91m", "BOLD": "\033[1m", "DIM": "\033[2m"
        }

def theme_prompt():
    """Meminta pengguna memilih tema, atau menggunakan environment variable."""
    t = os.environ.get("ERALDFORGE_THEME", "").lower()
    if t in ("hacker", "clean"): return t
    t = input("Tema [hacker/clean] (default clean): ").strip().lower()
    return t if t in ("hacker", "clean") else "clean"

# Inisialisasi variabel global warna
THEME = theme_prompt()
COLORS = get_colors(THEME)
G, W, Y, C_NEON, C_BOX, R, BOLD, DIM = (
    COLORS['G'], COLORS['W'], COLORS['Y'], COLORS['C_NEON'], 
    COLORS['C_BOX'], COLORS['R'], COLORS['BOLD'], COLORS['DIM']
)

# Banner ASCII baru dengan warna kuning (C_NEON)
BANNER_NEW = [
    C_NEON + "············································" + W,
    C_NEON + ":"+BOLD+C_NEON+"__      ___  __ _  ___         __        :"+W,
    C_NEON + ":"+BOLD+C_NEON+"\\ \     / (_)/ _(_) |_ _|_ __  / _| ___  :"+W,
    C_NEON + ":"+BOLD+C_NEON+" \\ \ /\ / /| | |_| |  | || '_ \\| |_ / _ \\ :"+W,
    C_NEON + ":"+BOLD+C_NEON+"  \\ V  V / | |  _| |  | || | | |  _| (_) |:"+W,
    C_NEON + ":"+BOLD+C_NEON+"   \\_/\\_/  |_|_| |_| |___|_| |_|_|  \\___/ :"+W,
    C_NEON + "············································" + W,
]

def print_banner():
    """Mencetak banner dan header utama, serta membersihkan layar."""
    os.system("clear")
    for line in BANNER_NEW:
        print(line)
    print(f"{C_BOX}{BOLD}EraldForge WiFi Info Utility (Professional Scan) - {THEME.upper()} Theme{W}")
    print(C_BOX + "════════════════════════════════════════════" + W)

# ---------------- Analysis Functions ----------------

def get_vendor_name(bssid):
    """Mengidentifikasi vendor berdasarkan OUI (Organizationally Unique Identifier)."""
    if not bssid or bssid == "??:??:??:??:??:??":
        return "Unknown"
    
    # Ambil 3 oktet pertama (OUI)
    oui_prefix = ":".join(bssid.upper().split(':')[:3])
    # Hanya OUI dari dictionary yang ditampilkan, jika tidak, tampilkan "Unknown Vendor"
    return OUI_VENDORS.get(oui_prefix, f"{DIM}Unknown Vendor{W}")

def get_band_info(freq):
    """Menentukan band (2.4/5/6 GHz) berdasarkan frekuensi."""
    try:
        f = int(freq)
        if 2400 <= f <= 2500:
            return "2.4 GHz", f"{G}2.4G{W}"
        elif 5150 <= f <= 5850:
            return "5 GHz", f"{C_BOX}5G{W}"
        elif 5925 <= f <= 7125:
            return "6 GHz", f"{Y}6G{W}"
        else:
            return "Other", f"{R}??{W}"
    except (ValueError, TypeError):
        return "N/A", f"{R}N/A{W}"

def get_signal_status(level):
    """Menentukan status dan indikator kekuatan sinyal (dBm)."""
    try:
        level = int(level)
    except (ValueError, TypeError):
        return (W, "N/A", "N/A")

    if level > -50:
        return (G, "EXCELLENT", "████") # Hijau
    elif level >= -60:
        return (C_BOX, "GOOD     ", "███░") # Cyan
    elif level >= -70:
        return (Y, "FAIR     ", "██░░") # Kuning
    else:
        return (R, "POOR     ", "█░░░") # Merah

# ---------------- Core Scan Functions ----------------
def run_scan():
    """Menjalankan pemindaian Wi-Fi menggunakan termux-wifi-scaninfo."""
    try:
        # Menangkap output dan mengabaikan error ke /dev/null
        out = subprocess.check_output(["termux-wifi-scaninfo"], stderr=subprocess.DEVNULL).decode('utf-8')
        data = json.loads(out)
        return data
    except FileNotFoundError:
        return f"Perintah 'termux-wifi-scaninfo' tidak ditemukan. Pastikan sudah terinstal."
    except Exception as e:
        return f"Error saat menjalankan pemindaian: {e}"

def sort_data(data):
    """Mengurutkan data berdasarkan status global CURRENT_SORT."""
    global CURRENT_SORT
    if CURRENT_SORT == "level":
        # Urutkan berdasarkan level sinyal (Descending: terkuat pertama)
        return sorted(data, key=lambda x: int(x.get('level', -100)), reverse=True)
    elif CURRENT_SORT == "ssid":
        # Urutkan berdasarkan SSID (Alphabetical)
        return sorted(data, key=lambda x: x.get('SSID') or x.get('ssid', 'z'))
    elif CURRENT_SORT == "freq":
        # Urutkan berdasarkan frekuensi (Ascending)
        return sorted(data, key=lambda x: int(x.get('frequency', 9999)), reverse=False)
    else:
        return data # Default

# ---------------- Display & Interactive Functions ----------------

def show_results(data):
    """Menampilkan hasil pemindaian dalam format tabel yang sangat profesional."""
    
    sorted_data = sort_data(data)
    
    if not sorted_data:
        print(f"\n{Y}⚠️ Tidak ada jaringan Wi-Fi ditemukan dalam pemindaian ini.{W}")
        return

    # Header Tabel (Rapi, 5 kolom utama + Indeks)
    print(f"\n{C_BOX}{BOLD}┌{'─'*4}┬{'─'*30}┬{'─'*10}┬{'─'*6}┬{'─'*8}┬{'─'*20}┐{W}")
    print(f"{C_BOX}│ {'No':<2} │ {'SSID (Jaringan)':<28} │ {'Signal':<8} │ {'Band':<4} │ {'Freq':<6} │ {'Vendor':<18} │{W}")
    print(f"{C_BOX}├{'─'*4}┼{'─'*30}┼{'─'*10}┼{'─'*6}┼{'─'*8}┼{'─'*20}┤{W}")
    
    for i, ap in enumerate(sorted_data, start=1):
        ssid = ap.get("SSID") or ap.get("ssid") or "(Hidden/Unknown)"
        bssid = (ap.get("BSSID") or ap.get("bssid") or "??:??:??:??:??:??").upper()
        level = ap.get("level", ap.get("rssi", "N/A")) 
        freq = ap.get("frequency", "N/A")
        
        # Analisis Sinyal & Vendor
        color, _, signal_bar = get_signal_status(level)
        _, band_display = get_band_info(freq)
        vendor = get_vendor_name(bssid)
        
        # Penyesuaian tampilan SSID
        ssid_display = ssid[:28].ljust(28) 
        vendor_display = vendor[:18].ljust(18)

        # Format baris output
        output_line = (
            f"{C_BOX}│ {str(i).ljust(2)}{W} "
            f"│ {G}{ssid_display}{W} "
            f"│ {color}{signal_bar}{W} {str(level):>4} "
            f"│ {band_display} "
            f"│ {str(freq):<6} "
            f"│ {DIM}{vendor_display}{W} │"
        )
        print(output_line)

    # Footer Tabel
    print(f"{C_BOX}└{'─'*4}┴{'─'*30}┴{'─'*10}┴{'─'*6}┴{'─'*8}┴{'─'*20}┘{W}")
    print(f"{C_BOX}Total Jaringan: {len(sorted_data)} | Disortir berdasarkan: {CURRENT_SORT.upper()}{W}")
    return sorted_data

def handle_sort_menu():
    """Menu untuk mengubah kriteria sorting."""
    global CURRENT_SORT
    print_banner()
    print(f"{C_BOX}{BOLD}===== PENGATURAN SORTING =====" + W)
    print(f" {G}l{W}: Level Sinyal (Terkuat)")
    print(f" {Y}s{W}: SSID (Abjad)")
    print(f" {C_BOX}f{W}: Frekuensi (Terendah)")
    print(C_BOX + "════════════════════════════════════════════" + W)
    
    cmd = input(f"{C_BOX}▶ Urutan Saat Ini ({CURRENT_SORT.upper()}). Pilih Opsi (l/s/f): {W}").strip().lower()
    
    if cmd == "l": CURRENT_SORT = "level"
    elif cmd == "s": CURRENT_SORT = "ssid"
    elif cmd == "f": CURRENT_SORT = "freq"
    else: 
        print(f"{R}Pilihan tidak valid.{W}")
        input(f"{C_BOX}Tekan Enter untuk melanjutkan...{W}")
        return
    
    print_banner()
    print(f"{G}Sorting diubah menjadi: {CURRENT_SORT.upper()}{W}")

def handle_detail_view(data):
    """Menampilkan detail lengkap dari AP yang dipilih."""
    if not data:
        print(f"{R}Tidak ada data untuk ditampilkan.{W}"); 
        input(f"{C_BOX}Tekan Enter...{W}")
        return

    raw_idx = input(f"\n{C_BOX}▶ Masukkan Nomor (No) AP untuk Detail: {W}").strip()
    try:
        idx_display = int(raw_idx) - 1
        selected_ap = data[idx_display]
    except (ValueError, IndexError):
        print(f"{R}Nomor AP tidak valid.{W}"); 
        input(f"{C_BOX}Tekan Enter...{W}")
        return

    print_banner()
    print(f"{C_BOX}{BOLD}===== DETAIL JARINGAN: {selected_ap.get('SSID') or selected_ap.get('ssid') or 'N/A'} ====={W}")

    for key, value in selected_ap.items():
        display_key = key.replace('_', ' ').upper().ljust(15)
        
        # Analisis tambahan untuk kunci tertentu
        if key.lower() in ["bssid", "bssid_oem"]:
            value = (value.upper() if isinstance(value, str) else str(value))
            vendor = get_vendor_name(value)
            value_display = f"{value} ({G}{vendor}{W})"
        elif key.lower() in ["level", "rssi"]:
            color, status, _ = get_signal_status(value)
            value_display = f"{color}{value} dBm ({status.strip()}){W}"
        elif key.lower() in ["frequency"]:
            band_name, _ = get_band_info(value)
            value_display = f"{value} MHz ({C_BOX}{band_name}{W})"
        else:
            value_display = str(value)

        print(f"{G}{display_key}{W}: {value_display}")
    
    print(C_BOX + "════════════════════════════════════════════" + W)
    input(f"{C_BOX}Tekan Enter untuk kembali ke daftar...{W}")


# ---------------- Main Interaction Loop ----------------
def main():
    # PERBAIKAN SYNTAX ERROR: 
    # Deklarasi global harus diletakkan di awal fungsi jika variabel global 
    # di-reassign (diberi nilai baru) di dalamnya, seperti saat ganti tema.
    global THEME, COLORS, G, W, Y, C_NEON, C_BOX, R, BOLD, DIM
    
    print_banner()
    
    while True:
        data = run_scan()
        if isinstance(data, str):
            print(f"\n{R}{BOLD}❌ Gagal Melakukan Pemindaian:{W}")
            print(f"{Y}   {data}{W}")
            print(f"{C_BOX}   Pastikan utilitas Termux API sudah terinstal dan perizinan sudah diberikan.{W}")
            
            print(f"\n{C_BOX}{BOLD}===== MENU AKSI =====" + W)
            print(f" {C_BOX}1.{W} {C_BOX}r{W}: Refresh Scan")
            print(f" {C_BOX}2.{W} {C_NEON}q{W}: Quit")
            print(C_BOX + "════════════════════════════════════════════" + W)
            
            cmd = input(f"{C_BOX}▶ Pilihan Anda: {W}").strip().lower()

        else:
            # Tampilkan hasil scan jika berhasil
            sorted_ap_list = show_results(data)
            
            # Menu Pilihan Baru dan Canggih
            print(f"\n{C_BOX}{BOLD}===== MENU AKSI =====" + W)
            print(f" {C_BOX}1.{W} {C_BOX}r{W}: Refresh Scan  | {C_BOX}2.{W} {Y}s{W}: Sort List     | {C_BOX}3.{W} {G}d{W}: View Detail")
            print(f" {C_BOX}4.{W} {C_BOX}t{W}: Change Theme  | {C_BOX}5.{W} {C_NEON}q{W}: Quit")
            print(C_BOX + "════════════════════════════════════════════" + W)
            
            cmd = input(f"{C_BOX}▶ Pilihan Anda: {W}").strip().lower()

        if cmd == "r":
            # Refresh Scan
            print_banner()
            print(f"{G}Scanning ulang jaringan...{W}")
            continue
            
        elif cmd == "s" and not isinstance(data, str):
            # Sort List
            handle_sort_menu()
            continue
            
        elif cmd == "d" and not isinstance(data, str):
            # View Detail
            handle_detail_view(sorted_ap_list)
            print_banner()
            continue
            
        elif cmd == "t":
            # Change Theme
            print_banner()
            new_theme = input(f"{C_BOX}Ganti Tema [hacker/clean]: {W}").strip().lower()
            if new_theme in ("hacker", "clean"):
                THEME = new_theme
                COLORS = get_colors(THEME)
                # Re-assign semua variabel global warna
                G, W, Y, C_NEON, C_BOX, R, BOLD, DIM = (
                    COLORS['G'], COLORS['W'], COLORS['Y'], COLORS['C_NEON'], 
                    COLORS['C_BOX'], COLORS['R'], COLORS['BOLD'], COLORS['DIM']
                )
                print_banner()
                print(f"{G}Tema diubah menjadi {THEME.upper()}{W}")
            else:
                print(f"{R}Tema tidak valid. Kembali ke Clean.{W}")
                input(f"{C_BOX}Tekan Enter...{W}")
            continue

        elif cmd in ("q", "quit", "exit"):
            print(f"{C_NEON}Keluar dari EraldForge WiFi Scanner. Sampai jumpa!{W}")
            break
        else:
            print(f"{R}Pilihan tidak dikenal. Masukkan r, s, d, t, atau q.{W}")
            input(f"{C_BOX}Tekan Enter untuk melanjutkan...{W}")
            print_banner()
            
if __name__ == "__main__":
    try:
        main()
    except EOFError:
        print(f"\n{C_NEON}Keluar dari EraldForge WiFi Scanner.{W}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{R}Terjadi error fatal: {e}{W}")
        sys.exit(1)