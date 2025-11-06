#!/data/data/com.termux/files/usr/bin/env python3
"""
EraldForge - QR Code Generator Canggih
Fitur: Mendukung berbagai tipe data (Teks, Wi-Fi, VCard), kustomisasi penuh (ECC, ukuran, border, warna FG/BG), 
preview ASCII berwarna, dan penyimpanan PNG.

Requires: python qrcode pillow (install via pip: pip install qrcode pillow)
"""
import os, sys
from pathlib import Path
import subprocess
import re

try:
    import qrcode
    # Mengimpor konstanta ECC untuk kontrol level koreksi kesalahan
    from qrcode.constants import ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q, ERROR_CORRECT_H
except ImportError:
    # Set qrcode ke None jika library tidak ditemukan untuk menangani fallback
    qrcode = None
    ERROR_CORRECT_L = None

# ---------------- Tema & Warna ----------------

def get_theme_colors():
    """Mengambil skema warna, difokuskan pada Neon Yellow (P) dan Green (G) untuk output."""
    return {
        "P": "\033[93m", # Neon Yellow (Primary Banner/Highlight)
        "R": "\033[91m", # Red (Error)
        "X": "\033[0m",  # Reset
        "B": "\033[36m", # Cyan (User Input Prompt)
        "G": "\033[32m", # Green (Success/Info)
        "W": "\033[97m", # White/Detail
    }

C = get_theme_colors()

# ---------------- Banner & Tampilan ----------------

# Banner dari input user, diperbaiki alignmentnya dan menggunakan warna Neon Yellow (P)
BANNER_LINES = [
    C["P"] + "·················································" + C["X"],
    C["P"] + "\033[1m" + ":  ___        ____          _                  " + C["P"] + ":",
    C["P"] + "\033[1m" + ": / _ \ _ __ / ___|___   __| | ___             " + C["P"] + ":",
    C["P"] + "\033[1m" + ":| | | | '__| |   / _ \ / _` |/ _ \            " + C["P"] + ":",
    C["P"] + "\033[1m" + ":| |_| | |  | |__| (_) | (_| |  __/            " + C["P"] + ":",
    C["P"] + "\033[1m" + ": \__\_\_|   \____\___| \__,_|\___|            " + C["P"] + ":",
    C["P"] + "\033[1m" + ": / ___| ___ _ __   ___ _ __ __ _| |_ ___  _ __ " + C["P"] + ":",
    C["P"] + "\033[1m" + ":| |  _ / _ \ '_ \ / _ \ '__/ _` | __/ _ \| '__|" + C["P"] + ":",
    C["P"] + "\033[1m" + ":| |_| |  __/ | | |  __/ | | (_| | || (_) | |  " + C["P"] + ":",
    C["P"] + "\033[1m" + ": \____|\___|_| |_|\___|_|  \__,_|\__\___/|_|  " + C["P"] + ":",
    C["P"] + "·················································" + C["X"],
]

def display_banner():
    """Mencetak banner EraldForge QR Code Generator."""
    os.system('clear')
    for line in BANNER_LINES:
        print(line)
    print(C["G"] + "QR Code Generator EraldForge Canggih (Fitur #8)" + C["X"])
    print(C["G"] + "===================================================" + C["X"] + "\n")

def ascii_qr(matrix, color=C['P']):
    """Mengubah matriks QR code menjadi tampilan ASCII yang mudah dilihat dengan warna kustom (Neon Yellow)."""
    out = []
    # Menggunakan karakter gelap/terang, dikombinasikan dengan warna Neon Yellow
    for row in matrix:
        line = "".join(f"{color}██{C['X']}" if v else "  " for v in row)
        out.append(line)
    return "\n".join(out)

def copy_to_clipboard(path_str):
    """Menyalin path file ke clipboard (khusus Termux)."""
    try:
        proc = subprocess.Popen(["termux-clipboard-set"], stdin=subprocess.PIPE, text=True, check=False)
        proc.communicate(input=path_str, timeout=1)
        print(f"\n{C['G']}✅ Path file berhasil disalin ke clipboard (via termux-clipboard-set).{C['X']}")
    except FileNotFoundError:
        print(f"\n{C['R']}❌ Gagal menyalin: Perintah 'termux-clipboard-set' tidak ditemukan.{C['X']}")
        print(f"{C['R']}Mohon instal Termux:API dengan perintah: {C['P']}pkg install termux-api{C['R']} lalu pastikan Anda memberikan izin akses.{C['X']}")
    except Exception as e:
        print(f"\n{C['R']}❌ Gagal menyalin ke clipboard: {type(e).__name__}. Coba salin manual.{C['X']}")

# ---------------- Pengaturan Kustomisasi Umum ----------------

def get_ecc_level():
    """Meminta pengguna memilih level koreksi kesalahan."""
    ECC_OPTIONS = {
        "1": (ERROR_CORRECT_L, "L (7%): Low (Data Penuh)"),
        "2": (ERROR_CORRECT_M, "M (15%): Medium (Default, Seimbang)"),
        "3": (ERROR_CORRECT_Q, "Q (25%): Quartile (Tahan Kerusakan Sedang)"),
        "4": (ERROR_CORRECT_H, "H (30%): High (Paling Tahan Kerusakan)"),
    }
    
    print(C["W"] + "\n--- Pilih Level Koreksi Kesalahan (ECC) ---" + C["X"])
    for key, value in ECC_OPTIONS.items():
        print(f"  {C['B']}{key}{C['X']}. {value[1]}")
    
    while True:
        choice = input(f"{C['B']}Pilihan (1-4) [{C['W']}2{C['B']}]: {C['X']}").strip() or "2"
        if choice in ECC_OPTIONS:
            return ECC_OPTIONS[choice][0], ECC_OPTIONS[choice][1]
        print(f"{C['R']}Pilihan tidak valid. Masukkan angka antara 1 dan 4.{C['X']}")

def get_integer_input(prompt, default, min_val, max_val):
    """Meminta input integer dengan validasi."""
    while True:
        try:
            value_input = input(f"{C['B']}{prompt} [{C['W']}{default}{C['B']}]: {C['X']}").strip() or str(default)
            value = int(value_input)
            if min_val <= value <= max_val:
                return value
            else:
                print(f"{C['R']}Nilai harus antara {min_val} dan {max_val}.{C['X']}")
        except ValueError:
            print(f"{C['R']}Input tidak valid. Masukkan angka bulat.{C['X']}")

def get_color_input(prompt, default_hex):
    """Meminta input kode warna HEX dan memvalidasinya."""
    while True:
        color_input = input(f"{C['B']}{prompt} (Contoh: #FF0000) [{C['W']}{default_hex}{C['B']}]: {C['X']}").strip() or default_hex
        # Memvalidasi format HEX (#RRGGBB atau RRGGBB)
        if re.match(r"^#?[0-9a-fA-F]{6}$", color_input):
            # Memastikan ada '#' di depan
            if not color_input.startswith('#'):
                color_input = '#' + color_input
            return color_input
        print(f"{C['R']}Format HEX tidak valid. Gunakan format #RRGGBB.{C['X']}")

# ---------------- Penanganan Tipe Data Terstruktur ----------------

def get_text_url_data():
    """Mengumpulkan data untuk tipe Teks/URL."""
    print(C["W"] + "\n--- Data Teks/URL ---" + C["X"])
    data = input(f"{C['B']}Masukkan Teks atau URL yang akan di-encode: {C['X']}").strip()
    return data, "TEXT/URL"

def get_wifi_data():
    """Mengumpulkan data untuk konfigurasi Wi-Fi (WIFI:T:<encryption>;S:<ssid>;P:<password>;;)."""
    print(C["W"] + "\n--- Konfigurasi Wi-Fi ---" + C["X"])
    ssid = input(f"{C['B']}SSID (Nama Jaringan Wi-Fi): {C['X']}").strip()
    if not ssid:
        print(f"{C['R']}SSID wajib diisi.{C['X']}")
        return None, None
        
    password = input(f"{C['B']}Password Wi-Fi (Kosongkan jika terbuka): {C['X']}").strip()
    
    print(C["W"] + "\n--- Pilih Tipe Enkripsi ---" + C["X"])
    print(f"  {C['B']}1{C['X']}. WPA/WPA2/WPA3 (Default)")
    print(f"  {C['B']}2{C['X']}. WEP")
    print(f"  {C['B']}3{C['X']}. NONE (Terbuka)")
    
    enc_choice = input(f"{C['B']}Pilihan Tipe Enkripsi (1-3) [{C['W']}1{C['B']}]: {C['X']}").strip() or "1"
    
    if enc_choice == '2':
        encryption = "WEP"
    elif enc_choice == '3':
        encryption = "nopass"
    else:
        encryption = "WPA"
        
    # Format Wi-Fi: S:<SSID>;T:<ENCRYPTION>;P:<PASSWORD>;;
    
    if encryption == "nopass":
        qr_data = f"WIFI:S:{ssid};T:nopass;H:false;;"
        info_type = "Wi-Fi (Terbuka)"
    else:
        qr_data = f"WIFI:T:{encryption};S:{ssid};P:{password};H:false;;"
        info_type = f"Wi-Fi ({encryption})"
        
    return qr_data, info_type

def get_vcard_data():
    """Mengumpulkan data untuk kartu kontak (VCard)."""
    print(C["W"] + "\n--- Data Kartu Kontak (VCard) ---" + C["X"])
    name = input(f"{C['B']}Nama Lengkap: {C['X']}").strip()
    org = input(f"{C['B']}Organisasi/Perusahaan (Opsional): {C['X']}").strip()
    phone = input(f"{C['B']}Nomor Telepon: {C['X']}").strip()
    email = input(f"{C['B']}Alamat Email: {C['X']}").strip()

    if not (name or phone or email):
        print(f"{C['R']}Setidaknya Nama, Telepon, atau Email harus diisi.{C['X']}")
        return None, None

    # Membuat VCard (Standar V3.0)
    vcard_lines = [
        "BEGIN:VCARD",
        "VERSION:3.0",
    ]
    if name:
        vcard_lines.append(f"FN:{name}")
        vcard_lines.append(f"N:{name};;;;")
    if org:
        vcard_lines.append(f"ORG:{org}")
    if phone:
        vcard_lines.append(f"TEL;TYPE=CELL:{phone}")
    if email:
        vcard_lines.append(f"EMAIL;TYPE=PREF,INTERNET:{email}")
        
    vcard_lines.append("END:VCARD")
    
    qr_data = "\n".join(vcard_lines)
    info_type = "VCard (Kontak)"
    
    return qr_data, info_type

# ---------------- Alur Generasi Utama ----------------

def generate_qr_code_flow(data, info_type):
    """Mengelola kustomisasi visual dan proses generasi QR Code."""
    
    # 1. Ambil Nama File
    print(C["W"] + "\n--- Nama File Output ---" + C["X"])
    filename = input(f"{C['B']}Nama file output PNG (tanpa ext) [erald_qr]: {C['X']}").strip() or "erald_qr"
    png_path = Path.cwd() / (filename + ".png")

    # 2. Ambil Pengaturan Kustomisasi Visual
    ecc_level, ecc_desc = get_ecc_level()
    box_size = get_integer_input("Ukuran setiap kotak QR (1-10)", default=3, min_val=1, max_val=10)
    border = get_integer_input("Lebar border (min 4, rekomendasi 4)", default=4, min_val=0, max_val=10)
    
    # 3. Kustomisasi Warna
    print(C["W"] + "\n--- Kustomisasi Warna (Kode HEX) ---" + C["X"])
    fg_color = get_color_input("Warna Foreground (Kotak Gelap)", default_hex="#000000") # Hitam
    bg_color = get_color_input("Warna Background (Kotak Terang)", default_hex="#FFFFFF") # Putih

    # 4. Tampilkan Detail Final
    print(C["G"] + "\n--- Detail Generasi Final ---" + C["X"])
    print(f"Tipe Data: {info_type}")
    print(f"Data Mentah (Awal): {data[:50]}...")
    print(f"ECC Level: {ecc_desc}")
    print(f"Ukuran/Border: {box_size} / {border}")
    print(f"Warna PNG (FG/BG): {fg_color} / {bg_color}")
    print("-" * 25 + C['X'])
    
    # 5. Generasi QR Code
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=ecc_level,
            box_size=box_size,
            border=border,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        matrix = qr.get_matrix()
        
        # 6. Tampilkan ASCII Preview
        print(C["G"] + "\n--- ASCII Preview (Untuk Terminal) ---" + C["X"])
        # Menggunakan warna Neon Yellow (P) untuk tampilan konsol
        print(ascii_qr(matrix, color=C['P'])) 
        
        # 7. Generate dan Simpan PNG
        img = qr.make_image(fill_color=fg_color, back_color=bg_color)
        img.save(str(png_path))
        
        print(f"\n{C['G']}✅ Berhasil! PNG disimpan di:{C['X']}")
        print(f"{C['W']}{png_path}{C['X']}")
        
        # 8. Salin Path ke Clipboard
        copy_to_clipboard(str(png_path))
        
    except Exception as e:
        print(f"\n{C['R']}⚠️ ERROR tak terduga saat generasi: {e}{C['X']}")
        
def main_menu():
    """Menampilkan menu utama dan mengarahkan ke alur yang dipilih."""
    while True:
        display_banner()
        print(C["W"] + "Menu Pilihan Tipe Data QR Code:" + C["X"])
        print(f"  {C['B']}1{C['X']}. {C['G']}Teks atau URL (Standar){C['X']}")
        print(f"  {C['B']}2{C['X']}. {C['P']}Konfigurasi Wi-Fi (Mudah Terhubung){C['X']}")
        print(f"  {C['B']}3{C['X']}. {C['W']}Kartu Kontak VCard (Simpan Nomor/Email){C['X']}")
        print(f"  {C['R']}4{C['X']}. {C['R']}Keluar{C['X']}")
        
        choice = input(f"\nPilihan (1-4): ").strip()

        data = None
        info_type = None

        if choice == '1':
            data, info_type = get_text_url_data()
        elif choice == '2':
            data, info_type = get_wifi_data()
        elif choice == '3':
            data, info_type = get_vcard_data()
        elif choice == '4':
            print(f"\n{C['G']}Terima kasih, EraldForge QR Code Generator ditutup.{C['X']}")
            break
        else:
            print(f"\n{C['R']}Pilihan tidak valid. Silakan coba lagi.{C['X']}")
            input(f"\n{C['G']}Tekan Enter untuk kembali ke Menu Utama...{C['X']}")
            continue

        if data:
            generate_qr_code_flow(data, info_type)
        elif data is not None:
             # Menangani kasus di mana pengguna memasukkan data kosong (misalnya di Teks/URL)
             print(f"{C['R']}Input data tidak boleh kosong.{C['X']}")

        input(f"\n{C['G']}Tekan Enter untuk kembali ke Menu Utama...{C['X']}")
        

def main():
    """Fungsi utama."""
    if qrcode is None:
        display_banner()
        print(f"{C['R']}❌ Peringatan: Library 'qrcode' atau 'pillow' tidak terinstal.{C['X']}")
        print(f"{C['G']}Instal dengan perintah:{C['W']}\n  pip install qrcode pillow{C['X']}")
        input(f"\n{C['G']}Tekan Enter untuk keluar...{C['X']}")
        sys.exit(1)

    try:
        main_menu()
    except KeyboardInterrupt:
        print(f"\n{C['R']}Generator dihentikan oleh pengguna.{C['X']}")
        sys.exit(0)

if __name__ == "__main__":
    main()