#!/data/data/com.termux/files/usr/bin/env python3
# EraldForge File Explorer v6.0 - Advanced Terminal File Explorer
# Fitur: Banner Neon, Dual Theme (Pro/Hacker), Navigasi Cepat, Detail File Ekstensif, ZIP/UNZIP, Hapus Rekursif.

import os, shutil, stat, zipfile
from pathlib import Path
from datetime import datetime
import textwrap

# --- Konfigurasi Dasar & Lokasi ---
HOME = Path.home()
VERSION = "6.0"
APP_NAME = "EraldForge File Explorer"

# --- Definisi Warna & Gaya ---
# Warna untuk "Pro" Theme (Default: Biru/Cyan)
C_PRO_DIR = "\033[96m"  # Cyan untuk Direktori
C_PRO_FILE = "\033[37m" # Putih untuk File
C_PRO_SIZE = "\033[94m" # Biru terang untuk ukuran
C_PRO_TIME = "\033[35m" # Magenta untuk waktu
C_PRO_PROMPT = "\033[92m" # Hijau terang untuk prompt

# Warna untuk "Hacker" Theme (Hijau/Kuning)
C_HACK_DIR = "\033[92m" # Hijau terang
C_HACK_FILE = "\033[32m" # Hijau
C_HACK_SIZE = "\033[93m" # Kuning neon untuk ukuran
C_HACK_TIME = "\033[90m" # Abu-abu gelap untuk waktu
C_HACK_PROMPT = "\033[93m" # Kuning neon

# Warna Universal
R = "\033[91m"     # Merah (Error)
Y = "\033[93m"     # Kuning Neon (Banner)
W = "\033[0m"      # Reset
BOLD = "\033[1m"   # Tebal

# --- Manajemen Tema (Ditingkatkan) ---
def get_theme_config():
    """Mengambil tema yang dipilih user atau default 'pro'."""
    os.system('clear')
    print(get_banner(show_info=False)) # Tampilkan banner tanpa info waktu
    print(f"{BOLD}{Y}:: KONFIGURASI TEMA ::{W}")
    t = os.environ.get("ERALDFORGE_THEME", "").lower()
    if t in ("hacker", "pro"): return t
    
    t = input(f"{Y}Pilih Tema [{C_PRO_PROMPT}pro{W}/{C_HACK_PROMPT}hacker{W}] (default pro) > {W}").strip().lower()
    return t if t in ("hacker", "pro") else "pro"

THEME_NAME = get_theme_config()

if THEME_NAME == "hacker":
    DIR_COLOR, FILE_COLOR, SIZE_COLOR, TIME_COLOR, PROMPT_COLOR = C_HACK_DIR, C_HACK_FILE, C_HACK_SIZE, C_HACK_TIME, C_HACK_PROMPT
else:
    DIR_COLOR, FILE_COLOR, SIZE_COLOR, TIME_COLOR, PROMPT_COLOR = C_PRO_DIR, C_PRO_FILE, C_PRO_SIZE, C_PRO_TIME, C_PRO_PROMPT

# --- Fungsi Banner ASCII (Neon) ---
def get_banner(show_info=True):
    """Mencetak banner ASCII sesuai permintaan dengan warna Neon."""
    ASCII_LINES = [
        "·························································",
        ": _____ _ _        _____            _       _           :",
        ":|  ___(_) | ___  | ____|_  ___ __ | | ___ | | ___ _ __ :",
        ":| |_  | | |/ _ \\ |  _| \\ \\/ / '_ \\| |/ _ \\| |/ _ \\ '__|:",
        ":|  _| | | |  __/ | |___ >  <| |_) | | (_) | |  __/ |   :",
        ":|_|   |_|_|\\___| |_____/_/\\_\\ .__/|_|\\___/|_|\\___|_|   :",
        ":                            |_|                        :",
        "·························································",
    ]
    
    banner_ascii = [f"{Y}{line}{W}" for line in ASCII_LINES]
    
    if show_info:
        info_line = (
            f"\n{BOLD}{PROMPT_COLOR}:: {APP_NAME} v{VERSION}{W} | "
            f"{DIR_COLOR}Theme: {THEME_NAME.capitalize()}{W} | "
            f"{TIME_COLOR}Time: {datetime.now().strftime('%H:%M:%S')}{W}\n"
        )
        return "\n".join(banner_ascii) + info_line
    
    return "\n".join(banner_ascii) + "\n"

# --- Utilitas Data & Format ---
def human_size(n):
    """Mengubah byte menjadi format yang mudah dibaca."""
    for unit in ('B','KB','MB','GB','TB'):
        if n < 1024: return f"{n:.1f} {unit}" if n < 10 else f"{n:.0f} {unit}"
        n /= 1024
    return f"{n:.1f} PB"

def get_permissions(path):
    """Mendapatkan string izin file (rwx format)."""
    try:
        s = path.stat().st_mode
        # Format: d/f + rwx (user)
        perm = ('d' if stat.S_ISDIR(s) else '-')
        perm += stat.filemode(s)[1:4] # Hanya izin user
        return perm
    except:
        return '????'

def list_dir(p):
    """Mendaftar isi direktori dengan detail."""
    p = Path(p).expanduser().resolve()
    if not p.is_dir(): return []
    
    # Tambahkan '..' untuk navigasi ke atas
    items = [(Path(p.parent), "..")] if p != Path('/') else []
    
    try:
        # Sortir: Direktori di atas, kemudian berdasarkan nama
        items.extend([(it, it.name) for it in p.iterdir()])
        items = sorted(items, key=lambda x: (not x[0].is_dir() if x[1] != '..' else False, x[1].lower()))
    except Exception as e:
        print(f"{R}ERROR: Gagal membaca direktori: {e}{W}")
        return []
    
    res = []
    for i, (path_obj, name) in enumerate(items, start=1):
        if name == "..":
            size_str = "<UP>"
            mod_time = ""
            perm = "d-rwx"
            color = DIR_COLOR
        else:
            try:
                stat_obj = path_obj.stat()
                if path_obj.is_dir():
                    size_str = "<DIR>"
                    color = DIR_COLOR
                else:
                    size_str = human_size(stat_obj.st_size)
                    color = FILE_COLOR
                    
                mod_time = datetime.fromtimestamp(stat_obj.st_mtime).strftime("%Y-%m-%d %H:%M")
                perm = get_permissions(path_obj)
                
            except Exception:
                size_str = "ERR"
                mod_time = "N/A"
                perm = "N/A"
                color = R
        
        # Simpan tuple: (index, Nama, Ukuran, Waktu, Izin, Path, Warna)
        res.append((i, name, size_str, mod_time, perm, path_obj, color))
    return res

# --- Fitur File Manager (Diperluas) ---

def action_preview(path: Path):
    """Menampilkan isi file (4KB pertama)."""
    os.system('clear')
    print(get_banner())
    print(f"{BOLD}{PROMPT_COLOR}:: PREVIEW FILE: {path.name} ::{W}")
    print(f"{'='*50}\n")
    try:
        with open(path, "rb") as f:
            data = f.read(4096)
            try: 
                # Coba decode sebagai teks, ganti karakter yang tidak bisa di-decode
                print(data.decode(errors="replace"))
            except UnicodeDecodeError: 
                # Jika gagal total (kemungkinan binary), cetak raw data
                print(f"{R}[DATA BINARY - TIDAK DAPAT DITAMPILKAN]{W}")
                
    except Exception as e:
        print(f"{R}❌ Gagal membuka: {e}{W}")
    
    print(f"\n{'='*50}")
    input(f"{PROMPT_COLOR}Tekan ENTER untuk kembali...{W}")
    os.system('clear')

def action_zip_folder(cwd: Path, target_name: str):
    """Membuat file ZIP dari folder."""
    src = cwd / target_name
    if not src.is_dir(): print(f"{R}❌ Error: '{target_name}' bukan folder.{W}"); return
    
    out_name = str(src.name) + ".zip"
    try:
        shutil.make_archive(str(cwd / src.name), 'zip', root_dir=str(src.parent), base_dir=str(src.name))
        print(f"{PROMPT_COLOR}✅ Berhasil: ZIP dibuat -> {out_name}{W}")
    except Exception as e:
        print(f"{R}❌ Error membuat ZIP: {e}{W}")

def action_unzip_file(cwd: Path, target_name: str):
    """Mengekstrak file ZIP."""
    src = cwd / target_name
    if not src.is_file() or src.suffix.lower() != '.zip':
        print(f"{R}❌ Error: '{target_name}' bukan file .zip.{W}"); return
    
    out_dir = cwd / src.stem
    try:
        with zipfile.ZipFile(src, 'r') as zf:
            zf.extractall(out_dir)
        print(f"{PROMPT_COLOR}✅ Berhasil: Ekstrak ke folder -> {out_dir.name}{W}")
    except Exception as e:
        print(f"{R}❌ Error ekstrak ZIP: {e}{W}")

def action_delete(path: Path):
    """Menghapus file atau folder rekursif."""
    if not path.exists():
        print(f"{R}❌ Error: Tidak ditemukan.{W}")
        return
        
    confirm = input(f"{R}⚠️ Yakin ingin HAPUS {path.name} secara rekursif? (y/N) > {W}").strip().lower()
    if confirm != 'y':
        print(f"{Y}Pembatalan penghapusan.{W}")
        return

    try:
        if path.is_dir():
            shutil.rmtree(path)
            print(f"{PROMPT_COLOR}✅ Direktori '{path.name}' berhasil dihapus (rekursif).{W}")
        else:
            os.remove(path)
            print(f"{PROMPT_COLOR}✅ File '{path.name}' berhasil dihapus.{W}")
    except Exception as e:
        print(f"{R}❌ Error saat menghapus: {e}{W}")

def action_copy_move(cwd: Path, action: str):
    """Melakukan Copy atau Move."""
    src_name = input(f"{PROMPT_COLOR}Sumber (nama/relatif) > {W}").strip()
    dst_name = input(f"{PROMPT_COLOR}Tujuan (nama/relatif) > {W}").strip()

    src = cwd / src_name
    dst = cwd / dst_name

    if not src.exists():
        print(f"{R}❌ Sumber tidak ditemukan: {src_name}{W}")
        return
        
    try:
        if action == 'copy':
            if src.is_dir():
                # shutil.copytree memerlukan folder tujuan baru
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dst) # copy2 menjaga metadata
            print(f"{PROMPT_COLOR}✅ Berhasil: Disalin dari '{src_name}' ke '{dst_name}'{W}")
        elif action == 'move':
            shutil.move(str(src), str(dst))
            print(f"{PROMPT_COLOR}✅ Berhasil: Dipindahkan dari '{src_name}' ke '{dst_name}'{W}")
    except Exception as e:
        print(f"{R}❌ Error saat {action}: {e}{W}")

# --- Loop Utama Program ---
def main():
    os.system('clear')
    cwd = HOME
    
    while True:
        os.system('clear')
        print(get_banner())
        
        # Tampilkan Direktori Saat Ini
        print(f"{BOLD}{DIR_COLOR}:: PWD: {W}{cwd.resolve()}")
        print("-" * (os.get_terminal_size().columns if os.get_terminal_size().columns < 80 else 80))
        
        items = list_dir(cwd)

        # Tampilkan Daftar File/Folder
        for i, name, size, mtime, perm, path_obj, color in items:
            
            # Format tampilan: [Index] [Izin] [Ukuran] [Waktu] [Nama]
            size_fmt = f"{SIZE_COLOR}{size:>10}{W}"
            mtime_fmt = f"{TIME_COLOR}{mtime:<16}{W}"
            perm_fmt = f"{DIR_COLOR}{perm:<5}{W}"
            
            if name == "..":
                # Item UP/..
                print(f"[{Y}UP{W}] {perm_fmt} {size_fmt} {mtime_fmt} {color}{BOLD}..{W}")
            else:
                # Item Normal
                print(f"[{PROMPT_COLOR}{i:02}{W}] {perm_fmt} {size_fmt} {mtime_fmt} {color}{name}{W}")
        
        print("-" * (os.get_terminal_size().columns if os.get_terminal_size().columns < 80 else 80))
        
        # Menu Perintah Canggih
        print(f"{BOLD}{PROMPT_COLOR}MENU:{W}")
        print(f"  {Y}u{W}=Up | {Y}cd <dir>{W}=ChangeDir | {Y}ls{W}=Refresh/List")
        print(f"  {Y}p <idx/name>{W}=Preview | {Y}d <idx/name>{W}=Delete (Rec.)")
        print(f"  {Y}c/m{W}=Copy/Move | {Y}z <name>{W}=Zip | {Y}un <name>{W}=Unzip")
        print(f"  {Y}q{W}=Quit/Exit")

        command = input(f"{PROMPT_COLOR}CMD > {W}").strip()
        cmd_parts = command.split(' ', 1)
        action = cmd_parts[0].lower()
        target = cmd_parts[1].strip() if len(cmd_parts) > 1 else ""

        if action in ("q", "quit", "exit"):
            print(f"\n{Y}Keluar dari {APP_NAME} v{VERSION}. Sampai jumpa!{W}")
            break
        
        elif action in ("u", "up"):
            if cwd == Path('/'):
                 print(f"{Y}Anda sudah berada di root directory!{W}")
            else:
                cwd = cwd.parent
            continue
            
        elif action in ("ls", "list"):
            # Lanjutkan loop untuk refresh
            continue

        elif action in ("cd", "chdir"):
            try:
                new_path = Path(target).expanduser().resolve()
                if not new_path.is_absolute():
                    new_path = cwd / target
                
                if new_path.is_dir():
                    cwd = new_path
                else:
                    print(f"{R}❌ Error: '{target}' bukan direktori atau tidak ditemukan.{W}")
            except Exception as e:
                print(f"{R}❌ Error CD: {e}{W}")
            input(f"{PROMPT_COLOR}Tekan ENTER untuk melanjutkan...{W}")
            continue

        # Perintah yang memerlukan target (idx atau nama)
        selected_item = None
        if target:
            # 1. Coba sebagai Index
            try:
                idx = int(target)
                if 1 <= idx <= len(items):
                    selected_item = items[idx - 1]
            except ValueError:
                # 2. Coba sebagai Nama/Relative Path
                p = cwd / target
                if p.exists():
                    selected_item = (0, target, '', '', '', p, '') # Format dummy
            
        if not selected_item and action in ('p', 'd', 'z', 'un'):
            print(f"{R}❌ Target tidak valid atau tidak ditemukan.{W}")
            input(f"{PROMPT_COLOR}Tekan ENTER untuk melanjutkan...{W}")
            continue

        # Eksekusi Aksi
        path_to_act = selected_item[5] if selected_item else (cwd / target)
        
        if action == "p":
            if path_to_act.is_file():
                action_preview(path_to_act)
            elif path_to_act.is_dir():
                cwd = path_to_act # Masuk ke direktori jika preview pada folder
            else:
                print(f"{R}❌ '{path_to_act.name}' bukan file atau direktori.{W}")
                input(f"{PROMPT_COLOR}Tekan ENTER untuk melanjutkan...{W}")
                
        elif action == "d":
            action_delete(path_to_act)
            input(f"{PROMPT_COLOR}Tekan ENTER untuk melanjutkan...{W}")
            
        elif action == "z":
            action_zip_folder(cwd, path_to_act.name)
            input(f"{PROMPT_COLOR}Tekan ENTER untuk melanjutkan...{W}")
            
        elif action == "un":
            action_unzip_file(cwd, path_to_act.name)
            input(f"{PROMPT_COLOR}Tekan ENTER untuk melanjutkan...{W}")
            
        elif action in ("c", "copy"):
            action_copy_move(cwd, 'copy')
            input(f"{PROMPT_COLOR}Tekan ENTER untuk melanjutkan...{W}")
            
        elif action in ("m", "move"):
            action_copy_move(cwd, 'move')
            input(f"{PROMPT_COLOR}Tekan ENTER untuk melanjutkan...{W}")
            
        else:
            print(f"{R}❌ Perintah tidak dikenal: {action}{W}")
            input(f"{PROMPT_COLOR}Tekan ENTER untuk melanjutkan...{W}")
            
if __name__ == "__main__":
    main()