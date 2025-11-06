#!/data/data/com.termux/files/usr/bin/env python3
# EraldForge - File Commander v5.0 (Ultimate Edition)
# Versi: Modern, Canggih, Profesional, Bersih
import os, shutil, stat, zipfile, sys
from pathlib import Path

# --- Konfigurasi Awal & Tema ---
HOME = Path.home()

def setup_theme():
    """Memilih tema dan mengembalikan kode warna."""
    os.system('clear')
    t = os.environ.get("ERALDFORGE_THEME", "").lower()
    if t not in ("hacker", "clean"):
        t = input("Pilih Tema [hacker/clean] (default clean): ").strip().lower()
        t = t if t in ("hacker", "clean") else "clean"
    
    if t == "hacker":
        return { # Skema Hijau Neon
            "DIR": "\033[96m", "FILE": "\033[92m", "SIZE": "\033[36m",
            "ERR": "\033[91m", "W": "\033[0m", "Y": "\033[93m", "BOLD": "\033[1m"
        }
    else:
        return { # Skema Biru-Putih Profesional
            "DIR": "\033[34m", "FILE": "\033[97m", "SIZE": "\033[37m",
            "ERR": "\033[91m", "W": "\033[0m", "Y": "\033[93m", "BOLD": "\033[1m"
        }

COLORS = setup_theme()
R_Y = COLORS['Y']
R_W = COLORS['W']
R_BOLD = COLORS['BOLD']

# --- Banner (Kuning Neon) ---
BANNER_LINES = [
    "·························································",
    ": _____ _ _        _____            _       _           :",
    ":|  ___(_) | ___  | ____|_  ___ __ | | ___ | | ___ _ __ :",
    ":| |_  | | |/ _ \ |  _| \ \/ / '_ \| |/ _ \| |/ _ \ '__|:",
    ":|  _| | | |  __/ | |___ >  <| |_) | | (_) | |  __/ |   :",
    ":|_|   |_|_|\___| |_____/_/\_\ .__/|_|\___/|_|\___|_|   :",
    ":                            |_|                        :",
    "·························································",
]
BANNER = "\n".join([R_Y + line + R_W for line in BANNER_LINES])

# --- Kelas Utama: EraldFileCommander ---
class EraldFileCommander:
    def __init__(self):
        self.cwd = HOME
        self.history = [HOME]
        self.clipboard = None # Untuk copy/move

    def human_size(self, n):
        """Mengubah ukuran byte menjadi format yang mudah dibaca."""
        for unit in ('B', 'KB', 'MB', 'GB', 'TB'):
            if n < 1024: return f"{n:.1f} {unit}" if n < 100 else f"{n:.0f} {unit}"
            n /= 1024
        return f"{n:.1f} EB"

    def list_dir(self):
        """Mendapatkan daftar item dalam direktori saat ini."""
        p = self.cwd
        if not p.exists():
            print(f"{COLORS['ERR']}❌ Error: Direktori tidak ditemukan.{R_W}")
            self.cwd = self.history[-2] if len(self.history) > 1 else HOME
            return []
            
        items = sorted(p.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
        res = []
        for it in items:
            try:
                if it.is_dir():
                    typ = f"{COLORS['DIR']} <DIR> {R_W}"
                    size = f"{COLORS['SIZE']} - {R_W}"
                else:
                    size_bytes = it.stat().st_size
                    typ = f"{COLORS['FILE']} <FILE>{R_W}"
                    size = f"{COLORS['SIZE']}{self.human_size(size_bytes)}{R_W}"
                
                res.append((it.name, typ, size, it))
            except Exception:
                # Menangani permission error
                res.append((it.name, f"{COLORS['ERR']} [N/A] {R_W}", f"{COLORS['ERR']} [N/A] {R_W}", it))
        return res

    def display_list(self, items):
        """Menampilkan daftar item dengan format yang rapi."""
        print(f"\n{R_Y}┌{'─'*70}┐{R_W}")
        print(f"{R_Y}│ {R_BOLD}DIREKTORI:{R_W} {self.cwd}")
        print(f"{R_Y}│{'─'*70}│{R_W}")
        print(f"{R_Y}│ {R_BOLD} NO | NAMA {' ':<40}| JENIS {' ':<5}| UKURAN{R_W}")
        print(f"{R_Y}├{'─'*70}┤{R_W}")
        
        for i, (n, typ, s, _) in enumerate(items, start=1):
            # Format tampilan item
            name_disp = n[:40] + ('...' if len(n) > 40 else n)
            print(f"{R_Y}│ {R_W}{i:3} | {name_disp:<40}{typ}{s:>10}{R_W}")

        print(f"{R_Y}└{'─'*70}┘{R_W}")
        
    def preview(self, path):
        """Mencoba menampilkan konten file teks/biner."""
        try:
            print(f"\n{R_Y}┌{'─'*30} PREVIEW: {path.name} {'─'*30}┐{R_W}")
            with open(path, "rb") as f:
                data = f.read(4096)
                try: 
                    print(data.decode(errors="replace"))
                except: 
                    print(f"{COLORS['ERR']} [DATA BINARY, TIDAK DAPAT DITAMPILKAN SEPENUHNYA] {R_W}")
            print(f"{R_Y}└{'─'*70}┘{R_W}")
        except Exception as e:
            print(f"{COLORS['ERR']}❌ Error saat membuka: {e}{R_W}")

    # --- Fitur File Commander ---
    def zip_folder(self, target_name):
        src = self.cwd / target_name
        if not src.is_dir():
            print(f"{COLORS['ERR']}❌ Error: '{target_name}' bukan direktori.{R_W}"); return
            
        out_name = input("Nama file ZIP output (cth: archive.zip): ").strip()
        if not out_name.endswith('.zip'): out_name += '.zip'

        try:
            shutil.make_archive(str(self.cwd / out_name).replace('.zip', ''), 'zip', root_dir=str(src.parent), base_dir=str(src.name))
            print(f"{COLORS['FILE']}✅ ZIP Berhasil: '{out_name}' dibuat di {self.cwd}{R_W}")
        except Exception as e:
            print(f"{COLORS['ERR']}❌ Error saat ZIP: {e}{R_W}")

    def unzip_file(self, target_name):
        src = self.cwd / target_name
        if not src.is_file() or not src.suffix == '.zip':
            print(f"{COLORS['ERR']}❌ Error: '{target_name}' bukan file .zip.{R_W}"); return

        dest_dir = input("Nama folder tujuan ekstraksi (kosong untuk di sini): ").strip()
        dest_path = self.cwd / dest_dir if dest_dir else self.cwd / src.stem

        try:
            with zipfile.ZipFile(src, 'r') as zip_ref:
                zip_ref.extractall(dest_path)
            print(f"{COLORS['FILE']}✅ UNZIP Berhasil: Diekstrak ke {dest_path}{R_W}")
        except Exception as e:
            print(f"{COLORS['ERR']}❌ Error saat UNZIP: {e}{R_W}")
    
    def copy_item(self, target_name):
        src = self.cwd / target_name
        if not src.exists():
            print(f"{COLORS['ERR']}❌ Error: '{target_name}' tidak ditemukan.{R_W}"); return
        self.clipboard = {'path': src, 'action': 'copy'}
        print(f"{COLORS['FILE']}✅ '{target_name}' disalin ke clipboard internal. Gunakan 'paste'.{R_W}")

    def move_item(self, target_name):
        src = self.cwd / target_name
        if not src.exists():
            print(f"{COLORS['ERR']}❌ Error: '{target_name}' tidak ditemukan.{R_W}"); return
        self.clipboard = {'path': src, 'action': 'move'}
        print(f"{COLORS['FILE']}✅ '{target_name}' disiapkan untuk dipindahkan (cut). Gunakan 'paste'.{R_W}")

    def paste_item(self):
        if not self.clipboard:
            print(f"{COLORS['ERR']}❌ Error: Clipboard kosong. Gunakan 'copy' atau 'move' dulu.{R_W}"); return
        
        src_path = self.clipboard['path']
        action = self.clipboard['action']
        dest_path = self.cwd / src_path.name

        if action == 'copy':
            try:
                if src_path.is_dir():
                    shutil.copytree(src_path, dest_path)
                else:
                    shutil.copy2(src_path, dest_path)
                print(f"{COLORS['FILE']}✅ Berhasil: '{src_path.name}' disalin ke {self.cwd}{R_W}")
            except Exception as e:
                print(f"{COLORS['ERR']}❌ Error saat menyalin: {e}{R_W}")
        
        elif action == 'move':
            try:
                shutil.move(str(src_path), str(dest_path))
                print(f"{COLORS['FILE']}✅ Berhasil: '{src_path.name}' dipindahkan ke {self.cwd}{R_W}")
            except Exception as e:
                print(f"{COLORS['ERR']}❌ Error saat memindahkan: {e}{R_W}")

        self.clipboard = None # Kosongkan setelah paste

    def delete_item(self, target_name):
        target = self.cwd / target_name
        if not target.exists():
            print(f"{COLORS['ERR']}❌ Error: '{target_name}' tidak ditemukan.{R_W}"); return
        
        confirm = input(f"{R_Y}⚠️ Yakin hapus '{target_name}' ({'folder' if target.is_dir() else 'file'})? (y/N): {R_W}").strip().lower()
        if confirm != 'y':
            print(f"{COLORS['Y']}❌ Pembatalan penghapusan.{R_W}"); return

        try:
            if target.is_dir():
                shutil.rmtree(target) # Hapus rekursif untuk folder
            else:
                os.remove(target)
            print(f"{COLORS['FILE']}✅ Berhasil: '{target_name}' dihapus.{R_W}")
        except Exception as e:
            print(f"{COLORS['ERR']}❌ Error saat menghapus: {e}{R_W}")

    def mkdir(self, target_name):
        target = self.cwd / target_name
        try:
            target.mkdir(exist_ok=True)
            print(f"{COLORS['FILE']}✅ Berhasil: Folder '{target_name}' dibuat.{R_W}")
        except Exception as e:
            print(f"{COLORS['ERR']}❌ Error saat membuat folder: {e}{R_W}")

    def main_loop(self):
        os.system('clear')
        print(BANNER)
        print(f"{R_Y}{R_BOLD}EraldForge File Commander v5.0 | {R_W}{COLORS['DIR']}Mode Profesional{R_W}")

        while True:
            items = self.list_dir()
            self.display_list(items)
            
            # Tampilan clipboard status
            cb_status = f"Clipboard: {'(Kosong)' if not self.clipboard else f'({self.clipboard["action"].upper()}: {self.clipboard["path"].name})'}"
            print(f"{R_Y}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{R_W}")
            print(f"{R_BOLD}NAVIGASI: {R_W} u=up | [No.]=open/cd | [Nama]=cd | q=quit")
            print(f"{R_BOLD}AKSI:     {R_W} c=copy | m=move | v=paste | z=zip | x=unzip | d=delete | k=mkdir | p=preview")
            print(f"{R_Y}Status: {cb_status}{R_W}")
            print(f"{R_Y}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{R_W}")
            
            cmd = input(f"{COLORS['FILE']}{R_BOLD}Commander > {R_W}").strip()
            if not cmd: continue

            # --- Command Handling ---
            if cmd in ("q", "quit"): break
            
            if cmd == "u": 
                self.cwd = self.cwd.parent
                if self.cwd not in self.history: self.history.append(self.cwd)
                continue
            
            elif cmd == "z": # Zip Folder
                name = input("Nama Folder yang di-ZIP: ").strip()
                if name: self.zip_folder(name)
                continue
                
            elif cmd == "x": # Unzip File (Fitur Baru)
                name = input("Nama File .zip yang di-UNZIP: ").strip()
                if name: self.unzip_file(name)
                continue
            
            elif cmd == "c": # Copy
                name = input("Nama item untuk di-COPY: ").strip()
                if name: self.copy_item(name)
                continue
            
            elif cmd == "m": # Move (Cut)
                name = input("Nama item untuk di-MOVE (cut): ").strip()
                if name: self.move_item(name)
                continue
            
            elif cmd == "v": # Paste
                self.paste_item(); continue

            elif cmd == "d": # Delete (Fitur Baru)
                name = input("Nama item untuk di-DELETE: ").strip()
                if name: self.delete_item(name)
                continue
            
            elif cmd == "k": # Mkdir (Fitur Baru)
                name = input("Nama Folder Baru: ").strip()
                if name: self.mkdir(name)
                continue

            elif cmd == "p": # Preview
                target = input("Nama File untuk di-PREVIEW: ").strip()
                t = self.cwd / target
                if t.exists() and t.is_file(): 
                    self.preview(t)
                    input(f"{R_Y}Tekan ENTER untuk lanjut...{R_W}")
                else: 
                    print(f"{COLORS['ERR']}❌ File tidak ditemukan atau itu folder.{R_W}")
                continue

            # --- Pilihan Numerik atau Navigasi Langsung ---
            try:
                idx = int(cmd) - 1
                if 0 <= idx < len(items):
                    entry = items[idx][3]
                    if entry.is_dir():
                        self.cwd = entry
                        if self.cwd not in self.history: self.history.append(self.cwd)
                    else:
                        self.preview(entry)
                        input(f"{R_Y}Tekan ENTER untuk lanjut...{R_W}")
                else:
                    print(f"{COLORS['ERR']}❌ Pilihan tidak valid.{R_W}")
            except ValueError:
                # Navigasi berdasarkan nama
                p = self.cwd / cmd
                if p.exists():
                    if p.is_dir():
                        self.cwd = p
                        if self.cwd not in self.history: self.history.append(self.cwd)
                    else:
                        self.preview(p)
                        input(f"{R_Y}Tekan ENTER untuk lanjut...{R_W}")
                else:
                    print(f"{COLORS['ERR']}❌ Item '{cmd}' tidak ditemukan.{R_W}")

if __name__ == "__main__":
    try:
        commander = EraldFileCommander()
        commander.main_loop()
    except Exception as e:
        print(f"{COLORS['ERR']}🔥 CRITICAL ERROR: {e}{R_W}")