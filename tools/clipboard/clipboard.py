#!/data/data/com.termux/files/usr/bin/env python3
# EraldForge - Clipboard Manager v3.0

import os
import json
import subprocess
import time
from pathlib import Path
from datetime import datetime
import textwrap

# --- Path dan Konfigurasi ---
HOME = Path.home()
HFILE = HOME / ".eraldforge_clipboard.json"
MAX_HISTORY = 200 # Batas maksimal item yang disimpan
MAX_DISPLAY = 100 # Batas item yang ditampilkan di list

# --- Color and Theme Integration ---
def get_colors():
    """Mengambil palet warna dari variabel lingkungan EraldForge."""
    C = {
        "num": "\033[36m",    # Cyan
        "title": "\033[34m",  # Blue
        "desc": "\033[37m",   # White/Light Gray
        "accent": "\033[33m", # Yellow
        "reset": "\033[0m",
        "bold": "\033[1m",
        "error": "\033[31m"   # Red for errors
    }
    # Jika program dijalankan dari EraldForge, variabel lingkungan akan disetel.
    # Namun, karena ini adalah tool mandiri, kita pakai default aman.
    return C

C = get_colors()

# --- Banner ASCII ---
BANNER_LINES = [
    "···············································",
    ":  ____ _ _       _                         _ :",
    ": / ___| (_)_ __ | |__   ___   __ _ _ __ __| |:",
    ":| |   | | | '_ \| '_ \ / _ \ / _` | '__/ _` |:",
    ":| |___| | | |_) | |_) | (_) | (_| | | | (_| |:",
    ": \____|_|_| .__/|_.__/ \___/ \__,_|_|  \__,_|:",
    ":          |_|                                :",
    "···············································"
]

def colored_banner():
    """Mencetak banner dengan warna Accent."""
    out = []
    for line in BANNER_LINES:
        if line.startswith(":") or line.startswith("·"):
            out.append(f"{C['accent']}{line}{C['reset']}")
        else:
            # Mewarnai teks di dalam banner
            out.append(f"{C['title']}{line}{C['reset']}")
    return "\n".join(out)

# --- Data Handling ---
def load_hist():
    """Memuat riwayat dari file JSON."""
    if not HFILE.exists(): return []
    try: 
        data = json.loads(HFILE.read_text())
        # Filter untuk memastikan data valid
        return [item for item in data if 'text' in item and 'ts' in item]
    except Exception: 
        return []

def save_hist(h):
    """Menyimpan riwayat ke file JSON, membatasi ukuran."""
    try: 
        # Batasi jumlah item
        HFILE.write_text(json.dumps(h[:MAX_HISTORY], indent=2))
    except Exception: 
        pass

# --- Termux Clipboard API Wrappers ---
def get_clip():
    """Mengambil teks dari clipboard Termux."""
    try:
        # Menambahkan timeout agar tidak menggantung
        out = subprocess.check_output(["termux-clipboard-get"], timeout=1).decode(errors='ignore').strip()
        return out if out else None
    except Exception:
        return None

def set_clip(text):
    """Menyalin teks ke clipboard Termux."""
    try:
        subprocess.run(["termux-clipboard-set", text], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=1)
        return True
    except Exception:
        return False

# --- Main Logic ---
def show_menu():
    """Menampilkan menu utama."""
    os.system("clear")
    print(colored_banner())
    print(f"{C['title']}EraldForge Clipboard Manager v3.0{C['reset']}")
    print(f"{C['accent']}──────────────────────────────────────────────{C['reset']}")
    
    menu = [
        ("1", "Ambil & Simpan", "Salin item saat ini di clipboard ke riwayat."),
        ("2", "Tampilkan Riwayat", "Lihat 100 item terakhir yang tersimpan."),
        ("3", "Tempel ke Clipboard", "Salin item dari riwayat ke clipboard aktif."),
        ("4", "Cari Riwayat", "Cari teks di antara item yang tersimpan."),
        ("0", "Keluar", "Tutup Clipboard Manager dan kembali ke menu utama.")
    ]
    
    max_len = max(len(t) for _, t, _ in menu)
    
    for code, title, desc in menu:
        print(f"{C['num']}[{code}]{C['reset']} {C['title']}{title:<{max_len}}{C['reset']} - {C['desc']}{desc}{C['reset']}")
        
    print(f"{C['accent']}──────────────────────────────────────────────{C['reset']}")
    return input(f"{C['bold']}Pilihan:{C['reset']} ").strip()

def handle_save(hist):
    """Menangani pilihan 1: Save current clipboard."""
    print(f"{C['accent']}Mengambil dari clipboard Termux...{C['reset']}")
    txt = get_clip()
    
    if not txt:
        print(f"{C['error']}⚠️ Error: Clipboard kosong atau termux-api tidak tersedia.{C['reset']}"); time.sleep(2); return

    # Cek duplikat (opsional: jika item paling atas sama)
    if hist and hist[0]["text"] == txt:
        print(f"{C['title']}Teks sama dengan item terakhir. Tidak disimpan.{C['reset']}"); time.sleep(2); return
        
    hist.insert(0, {"text": txt, "ts": int(time.time())})
    save_hist(hist)
    
    preview = textwrap.shorten(txt.replace("\n", " "), width=50, placeholder="...")
    print(f"{C['num']}✔ Berhasil menyimpan. {C['title']}Preview:{C['reset']} {preview}{C['reset']}")
    time.sleep(2)

def handle_list(hist):
    """Menangani pilihan 2: Tampilkan riwayat."""
    os.system("clear")
    print(f"{C['title']}=== Riwayat Clipboard ({len(hist)} item) ==={C['reset']}")
    
    if not hist:
        print(f"{C['accent']}Riwayat kosong.{C['reset']}"); time.sleep(2); return

    print(f"{C['accent']}------------------------------------------------{C['reset']}")
    for i, it in enumerate(hist[:MAX_DISPLAY], start=1):
        ts = datetime.fromtimestamp(it.get("ts", time.time())).strftime("%Y-%m-%d %H:%M:%S")
        
        # Bersihkan teks dari newline untuk tampilan rapi
        t = it.get("text", "--- ERROR ---").replace("\n", " ")
        preview = textwrap.shorten(t, width=os.get_terminal_size().columns - 25, placeholder="...")
        
        print(f"{C['num']}[{i:02}]{C['reset']} {C['desc']}{ts}{C['reset']}: {C['title']}{preview}{C['reset']}")
        
    print(f"{C['accent']}------------------------------------------------{C['reset']}")
    input("Tekan Enter untuk kembali... ")

def handle_paste(hist):
    """Menangani pilihan 3: Tempel item ke clipboard."""
    if not hist:
        print(f"{C['error']}Riwayat kosong.{C['reset']}"); time.sleep(2); return
        
    idx_str = input(f"{C['bold']}Masukkan Nomor Index ke-Riwayat:{C['reset']} ").strip()
    try:
        idx = int(idx_str) - 1
        if idx < 0 or idx >= len(hist):
            raise ValueError
            
        ok = set_clip(hist[idx]["text"])
        
        if ok:
            preview = textwrap.shorten(hist[idx]["text"].replace("\n", " "), width=50, placeholder="...")
            print(f"{C['num']}✔ Berhasil disalin. {C['title']}Preview:{C['reset']} {preview}{C['reset']}")
        else:
            print(f"{C['error']}❌ Gagal menyalin ke clipboard Termux.{C['reset']}")
            
    except ValueError:
        print(f"{C['error']}Index tidak valid.{C['reset']}")
        
    time.sleep(2)

def handle_search(hist):
    """Menangani pilihan 4: Cari riwayat."""
    os.system("clear")
    q = input(f"{C['bold']}Query Pencarian:{C['reset']} ").strip().lower()
    if not q: return

    results = []
    for i, it in enumerate(hist, start=1):
        if q in it.get("text", "").lower():
            results.append((i, it))

    print(f"\n{C['title']}=== Hasil Pencarian ({len(results)} ditemukan) ==={C['reset']}")
    
    if not results:
        print(f"{C['accent']}Tidak ada hasil untuk '{q}'.{C['reset']}"); time.sleep(2); return

    for i, (idx_original, it) in enumerate(results, start=1):
        ts = datetime.fromtimestamp(it.get("ts", time.time())).strftime("%Y-%m-%d %H:%M:%S")
        t = it.get("text", "--- ERROR ---").replace("\n", " ")
        preview = textwrap.shorten(t, width=os.get_terminal_size().columns - 25, placeholder="...")
        
        # Tampilkan index original di riwayat
        print(f"{C['num']}[{idx_original:02}]{C['reset']} {C['desc']}{ts}{C['reset']}: {C['title']}{preview}{C['reset']}")
    
    print(f"{C['accent']}------------------------------------------------{C['reset']}")
    input("Tekan Enter untuk kembali... ")


def main():
    while True:
        hist = load_hist()
        choice = show_menu()
        
        if choice == "1":
            handle_save(hist)
        elif choice == "2":
            handle_list(hist)
        elif choice == "3":
            handle_paste(hist)
        elif choice == "4":
            handle_search(hist)
        elif choice in ("0", "q"):
            print(f"{C['title']}Keluar dari Clipboard Manager. Sampai jumpa!{C['reset']}"); break
        else:
            print(f"{C['error']}Pilihan tidak valid.{C['reset']}"); time.sleep(1)

if __name__ == "__main__":
    main()