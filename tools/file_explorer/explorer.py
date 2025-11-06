#!/data/data/com.termux/files/usr/bin/env python3
# EraldForge File Explorer v6.1 - Advanced Terminal File Explorer
# Peningkatan: Menu 3 Kolom Modern, Fitur Mkdir & Touch.

import os, shutil, stat, zipfile
from pathlib import Path
from datetime import datetime
import textwrap

# --- Konfigurasi Dasar & Lokasi ---
HOME = Path.home()
VERSION = "6.1" # Versi ditingkatkan
APP_NAME = "EraldForge File Explorer"

# --- Definisi Warna & Gaya ---
# Warna untuk "Pro" Theme (Default: Biru/Cyan)
C_PRO_DIR = "\033[96m"    # Cyan untuk Direktori
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

# --- Fungsi Banner ASCII (Neon) ---
def get_banner(show_info=True, theme_name="pro", prompt_color=C_PRO_PROMPT, dir_color=C_PRO_DIR, time_color=C_PRO_TIME):
    """Mencetak banner ASCII sesuai permintaan dengan warna Neon dan info tema."""
    ASCII_LINES = [
        f"{Y}·························································{W}",
        f"{Y}: {BOLD}_____ _ _        _____            _                     :{W}",
        f"{Y}:|  ___(_) | ___  | ____|_  ___ __ | | ___  _ __ ___ _ __ :{W}",
        f"{Y}:| |_  | | |/ _ \ |  _| \ \/ / '_ \| |/ _ \| '__/ _ \ '__|:{W}",
        f"{Y}:|  _| | | |  __/ | |___ >  <| |_) | | (_) | | |  __/ |   :{W}",
        f"{Y}:|_|   |_|_|\___| |_____/_/\_\ .__/|_|\___/|_|  \___|_|   :{W}",
        f"{Y}:                            |_|                          :{W}",
        f"{Y}·························································{W}",
    ]
    
    output = "\n".join(ASCII_LINES)
    
    if show_info:
        info_line = (
            f"\n{BOLD}{prompt_color}:: {APP_NAME} v{VERSION}{W} | "
            f"{dir_color}Theme: {theme_name.capitalize()}{W} | "
            f"{time_color}Time: {datetime.now().strftime('%H:%M:%S')}{W}\n"
        )
        output += info_line
    
    return output

# --- Manajemen Tema (Ditingkatkan & Diperbaiki) ---
def get_theme_choice():
    """Meminta pilihan tema saat inisialisasi."""
    os.system('clear')
    
    # Tampilkan banner awal dengan warna default, karena tema belum dipilih
    print(get_banner(show_info=False, prompt_color=C_PRO_PROMPT, dir_color=C_PRO_DIR, time_color=C_PRO_TIME)) 
    
    print(f"{BOLD}{Y}:: KONFIGURASI TEMA ::{W}")
    t = os.environ.get("ERALDFORGE_THEME", "").lower()
    if t in ("hacker", "pro"): return t
    
    t = input(f"{Y}Pilih Tema [{C_PRO_PROMPT}pro{W}/{C_HACK_PROMPT}hacker{W}] (default pro) > {W}").strip().lower()
    return t if t in ("hacker", "pro") else "pro"

# --- Inisialisasi Tema (Penting: harus dilakukan sebelum main) ---
THEME_NAME = get_theme_choice()

if THEME_NAME == "hacker":
    DIR_COLOR, FILE_COLOR, SIZE_COLOR, TIME_COLOR, PROMPT_COLOR = C_HACK_DIR, C_HACK_FILE, C_HACK_SIZE, C_HACK_TIME, C_HACK_PROMPT
else:
    DIR_COLOR, FILE_COLOR, SIZE_COLOR, TIME_COLOR, PROMPT_COLOR = C_PRO_DIR, C_PRO_FILE, C_PRO_SIZE, C_PRO_TIME, C_PRO_PROMPT

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
        perm = ('d' if stat.S_ISDIR(s) else '-')
        perm += stat.filemode(s)[1:4] 
        return perm
    except:
        return '????'

def list_dir(p):
    """Mendaftar isi direktori dengan detail."""
    p = Path(p).expanduser().resolve()
    if not p.is_dir(): return []
    
    items = [(p.parent, "..")] if p != Path('/') else []
    
    try:
        items.extend([(it, it.name) for it in p.iterdir()])
        items = sorted(items, key=lambda x: (not x[0].is_dir() if x[1] != '..' else False, x[1].lower()))
    except Exception as e:
        print(f"{R}ERROR: Gagal membaca direktori: {e}{W}")
        return []
    
    res = []
    start_index = 1 if items and items[0][1] == ".." else 1
    
    for i, (path_obj, name) in enumerate(items, start=start_index):
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

# --- Fitur File Manager (Fungsi Baru/Ditingkatkan) ---

def action_preview(path: Path):
    """Menampilkan isi file (4KB pertama)."""
    os.system('clear')
    print(get_banner(theme_name=THEME_NAME, prompt_color=PROMPT_COLOR, dir_color=DIR_COLOR, time_color=TIME_COLOR))
    print(f"{BOLD}{PROMPT_COLOR}:: PREVIEW FILE: {path.name} ::{W}")
    print(f"{'='*50}\n")
    try:
        with open(path, "rb") as f:
            data = f.read(4096)
            try: 
                print(data.decode(errors="replace"))
            except UnicodeDecodeError: 
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
        # shutil.make_archive menangani ZIP folder/direktori dengan baik
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
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dst)
            print(f"{PROMPT_COLOR}✅ Berhasil: Disalin dari '{src_name}' ke '{dst_name}'{W}")
        elif action == 'move':
            shutil.move(str(src), str(dst))
            print(f"{PROMPT_COLOR}✅ Berhasil: Dipindahkan dari '{src_name}' ke '{dst_name}'{W}")
    except Exception as e:
        print(f"{R}❌ Error saat {action}: {e}{W}")

def action_mkdir(cwd: Path, dir_name: str):
    """Membuat direktori baru (mk)."""
    new_dir = cwd / dir_name
    if not dir_name:
        print(f"{R}❌ Error: Nama direktori harus diberikan.{W}")
        return
    if new_dir.exists():
        print(f"{R}❌ Error: Direktori '{dir_name}' sudah ada.{W}")
        return
    try:
        new_dir.mkdir(parents=True, exist_ok=False)
        print(f"{PROMPT_COLOR}✅ Berhasil: Direktori '{dir_name}' dibuat.{W}")
    except Exception as e:
        print(f"{R}❌ Error membuat direktori: {e}{W}")
        
def action_touch(cwd: Path, file_name: str):
    """Membuat file kosong baru (touch)."""
    new_file = cwd / file_name
    if not file_name:
        print(f"{R}❌ Error: Nama file harus diberikan.{W}")
        return
    if new_file.exists():
        print(f"{R}❌ Error: File '{file_name}' sudah ada.{W}")
        return
    try:
        new_file.touch()
        print(f"{PROMPT_COLOR}✅ Berhasil: File kosong '{file_name}' dibuat.{W}")
    except Exception as e:
        print(f"{R}❌ Error membuat file: {e}{W}")


# --- Loop Utama Program ---
def main():
    def get_target_from_list(target_str, item_list, current_dir):
        # 1. Coba sebagai Index
        try:
            idx = int(target_str)
            if 1 <= idx <= len(item_list):
                return item_list[idx - 1] 
        except ValueError:
            pass
        
        # 2. Coba sebagai Nama/Relative Path
        p = current_dir / target_str
        if p.exists():
            for item in item_list:
                if item[1] == target_str:
                    return item
            return (0, target_str, '', '', '', p, '')
        return None

    os.system('clear')
    cwd = HOME
    
    while True:
        os.system('clear')
        print(get_banner(theme_name=THEME_NAME, prompt_color=PROMPT_COLOR, dir_color=DIR_COLOR, time_color=TIME_COLOR))
        
        print(f"{BOLD}{DIR_COLOR}:: PWD: {W}{cwd.resolve()}")
        term_width = os.get_terminal_size().columns if os.get_terminal_size().columns < 80 else 80
        print("-" * term_width)
        
        items = list_dir(cwd)

        # Tampilkan Daftar File/Folder
        for i, name, size, mtime, perm, path_obj, color in items:
            size_fmt = f"{SIZE_COLOR}{size:>10}{W}"
            mtime_fmt = f"{TIME_COLOR}{mtime:<16}{W}"
            perm_fmt = f"{DIR_COLOR}{perm:<5}{W}"
            index_display = f"{Y}UP{W}" if name == ".." else f"{PROMPT_COLOR}{i:02}{W}"

            print(f"[{index_display}] {perm_fmt} {size_fmt} {mtime_fmt} {color}{name}{W}")
        
        print("-" * term_width)
        
        ## --- MENU PERINTAH CANGGIH (Rapi, Sejajar, Profesional) ---
        print(f"{BOLD}{PROMPT_COLOR}:: MENU KOMANDO ::{W}")
        
        # Susunan Menu 3 Kolom sesuai permintaan
        menu_items = [
            # Baris 1: Navigasi
            (f"{Y}u{W}=Up",              f"| {Y}cd <dir>{W}=Change Dir",  f"| {Y}ls{W}=Refresh/List"), 
            # Baris 2: Dasar File Ops
            (f"| {Y}q{W}=Quit",          f"| {Y}p <tgt>{W}=Preview",     f"| {Y}d <tgt>{W}=Delete (Rec.)"),
            # Baris 3: Copy/Move/Zip
            (f"| {Y}c{W}=Copy",          f"| {Y}m{W}=Move",             f"| {Y}z <tgt>{W}=Zip"),
            # Baris 4: Unzip/Create
            (f"| {Y}un <tgt>{W}=Unzip",   f"| {Y}mk <name>{W}=Mkdir",     f"| {Y}touch <name>{W}=Touch File"),
            # Baris 5: Find (Placeholder)
            (f"| {Y}f <name>{W}=Find (TODO)", "",                        ""),
        ]

        # Padding yang Ditingkatkan untuk kerapian (Lebar disesuaikan)
        col1_width = 13 # u=Up | q=Quit | c=Copy | un <tgt>
        col2_width = 20 # cd <dir> | p <tgt> | m=Move | mk <name>
        col3_width = 24 # ls=Refresh | d <tgt> | z <tgt> | touch <name>
        
        for line in menu_items:
            # Pastikan line memiliki 3 elemen, jika kurang tambahkan string kosong
            line = list(line) + [''] * (3 - len(line))
            
            col1, col2, col3 = line
            
            # Cetak baris dengan padding rata kiri (<)
            print(
                f"  {col1:<{col1_width}} {col2:<{col2_width}} {col3:<{col3_width}}",
                sep='',
                end='\n'
            )
        
        print("-" * term_width)

        command = input(f"{PROMPT_COLOR}CMD > {W}").strip()
        cmd_parts = command.split(' ', 1)
        action = cmd_parts[0].lower()
        target = cmd_parts[1].strip() if len(cmd_parts) > 1 else ""

        # --- Aksi Navigasi & Utility ---
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
            continue 

        elif action in ("cd", "chdir"):
            try:
                new_path = Path(target).expanduser()
                if not new_path.is_absolute():
                    new_path = cwd / target
                
                selected_item_cd = get_target_from_list(target, items, cwd)
                if selected_item_cd:
                    new_path = selected_item_cd[5]
                
                if new_path.is_dir():
                    cwd = new_path.resolve()
                else:
                    print(f"{R}❌ Error: '{target}' bukan direktori atau tidak ditemukan.{W}")
            except Exception as e:
                print(f"{R}❌ Error CD: {e}{W}")
            input(f"{PROMPT_COLOR}Tekan ENTER untuk melanjutkan...{W}")
            continue
        
        elif action in ("mk", "mkdir"):
            action_mkdir(cwd, target)
            input(f"{PROMPT_COLOR}Tekan ENTER untuk melanjutkan...{W}")
            continue
            
        elif action in ("touch"):
            action_touch(cwd, target)
            input(f"{PROMPT_COLOR}Tekan ENTER untuk melanjutkan...{W}")
            continue
            
        elif action == "f": # Placeholder for Find action
            print(f"{Y}Fitur 'Find' akan segera diimplementasikan (TODO).{W}")
            input(f"{PROMPT_COLOR}Tekan ENTER untuk melanjutkan...{W}")
            continue

        # --- Aksi dengan Target (File/Folder: p, d, z, un) ---
        selected_item = get_target_from_list(target, items, cwd)

        if not selected_item and action in ('p', 'd', 'z', 'un'):
            print(f"{R}❌ Target tidak valid atau tidak ditemukan.{W}")
            input(f"{PROMPT_COLOR}Tekan ENTER untuk melanjutkan...{W}")
            continue

        path_to_act = selected_item[5] if selected_item else None
        
        if action == "p":
            if path_to_act and path_to_act.is_file():
                action_preview(path_to_act)
            elif path_to_act and path_to_act.is_dir() and selected_item[1] != '..':
                cwd = path_to_act.resolve() 
            else:
                print(f"{R}❌ Target bukan file.{W}")
                input(f"{PROMPT_COLOR}Tekan ENTER untuk melanjutkan...{W}")
                
        elif action == "d":
            if path_to_act and selected_item[1] != '..':
                action_delete(path_to_act)
            else:
                print(f"{R}❌ Tidak bisa menghapus direktori parent (..).{W}")
            input(f"{PROMPT_COLOR}Tekan ENTER untuk melanjutkan...{W}")
            
        elif action == "z":
            if path_to_act and path_to_act.is_dir():
                action_zip_folder(cwd, path_to_act.name)
            else:
                print(f"{R}❌ Target bukan folder untuk di-ZIP.{W}")
            input(f"{PROMPT_COLOR}Tekan ENTER untuk melanjutkan...{W}")
            
        elif action == "un":
            if path_to_act and path_to_act.is_file() and path_to_act.suffix.lower() == '.zip':
                action_unzip_file(cwd, path_to_act.name)
            else:
                print(f"{R}❌ Target bukan file .zip.{W}")
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