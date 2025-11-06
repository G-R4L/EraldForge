#!/data/data/com.termux/files/usr/bin/env python3
""" EraldForge v2.3 — Launcher final (ID-only)
By Gerald (G-R4L) 
"""
import os
import sys
import json
import subprocess
import socket
import time
import platform
import textwrap
import shutil
from pathlib import Path
from datetime import datetime, timedelta

try:
    import psutil
except Exception:
    psutil = None

# ---------------- paths / config ----------------
BASE = Path(__file__).resolve().parent
TOOLS_DIR = BASE / "tools"
CONSENT_LOG = Path.home() / ".eraldforge_consent.log"
VERSION = "2.3"
ERALD_LANG = "id"

# ---------------- color palette ----------------
THEMES = {
    # Default: 'title' adalah Biru (\033[34m). 'desc' adalah Putih (\033[37m). 'time' adalah Magenta Terang (\033[95m)
    "default": {"num":"\033[36m","title":"\033[34m","desc":"\033[37m","accent":"\033[33m","reset":"\033[0m","bold":"\033[1m", "time":"\033[95m"},
    "matrix": {"num":"\033[32m","title":"\033[32m","desc":"\033[37m","accent":"\033[92m","reset":"\033[0m","bold":"\033[1m", "time":"\033[95m"},
    "cyberpunk":{"num":"\033[95m","title":"\033[96m","desc":"\033[37m","accent":"\033[93m","reset":"\033[0m","bold":"\033[1m", "time":"\033[95m"},
    "solarized":{"num":"\033[33m","title":"\033[36m","desc":"\033[37m","accent":"\033[32m","reset":"\033[0m","bold":"\033[1m", "time":"\033[95m"}
}
CURRENT_THEME = "default"
C = THEMES[CURRENT_THEME]

# ---------------- Banner ASCII ----------------
# Banner baru yang sudah dirapikan
BANNER_LINES = [
    " ____                 ___        __ ____        ",
    "/\\  _`\\              /\\_ \\      /\\ \\/\\  _`\\     ",
    "\\ \\ \\L\\_\\ _ __    __  \\//\\ \\    \\_\\ \\ \\ \\L\\_\\___  _ __    __  ",
    " \\ \ _\\L /\\`'__\\/'__`\\  \ \ \  /'_` \ \  _\\/ __`\\/\\`'__\\/'_ `\\ /'__`\\ ",
    "  \ \ \L\ \ \ \//\ \L\.\_ \_\ \_/\ \L\ \ \ \/\ \L\ \ \ \//\ \L\ \/\  __/",
    "   \ \____/\ \_\\ \__/.\_\/\____\\ \___,_\ \_\ \____/\ \_\\ \____ \ \____\\",
    "    \/___/  \/_/ \/__/\/_/\/____/\/__,_ /\/_/\/___/  \/_/ \/___L\ \/____/",
    "                                                          /\\____/  ",
    "                                                          \\/_/__/   "
]

def colored_banner():
    """Mencetak banner dengan warna."""
    out = []
    for i, ln in enumerate(BANNER_LINES):
        # Mempertahankan skema warna sebelumnya (Merah untuk baris atas, Biru untuk baris bawah)
        if i <= 4:
            out.append("\033[31m" + ln + C["reset"])
        else:
            out.append("\033[34m" + ln + C["reset"])
    return "\n".join(out)

# ---------------- Menu ----------------
MENU_LIST = [
    ("calculator", "Kalkulator interaktif"),
    ("clipboard", "Clipboard history (termux-api)"),
    ("file_explorer", "Jelajahi filesystem & zip/unzip"),
    ("port_scanner", "Pemindai port (wrapper nmap)"),
    ("todo", "Todo list (local JSON)"),
    ("wifi_info", "Info Wi‑Fi (readonly)"),
    ("password_generator", "Generator password aman"),
    ("qrcode_generator", "Buat QR (simpan PNG)")
]

# ---------------- UI strings ----------------
S = {
    "tag": "✦ Ethical • Modular • Termux-Native ✦",
    "menu_title": "EraldForge Main Menu",
    "prompt": "Pilih nomor atau huruf: ",
    "update_ok": "✔ Update selesai!",
    "update_none": "Tidak ada update baru.",
    "consent_title": "=== Persetujuan wajib untuk fitur keamanan ===",
    "consent_prompt": "Ketik 'yes' untuk melanjutkan: ",
    "consent_denied": "Dibatalkan oleh pengguna.",
    "press": "Tekan Enter untuk kembali...",
    "invalid": "Pilihan tidak valid."
}

# ---------------- Helpers ----------------
def clear():
    """Membersihkan terminal."""
    os.system("clear" if os.name != "nt" else "cls")

def term_width(default=80):
    """Mendapatkan lebar terminal yang aman."""
    try:
        w = shutil.get_terminal_size().columns
        return max(60, w)
    except Exception:
        return default

def shorten(s, width):
    """Memotong string dengan elipsis."""
    try:
        return textwrap.shorten(s, width=width, placeholder="...")
    except Exception:
        return (s[:width-3] + "...") if len(s)>width else s

def pause(msg=None):
    """Menunggu input Enter dari pengguna."""
    if msg is None:
        msg = S["press"]
    try:
        input(msg)
    except Exception:
        pass

def save_consent(action, target=None):
    """Mencatat persetujuan fitur keamanan."""
    try:
        with open(CONSENT_LOG, "a") as f:
            f.write(f"{datetime.utcnow().isoformat()} | {action} | target={target}\n")
    except Exception:
        pass

def run_python_with_lang(script_path, extra_env=None):
    """Menjalankan skrip Python dengan variabel lingkungan bahasa."""
    env = os.environ.copy()
    env["ERALDFORGE_LANG"] = ERALD_LANG
    if extra_env:
        env.update(extra_env)
    return subprocess.run([sys.executable, str(script_path)], env=env)

def run_tool_dir(tool_dir):
    """Mencari dan menjalankan script entry point di direktori tool."""
    meta = tool_dir / "meta.json"
    entry = None
    if meta.exists():
        try:
            j = json.loads(meta.read_text())
            entry = j.get("entry")
        except Exception:
            pass
    
    if not entry:
        candidates = ("main.py", "run.py", "start.py", f"{tool_dir.name}.py")
        for c in candidates:
            if (tool_dir / c).exists():
                entry = c
                break
    
    if not entry:
        return False
    
    p = tool_dir / entry
    if not p.exists():
        return False
    
    if p.suffix == ".py":
        run_python_with_lang(p)
    else:
        subprocess.run([str(p)])
    return True

# ---------------- Fallbacks ----------------
def fallback_calculator():
    clear()
    print("== Kalkulator fallback ==")
    expr = input("Masukkan ekspresi: ").strip()
    if not expr: pause(); return
    import math
    SAFE = {"__builtins__": None}
    SAFE.update({k: getattr(math, k) for k in dir(math) if not k.startswith("_")})
    SAFE.update({"abs": abs, "round": round, "pow": pow})
    try:
        print("Hasil:", eval(expr, SAFE, {}))
    except Exception as e:
        print("Error:", e)
    pause()

def fallback_clipboard():
    clear()
    print("== Clipboard fallback ==")
    try:
        out = subprocess.check_output(["termux-clipboard-get"], stderr=subprocess.DEVNULL).decode(errors="ignore")
        print(out[:1000])
    except Exception:
        print("termux-api tidak tersedia.")
    pause()

def fallback_file_explorer():
    clear()
    print("== File Explorer fallback ==")
    cwd = Path.home()
    while True:
        print("\nCurrent:", cwd)
        try:
            items = sorted(cwd.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
        except Exception as e:
            print(e); pause(); return
        
        # Tampilkan maksimal 200 item
        for i, it in enumerate(items[:200], start=1):
            name = it.name + ("/" if it.is_dir() else "")
            print(f"{i}. {name}")
        
        print("u. up, q. quit")
        ch = input("Choice: ").strip().lower()
        
        if ch == "q":
            break
        if ch == "u":
            cwd = cwd.parent; continue
        
        try:
            ix = int(ch) - 1
            it = items[ix]
            if it.is_dir():
                cwd = it
            else:
                # Tampilkan 4096 bytes pertama dari file teks
                print(it.open("r", errors="replace").read(4096))
        except Exception:
            print("Pilihan tidak valid.")
        pause()

def fallback_portscanner():
    clear()
    print("== Port Scanner fallback ==")
    tgt = input("Target: ").strip()
    if not tgt: pause(); return
    rng = input("Range (mis. 1-1024): ").strip() or "1-1024"
    
    try:
        a,b = map(int, rng.split("-"))
    except Exception:
        a,b = 1,1024
    
    open_ports = []
    for p in range(a,b+1):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.35)
            if s.connect_ex((tgt,p)) == 0:
                open_ports.append(p)
            s.close()
        except KeyboardInterrupt:
            break
        except Exception:
            pass
    
    print("Open ports:", ", ".join(map(str,open_ports)) if open_ports else "Tidak ditemukan")
    pause()

def fallback_todo():
    TF = Path.home() / ".eraldforge_todo.json"
    def load():
        try:
            return json.loads(TF.read_text())
        except Exception:
            return []
    def save(x):
        try:
            TF.write_text(json.dumps(x, indent=2))
        except Exception:
            pass
            
    while True:
        clear()
        items = load()
        for i,it in enumerate(items):
            print(f"{i}. [{'x' if it.get('done') else ' '}] {it.get('task')}")
        
        print("a add, t toggle, d del, q quit")
        c = input("Pilihan: ").strip().lower()
        
        if c=="q": break
        if c=="a":
            t=input("Task: ").strip()
            if t: items.append({"task":t,"done":False}); save(items)
        elif c=="t":
            try:
                ix=int(input("Index:")); items[ix]['done']=not items[ix].get('done',False); save(items)
            except: 
                print("Invalid index")
        elif c=="d":
            try:
                ix=int(input("Index:")); items.pop(ix); save(items)
            except:
                print("Invalid index")
        pause()

def fallback_wifi_info():
    clear()
    print("== Wi-Fi Info fallback ==")
    try:
        out=subprocess.check_output(["termux-wifi-scaninfo"], stderr=subprocess.DEVNULL).decode(errors="ignore")
        print(out)
    except Exception:
        print("termux-api tidak tersedia.")
    pause()

def builtin_password_generator():
    clear()
    print("=== Password Generator ===")
    try:
        n=int(input("Length [16]: ").strip() or "16")
    except Exception:
        n=16
    
    import secrets,string
    chars = string.ascii_letters+string.digits+"!@#$%^&*()-_=+"
    pw="".join(secrets.choice(chars) for _ in range(n))
    print(pw)
    
    try:
        subprocess.run(["termux-clipboard-set", pw], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); print("(Tersalin ke clipboard)")
    except Exception:
        pass
    pause()

def builtin_qrcode():
    clear()
    print("=== QR Code Generator ===")
    txt = input("Text/URL: ").strip()
    if not txt: pause(); return
    
    try:
        import qrcode
        img = qrcode.make(txt)
        fname = BASE / f"qrcode_{int(time.time())}.png"
        img.save(str(fname))
        print("QR disimpan:", fname)
    except Exception:
        print("Library qrcode tidak tersedia."); print(txt)
    pause()

# ---------------- System Monitor (versi minimal untuk Termux) ----------------
def system_monitor():
    """Menampilkan informasi sistem yang paling mungkin berhasil di Termux non-root."""
    clear()
    print("==== System Monitor ====")
    
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Waktu: {now}")
    
    # Uptime
    uptime_str = "N/A"
    try:
        if psutil:
            uptime_sec = time.time() - psutil.boot_time()
            uptime_str = str(timedelta(seconds=int(uptime_sec)))
    except Exception:
        pass
    print(f"Uptime: {uptime_str}\n")
    
    # CPU (Hanya tampilkan info yang paling aman)
    print("CPU:")
    cpu_logical = "N/A"
    try:
        if psutil:
            # psutil.cpu_count(logical=True) biasanya aman
            cpu_logical = psutil.cpu_count(logical=True)
            print(f" - Jumlah core logical : {cpu_logical}")
        else:
            print(" - psutil tidak tersedia.")
        # Menghapus: Load average, CPU usage total, CPU per-core, Top Processes
        print(" - Metrik Usage/Load diblokir oleh sistem Android.\n")
    except Exception:
        print(" - Info CPU tidak tersedia\n")

    # Memory
    print("Memori:")
    try:
        if psutil:
            mem=psutil.virtual_memory(); swap=psutil.swap_memory()
            print(f" - Total RAM: {round(mem.total/1024**3,1)} GiB")
            print(f" - Used: {round(mem.used/1024**3,1)} GiB")
            print(f" - Free: {round(mem.free/1024**3,1)} GiB")
            print(f" - Available: {round(mem.available/1024**3,1)} GiB")
            print(f" - Swap total: {round(swap.total/1024**2,1)} MiB")
            print(f" - Swap used: {round(swap.used/1024**2,1)} MiB\n")
        else:
            print(" - Info RAM/SWAP tidak tersedia (psutil tidak tersedia)\n")
    except Exception:
        print(" - Info RAM/SWAP tidak tersedia\n")

    # Disk
    print("Disk (/):")
    try:
        if psutil:
            disk=psutil.disk_usage("/")
            print(f" - Total: {round(disk.total/1024**3,1)} GiB")
            print(f" - Used: {round(disk.used/1024**3,1)} GiB")
            print(f" - Free: {round(disk.free/1024**3,1)} GiB")
            print(f" - Usage: {disk.percent}%\n")
        else:
            print(" - Info Disk tidak tersedia (psutil tidak tersedia)\n")
    except Exception:
        print(" - Info Disk tidak tersedia\n")
    
    # Network
    print("Network:")
    try:
        if psutil:
            net_if=psutil.net_if_addrs()
            net_io=psutil.net_io_counters(pernic=True)
            
            found_net = False
            for iface, addrs in net_if.items():
                # Cari alamat IPv4
                ip_addr=[a.address for a in addrs if a.family.name=="AF_INET"]
                if not ip_addr:
                    continue
                
                # Cek data I/O
                io_stats = net_io.get(iface)
                if io_stats:
                    tx=round(io_stats.bytes_sent/1024**3,2)
                    rx=round(io_stats.bytes_recv/1024**3,2)
                    print(f" - Interface: {iface} IP: {ip_addr[0]} Sent: {tx} GiB Recv: {rx} GiB")
                    found_net = True
            
            if not found_net:
                    print(" - Tidak ada interface network yang aktif (IPv4)")
        else:
            print(" - Info network tidak tersedia (psutil tidak tersedia)\n")
    except Exception:
        print(" - Info network tidak tersedia\n")
        
    pause()


# ---------------- UI ----------------
def show_menu():
    """Menampilkan menu utama dengan layout yang rapi."""
    global C # Memastikan C diperbarui setelah ganti tema
    
    clear()
    
    # Banner
    print(colored_banner())

    # PERBAIKAN: Hitung padding untuk menengahkan tagline
    width = term_width()
    tag = S["tag"]
    # Menghitung padding, diasumsikan width cukup besar
    # (width - len(tag)) / 2
    padding = " " * ((width - len(tag)) // 2)
    
    print(padding + C["title"] + S["tag"] + C["reset"])
    print(C["accent"] + "══════════════════════════════════════════════════════════" + C["reset"])
    
    now = datetime.now().strftime("%H:%M:%S")
    # Menggunakan C['time'] untuk warna jam
    print(f"{C['time']}🕒 [{now}]{C['reset']} {C['title']}{S['menu_title']}{C['reset']}")
    print(C["accent"] + "──────────────────────────────────────────────" + C["reset"]) # Garis pemisah sebelum menu utama

    # Lebar terminal & kolom
    num_col = 4 # "[1] "
    name_col = 24 # Nama tool
    desc_width = width - (num_col + name_col + 5) # sisa untuk deskripsi
    desc_col = max(20, desc_width)

    # Tampilkan menu tools (1-8)
    for i, (tid, default_desc) in enumerate(MENU_LIST, start=1):
        title = tid.replace("_", " ").title()
        
        # ambil deskripsi meta.json jika ada
        meta_desc = ""
        md = TOOLS_DIR / tid / "meta.json"
        if md.exists():
            try:
                j = json.loads(md.read_text())
                meta_desc = j.get("desc") or j.get("desc_id") or j.get("desc_en") or ""
            except Exception:
                meta_desc = ""
        
        desc = meta_desc or default_desc
        desc = shorten(desc, desc_col)
        
        # Menggunakan C['desc'] (PUTIH) untuk DESKRIPSI Tools 1-8
        print(f"{C['num']}[{i}]{C['reset']} {C['title']}{title:<{name_col}}{C['reset']} - {C['desc']}{desc}{C['reset']}")

    # Tampilkan menu tambahan (U, T, S, A, 0)
    print(C["accent"] + "──────────────────────────────────────────────" + C["reset"])
    extras = [
        ("U", "Update GitHub", "tarik update dari repo"),
        ("T", "Tema", "ganti tema"),
        ("S", "System Monitor", "info lengkap sistem"),
        ("A", "Tentang EraldForge", "info versi & author"),
        ("0", "Keluar", "tutup program")
    ]
    
    # Menggunakan C['desc'] (PUTIH) untuk DESKRIPSI Menu Tambahan
    for code, title, desc in extras:
        print(f"{C['num']}[{code}]{C['reset']} {C['title']}{title:<{name_col}}{C['reset']} - {C['desc']}{desc}{C['reset']}")

    print(C["accent"] + "══════════════════════════════════════════════════════════" + C["reset"])
    print(S["prompt"], end="")

def theme_menu():
    """Menu untuk memilih tema."""
    global CURRENT_THEME,C
    clear(); print("=== Pilih Tema ===")
    names=list(THEMES.keys())
    for i,n in enumerate(names,start=1):
        print(f"[{i}] {n}")
    print("[B] Kembali")
    
    choice=input("Pilih: ").strip().lower()
    if choice=="b": return
    
    try:
        idx=int(choice)-1
        CURRENT_THEME=names[idx]
        C=THEMES[CURRENT_THEME]
        print("Tema diganti:", CURRENT_THEME)
    except Exception:
        print("Pilihan tidak valid.")
    pause()

def about_menu():
    """Menu 'Tentang'."""
    clear()
    print(f"EraldForge {VERSION}")
    print("Pengembang : Gerald (G-R4L)")
    print("Repo : https://github.com/G-R4L/EraldForge")
    print("Tujuan : Multitool Termux, aman & ethical")
    pause()

# ---------------- Choice Handling ----------------
def handle_choice(ch):
    """Menangani pilihan menu."""
    ch=ch.strip().lower()
    if not ch: return
    
    if ch in ("0","q","exit"):
        print("Bye."); sys.exit(0)
    
    if ch=="u":
        # Check if git is available (optional)
        try:
            subprocess.run(["git","--version"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        except:
            pass
        
        try:
            # Lakukan git pull
            p=subprocess.run(["git","pull"],cwd=str(BASE))
        except: 
            p=None
        
        print(S["update_ok"] if p and p.returncode==0 else S["update_none"])
        pause(); return
    
    if ch=="t": theme_menu(); return
    if ch=="s": system_monitor(); return
    if ch=="a": about_menu(); return
    
    if ch.isdigit():
        n=int(ch)
        if 1<=n<=len(MENU_LIST):
            tid=MENU_LIST[n-1][0]
            td=TOOLS_DIR/tid
            
            # Cek metadata tool
            meta=td/"meta.json"
            security=False; desc=""
            if meta.exists():
                try:
                    j=json.loads(meta.read_text())
                    security=bool(j.get("security",False))
                    desc=j.get("desc") or j.get("desc_id") or j.get("desc_en") or ""
                except:
                    pass
            
            # Proses persetujuan keamanan jika diperlukan
            tgt=None
            if security:
                clear()
                print(S["consent_title"])
                print("Fitur ini dapat digunakan untuk tujuan etis (misalnya pada jaringan Anda sendiri).")
                print(desc or MENU_LIST[n-1][1])
                ok=input(S["consent_prompt"]).strip().lower()=="yes"
                if not ok:
                    print(S["consent_denied"]); pause(); return
                
                # Tanya target untuk tool yang sensitif
                tgt=input("Target (IP/domain) atau kosong: ").strip() or None
                save_consent(desc or tid, tgt)
            
            if tgt: 
                os.environ["ERALDFORGE_TARGET"]=tgt

            # Coba jalankan tool dari direktori
            if td.exists() and td.is_dir():
                if run_tool_dir(td):
                    return

            # Fallback jika tool dari direktori tidak ada atau gagal
            if tid=="calculator": fallback_calculator(); return
            if tid=="clipboard": fallback_clipboard(); return
            if tid=="file_explorer": fallback_file_explorer(); return
            if tid=="port_scanner": fallback_portscanner(); return
            if tid=="todo": fallback_todo(); return
            if tid=="wifi_info": fallback_wifi_info(); return
            if tid=="password_generator": builtin_password_generator(); return
            if tid=="qrcode_generator": builtin_qrcode(); return

            print("Tool tidak ditemukan dan tidak ada fallback."); pause(); return
            
    print(S["invalid"]); pause()

# ---------------- Startup Animation ----------------
def startup_anim():
    """Animasi saat program dimulai."""
    clear(); print("Starting EraldForge ...")
    
    # Animasi spinner
    spinner="|/-\\"
    for i in range(14):
        sys.stdout.write("\r"+spinner[i%4]+" Initializing modules..."); sys.stdout.flush(); time.sleep(0.08)
    
    # Animasi progress bar
    width=30
    for p in range(width+1):
        sys.stdout.write("\rBoot ["+"#"*p+" "*(width-p)+"]"); sys.stdout.flush(); time.sleep(0.02)
    
    sys.stdout.write("\n"); time.sleep(0.12)

# ---------------- Main ----------------
def main():
    """Fungsi utama program."""
    TOOLS_DIR.mkdir(parents=True, exist_ok=True)
    startup_anim()
    
    while True:
        show_menu()
        ch=input()
        handle_choice(ch)

if __name__=="__main__":
    main()