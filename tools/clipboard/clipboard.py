#!/data/data/com.termux/files/usr/bin/env python3
# EraldForge Clipboard Manager v5.0 (Ultimate Edition)
# Fitur: Input Manual, Bersihkan Riwayat, Refresh Menu

import os, sys
from datetime import datetime

# --- Konfigurasi Dasar ---
CLIP_DIR = os.path.join(os.path.expanduser("~"), ".clipboard_manager")
HISTORY_FILE = os.path.join(CLIP_DIR, "history.txt")

# --- Definisi Warna ---
R = "\033[91m"
G = "\033[92m"
Y = "\033[93m"
C = "\033[96m"
W = "\033[0m"
BOLD = "\033[1m"

# --- Banner Erald ---
BANNER = f"""
{Y}···············································{W}
{Y}:  ____ _ _       _                         _ :{W}
{Y}: / ___| (_)_ __ | |__   ___   __ _ _ __ __| |:{W}
{Y}:| |   | | | '_ \| '_ \ / _ \ / _` | '__/ _` |:{W}
{Y}:| |___| | | |_) | |_) | (_) | (_| | | | (_| |:{W}
{Y}: \____|_|_| .__/|_.__/ \___/ \__,_|_|  \__,_|:{W}
{Y}:          |_|                                :{W}
{Y}···············································{W}
"""

# --- Utilitas Data ---
def ensure_directory():
    """Memastikan folder dan file riwayat ada."""
    if not os.path.exists(CLIP_DIR):
        os.makedirs(CLIP_DIR)
        print(f"{C}✅ Dibuat: Folder riwayat otomatis {CLIP_DIR}{W}")
    if not os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'w') as f:
            f.write("") # Buat file kosong

def load_history():
    """Memuat riwayat dari file."""
    ensure_directory()
    try:
        with open(HISTORY_FILE, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]
            history = []
            for line in lines:
                parts = line.split('::', 1)
                if len(parts) == 2:
                    history.append({
                        'timestamp': parts[0].strip(),
                        'content': parts[1].strip()
                    })
            return history
    except Exception as e:
        print(f"{R}⚠️ Error memuat riwayat: {e}{W}")
        return []

def save_history(history):
    """Menyimpan riwayat ke file."""
    ensure_directory()
    try:
        with open(HISTORY_FILE, 'w') as f:
            for item in history:
                f.write(f"{item['timestamp']} :: {item['content']}\n")
    except Exception as e:
        print(f"{R}⚠️ Error menyimpan riwayat: {e}{W}")

def add_to_history(content):
    """Menambahkan konten baru ke riwayat."""
    history = load_history()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    history.append({'timestamp': timestamp, 'content': content})
    save_history(history)
    print(f"{G}✅ Teks berhasil disimpan ke riwayat.{W}")

# --- Fungsi Clipboard Termux API ---
def termux_clipboard_get():
    """Mencoba mengambil teks dari clipboard Termux."""
    try:
        # Perintah Termux API untuk mengambil clipboard
        result = os.popen('termux-clipboard-get').read().strip()
        if not result:
            return None, f"{R}Clipboard kosong.{W}"
        return result, None
    except Exception as e:
        # Menangkap error jika termux-api tidak ada/gagal
        return None, f"{R}Error: termux-api tidak tersedia atau gagal. ({e}){W}"

def termux_clipboard_set(text):
    """Mencoba menempatkan teks ke clipboard Termux."""
    try:
        # Perintah Termux API untuk menempatkan clipboard
        os.system(f'echo "{text}" | termux-clipboard-set')
        return True, None
    except Exception as e:
        return False, f"{R}Error: termux-api tidak tersedia atau gagal. ({e}){W}"

# --- Fitur Inti Clipboard Manager ---

def action_get_clipboard():
    """Aksi 1: Ambil dari clipboard dan simpan."""
    print(f"\n{C}Mengambil dari clipboard Termux...{W}")
    content, error = termux_clipboard_get()

    if error:
        print(f"⚠️ {error}")
        print(f"{Y}➡️ Coba opsi [2] untuk memasukkan teks secara manual.{W}")
        return

    # Jika berhasil, tambahkan ke riwayat
    if content:
        print(f"{C}✅ Berhasil mengambil konten ({len(content)} karakter).{W}")
        add_to_history(content)

def action_manual_input():
    """Aksi 2: Masukkan teks manual dan simpan."""
    print(f"\n{C}Simpan Manual: Masukkan teks yang ingin Anda simpan.{W}")
    print(f"{C}──────────────────────────────────────────────{W}")
    manual_content = input(f"{G}{BOLD}Masukkan Teks > {W}").strip()
    
    if manual_content:
        add_to_history(manual_content)
    else:
        print(f"{Y}❌ Tidak ada teks dimasukkan. Pembatalan.{W}")

def action_show_history():
    """Aksi 3: Tampilkan riwayat."""
    history = load_history()
    print(f"\n{C}──────────────────────────────────────────────{W}")
    print(f"{C} Riwayat Tersimpan ({len(history)} item){W}")
    print(f"{C}──────────────────────────────────────────────{W}")
    
    if not history:
        print(f"{Y}Riwayat masih kosong.{W}")
        return

    # Tampilkan 100 item terakhir
    for i, item in enumerate(history[-100:], 1):
        # Tampilkan hanya 50 karakter pertama untuk ringkasan
        summary = item['content'][:50] + ('...' if len(item['content']) > 50 else '')
        print(f"[{i:02}] {item['timestamp']} | {summary}")

    print(f"{C}──────────────────────────────────────────────{W}")

def action_set_clipboard():
    """Aksi 4: Pilih item dari riwayat dan tempatkan ke clipboard."""
    history = load_history()
    action_show_history()
    
    if not history: return

    try:
        choice_str = input(f"{G}{BOLD}Pilih nomor item untuk ditempel (0 untuk batal) > {W}").strip()
        choice = int(choice_str)
        
        if choice == 0:
            print(f"{Y}Pembatalan operasi tempel.{W}")
            return

        # Pastikan pilihan valid dalam 100 item terakhir
        if 1 <= choice <= len(history):
            # Mengambil item dari posisi yang benar (indeks dimulai dari 0)
            selected_item = history[choice - 1] 
            
            # Tempel ke clipboard Termux
            success, error = termux_clipboard_set(selected_item['content'])
            
            if success:
                print(f"{G}✅ Berhasil: Item [{choice}] ditempel ke clipboard aktif.{W}")
            else:
                print(f"⚠️ {error}")
                print(f"{R}Pastikan Termux:API terinstal dan berfungsi.{W}")
        else:
            print(f"{R}❌ Pilihan tidak valid.{W}")

    except ValueError:
        print(f"{R}❌ Masukkan harus berupa angka.{W}")
    except Exception as e:
        print(f"{R}Error: {e}{W}")

def action_search_history():
    """Aksi 5: Cari teks dalam riwayat."""
    history = load_history()
    if not history:
        print(f"{Y}Riwayat masih kosong.{W}")
        return

    search_term = input(f"{G}{BOLD}Masukkan teks yang dicari > {W}").strip().lower()
    if not search_term:
        print(f"{Y}Tidak ada kata kunci dimasukkan.{W}")
        return
    
    results = []
    for item in history:
        if search_term in item['content'].lower():
            results.append(item)

    print(f"\n{C}──────────────────────────────────────────────{W}")
    print(f"{C} Hasil Pencarian ({len(results)} ditemukan){W}")
    print(f"{C}──────────────────────────────────────────────{W}")
    
    if not results:
        print(f"{Y}Tidak ada item yang cocok dengan '{search_term}'.{W}")
        return

    for i, item in enumerate(results, 1):
        summary = item['content'][:50] + ('...' if len(item['content']) > 50 else '')
        print(f"[{i:02}] {item['timestamp']} | {summary}")
    print(f"{C}──────────────────────────────────────────────{W}")

def action_clear_history():
    """Aksi 6: Bersihkan semua riwayat yang tersimpan."""
    print(f"\n{R}{BOLD}⚠️ PERINGATAN: Menghapus semua riwayat. Tindakan ini TIDAK dapat dibatalkan!{W}")
    
    confirm = input(f"{Y}Ketik '{BOLD}YA{W}{Y}' untuk konfirmasi penghapusan seluruh riwayat: {W}").strip().upper()
    
    if confirm == 'YA':
        try:
            # Timpa file riwayat dengan kosong
            with open(HISTORY_FILE, 'w') as f:
                f.write("")
            print(f"{G}✅ Riwayat {HISTORY_FILE} berhasil dihapus/dibersihkan.{W}")
        except Exception as e:
            print(f"{R}❌ Gagal menghapus riwayat: {e}{W}")
    else:
        print(f"{Y}Pembatalan penghapusan riwayat.{W}")


# --- Loop Utama ---
def main():
    os.system('clear')
    
    while True:
        print(BANNER)
        print(f"{C}EraldForge Clipboard Manager v5.0 (Ultimate Edition){W}")
        print(f"{C}──────────────────────────────────────────────{W}")
        print(f"[1] Ambil dari Clipboard - Salin item saat ini dari clipboard sistem ke riwayat.")
        print(f"[2] Simpan Manual        - Masukkan teks secara manual ke riwayat.")
        print(f"[3] Tampilkan Riwayat    - Lihat 100 item terakhir yang tersimpan.")
        print(f"[4] Tempel ke Clipboard  - Salin item dari riwayat ke clipboard aktif.")
        print(f"[5] Cari Riwayat         - Cari teks di antara item yang tersimpan.")
        print(f"{C}──────────────────────────────────────────────{W}")
        print(f"[6] Bersihkan Riwayat    - Hapus permanen semua item yang tersimpan.")
        print(f"[R] Refresh Menu         - Bersihkan layar dan tampilkan menu lagi.")
        print(f"[0] Keluar               - Tutup Clipboard Manager.")
        print(f"{C}──────────────────────────────────────────────{W}")
        
        try:
            choice = input(f"{G}{BOLD}Pilihan > {W}").strip().upper()
            
            if choice == '1':
                action_get_clipboard()
            elif choice == '2':
                action_manual_input()
            elif choice == '3':
                action_show_history()
            elif choice == '4':
                action_set_clipboard()
            elif choice == '5':
                action_search_history()
            elif choice == '6':
                action_clear_history()
            elif choice == 'R': # Pilihan refresh
                os.system('clear')
                continue # Langsung ke awal loop untuk menampilkan menu baru
            elif choice == '0':
                print(f"{Y}Keluar dari Clipboard Manager. Sampai jumpa!{W}")
                break
            else:
                print(f"{R}❌ Pilihan tidak valid. Silakan coba lagi.{W}")
        
        except KeyboardInterrupt:
            print(f"\n{Y}Keluar dari Clipboard Manager. Sampai jumpa!{W}")
            break
        except Exception as e:
            print(f"{R}Error tak terduga: {e}{W}")

if __name__ == "__main__":
    main()