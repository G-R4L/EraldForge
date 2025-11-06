#!/data/data/com.termux/files/usr/bin/env python3
"""
EraldForge v2.3 — Launcher final (ID-only)
By Gerald (G-R4L)

Fitur & perbaikan:
- Banner ASCII Erald (merah) / Forge (biru)
- Animasi startup (boot) + progress spinner
- Menu rapi 1..8 + S (System Monitor) + T (Tema) + A (Tentang) + 0 (Keluar)
- Deskripsi dipangkas rapi sesuai lebar terminal
- System Monitor lengkap + fallback jika psutil tidak terpasang atau /proc stat permission denied
- Fallback builtin tools bila folder tools/<id> tidak ada
- Semua tool Python dipanggil dengan ERALDFORGE_LANG set
- Consent logging untuk fitur sensitif
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

# optional psutil (not required)
try:
    import psutil
except Exception:
    psutil = None

# ---------------- paths / config ----------------
BASE = Path(__file__).resolve().parent
TOOLS_DIR = BASE / "tools"
CONSENT_LOG = Path.home() / ".eraldforge_consent.log"
VERSION = "2.3"
ERALD_LANG = "id"   # fixed Indonesian

# ---------------- color palette (simple) ----------------
THEMES = {
    "default": {"num":"\033[36m","title":"\033[34m","desc":"\033[37m","accent":"\033[33m","reset":"\033[0m","bold":"\033[1m"},
    "matrix":  {"num":"\033[32m","title":"\033[32m","desc":"\033[37m","accent":"\033[92m","reset":"\033[0m","bold":"\033[1m"},
    "cyberpunk":{"num":"\033[95m","title":"\033[96m","desc":"\033[37m","accent":"\033[93m","reset":"\033[0m","bold":"\033[1m"},
    "solarized":{"num":"\033[33m","title":"\033[36m","desc":"\033[37m","accent":"\033[32m","reset":"\033[0m","bold":"\033[1m"}
}
CURRENT_THEME = "default"
C = THEMES[CURRENT_THEME]

# ---------------- Banner ASCII (Erald red top lines, Forge blue bottom) ----------------
BANNER_LINES = [
" ____                   ___       __  ____                               ",
"/\\  _`\\                /\\_ \\     /\\ \\ /\\  _`\\                            ",
"\\ \\ \\L\\_\\  _ __    __  \\//\\ \\    \\_\\ \\ \\ \\L\\_\\___   _ __    __      __   ",
" \\ \\  _\\L /\\`'__\\/\'__`\\  \\ \\ \\   /'_` \\ \\  _\\/ __`\\/\\`'__\\/'_ `\\  /'__`\\ ",
"  \\ \\ \\L\\ \\ \\ \\//\\ \\L\\.\\_ \\_\\ \\_/\\ \\L\\ \\ \\ \\/\\ \\L\\ \\ \\ \\//\\ \\L\\ \\/\\  __/ ",
"   \\ \\____/\\ \\_\\\\ \\__/.\\_\\/\\____\\ \\___,_\\ \\_\\ \\____/\\ \\_\\\\ \\____ \\ \\____\\",
"    \\/___/  \\/_/ \\/__/\\/_/\\/____/\\/__,_ /\\/ _/\\/___/  \\/_/ \\/___L\\ \\/____/",
"                                                            /\\____/      ",
"                                                            \\_/__/       "
]

def colored_banner():
    out = []
    for i, ln in enumerate(BANNER_LINES):
        if i <= 4:
            out.append("\033[31m" + ln + C["reset"])  # Erald = red
        else:
            out.append("\033[34m" + ln + C["reset"])  # Forge = blue
    return "\n".join(out)

# ---------------- menu & defaults ----------------
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

# ---------------- UI strings (ID) ----------------
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

# ---------------- helpers ----------------
def clear():
    os.system("clear" if os.name != "nt" else "cls")

def term_width(default=80):
    try:
        w = shutil.get_terminal_size().columns
        return max(60, w)
    except Exception:
        return default

def shorten(s, width):
    # use textwrap.shorten to avoid cutting words abruptly
    try:
        return textwrap.shorten(s, width=width, placeholder="...")
    except Exception:
        return (s[:width-3] + "...") if len(s)>width else s

def pause(msg=None):
    if msg is None:
        msg = S["press"]
    try:
        input(msg)
    except Exception:
        pass

def save_consent(action, target=None):
    try:
        with open(CONSENT_LOG, "a") as f:
            f.write(f"{datetime.utcnow().isoformat()} | {action} | target={target}\n")
    except Exception:
        pass

def run_python_with_lang(script_path, extra_env=None):
    env = os.environ.copy()
    env["ERALDFORGE_LANG"] = ERALD_LANG
    if extra_env:
        env.update(extra_env)
    return subprocess.run([sys.executable, str(script_path)], env=env)

def run_tool_dir(tool_dir):
    """
    Find entry from meta.json or try common filenames.
    Returns True if ran something, False otherwise.
    """
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
    # if python script -> run with same interpreter and pass ERALDFORGE_LANG
    if p.suffix == ".py":
        run_python_with_lang(p)
    else:
        subprocess.run([str(p)])
    return True

# ---------------- built-in fallback implementations ----------------
def fallback_calculator():
    clear()
    print("== Kalkulator fallback ==")
    expr = input("Masukkan ekspresi (mis. 2+2): ").strip()
    if not expr:
        pause(); return
    # minimal safe eval: allow math functions
    import math
    SAFE = {"__builtins__": None}
    SAFE.update({k: getattr(math, k) for k in dir(math) if not k.startswith("_")})
    SAFE.update({"abs": abs, "round": round, "pow": pow})
    try:
        res = eval(expr, SAFE, {})
        print("Hasil:", res)
    except Exception as e:
        print("Error:", e)
    pause()

def fallback_clipboard():
    clear()
    print("== Clipboard fallback ==")
    try:
        out = subprocess.check_output(["termux-clipboard-get"], stderr=subprocess.DEVNULL).decode(errors="ignore")
        print("Preview clipboard (max 1000 chars):")
        print(out[:1000])
    except Exception:
        print("termux-api tidak tersedia atau izin belum diberikan.")
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
            print("Tidak dapat membaca direktori:", e); pause(); return
        for i, it in enumerate(items[:200], start=1):
            name = it.name + ("/" if it.is_dir() else "")
            print(f"{i}. {name}")
        print("u. up, q. quit")
        ch = input("Choice: ").strip().lower()
        if ch == "q":
            break
        if ch == "u":
            cwd = cwd.parent
            continue
        try:
            ix = int(ch) - 1
            it = items[ix]
            if it.is_dir():
                cwd = it
            else:
                try:
                    print(it.open("r", errors="replace").read(4096))
                except Exception as e:
                    print("Tidak bisa buka file:", e)
        except Exception:
            print("Pilihan tidak valid.")
    pause()

def fallback_portscanner():
    clear()
    print("== Port Scanner fallback (TCP connect scan) ==")
    tgt = input("Target (host/IP): ").strip()
    if not tgt:
        pause(); return
    rng = input("Range (e.g. 20-1024) [1-1024]: ").strip() or "1-1024"
    try:
        a, b = rng.split("-"); a = int(a); b = int(b)
    except Exception:
        a, b = 1, 1024
    print(f"Scanning {tgt} ports {a}-{b} ... (Ctrl-C to stop)")
    open_ports = []
    for p in range(a, b+1):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.35)
            if s.connect_ex((tgt, p)) == 0:
                open_ports.append(p)
            s.close()
        except KeyboardInterrupt:
            print("Dibatalkan.")
            break
        except Exception:
            pass
    if open_ports:
        print("Open ports:", ", ".join(map(str, open_ports)))
    else:
        print("Tidak ditemukan port terbuka di rentang itu (atau blocked).")
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
        print("=== Todo (fallback) ===")
        for i, it in enumerate(items):
            print(f"{i}. [{'x' if it.get('done') else ' '}] {it.get('task')}")
        print("a add, t toggle, d del, q quit")
        c = input("Pilihan: ").strip().lower()
        if c == "q":
            break
        if c == "a":
            t = input("Task: ").strip()
            if t:
                items.append({"task": t, "done": False}); save(items)
        elif c == "t":
            try:
                ix = int(input("Index: ").strip()); items[ix]['done'] = not items[ix].get('done', False); save(items)
            except Exception:
                print("Invalid index")
        elif c == "d":
            try:
                ix = int(input("Index: ").strip()); items.pop(ix); save(items)
            except Exception:
                print("Invalid index")
    pause()

def fallback_wifi_info():
    clear()
    print("== Wi‑Fi Info (fallback) ==")
    try:
        out = subprocess.check_output(["termux-wifi-scaninfo"], stderr=subprocess.DEVNULL).decode(errors="ignore")
        print(out)
    except Exception:
        print("termux-api tidak tersedia atau izin lokasi diperlukan.")
    pause()

def builtin_password_generator():
    clear()
    print("=== Password Generator ===")
    try:
        n = int(input("Length [16]: ").strip() or "16")
    except Exception:
        n = 16
    import secrets, string
    chars = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
    pw = "".join(secrets.choice(chars) for _ in range(n))
    print("\nGenerated password:\n", pw)
    try:
        subprocess.run(["termux-clipboard-set", pw], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("(Tersalin ke clipboard)")
    except Exception:
        pass
    pause()

def builtin_qrcode():
    clear()
    print("=== QR Code Generator ===")
    txt = input("Text/URL: ").strip()
    if not txt:
        pause(); return
    try:
        import qrcode
        img = qrcode.make(txt)
        fname = BASE / f"qrcode_{int(time.time())}.png"
        img.save(str(fname))
        print("QR disimpan:", fname)
    except Exception:
        print("Library qrcode tidak tersedia. Instal: pip install qrcode pillow")
        print("Fallback: menampilkan teks:")
        print(txt)
    pause()

# ---------------- System Monitor (diperbaiki, tangani permission) ----------------
def system_monitor():
    clear()
    print("=== System Monitor ===")
    if not psutil:
        print("psutil belum terpasang. Untuk info lebih lengkap: pip install psutil")
        pause(); return
    try:
        # CPU total & per core
        try:
            cpu_total = psutil.cpu_percent(interval=1)
            cpu_per = psutil.cpu_percent(interval=0.5, percpu=True)
        except PermissionError as pe:
            print("PermissionError saat membaca /proc: beberapa metrik tidak tersedia.")
            print("Detail error:", pe)
            pause(); return
        print(f"CPU Total : {cpu_total}%")
        for i, v in enumerate(cpu_per):
            print(f"  Core {i:02d} : {v}%")
        # RAM
        mem = psutil.virtual_memory()
        print(f"RAM Used  : {round(mem.used/1024/1024)}MB / {round(mem.total/1024/1024)}MB ({mem.percent}%)")
        # Disk
        disk = psutil.disk_usage("/")
        print(f"Disk Used : {round(disk.used/1024/1024/1024,1)}GB / {round(disk.total/1024/1024/1024,1)}GB ({disk.percent}%)")
        # Uptime
        uptime_s = time.time() - psutil.boot_time()
        print("Uptime    :", str(timedelta(seconds=int(uptime_s))))
        # Network
        try:
            net = psutil.net_io_counters()
            print(f"Network TX: {round(net.bytes_sent/1024/1024,2)} MB")
            print(f"Network RX: {round(net.bytes_recv/1024/1024,2)} MB")
        except Exception:
            pass
        # Battery (optional)
        try:
            batt = psutil.sensors_battery()
            if batt:
                print(f"Battery   : {batt.percent}% {'(Charging)' if batt.power_plugged else ''}")
            else:
                print("Battery   : N/A")
        except Exception:
            pass
        # Process count & top few processes
        try:
            pids = psutil.pids()
            print(f"Processes : {len(pids)} total")
            # show top 5 by memory (best-effort)
            procs = []
            for pid in pids[-200:]:
                try:
                    p = psutil.Process(pid)
                    procs.append((p.memory_info().rss, pid, p.name()))
                except Exception:
                    pass
            procs.sort(reverse=True)
            print("Top processes by memory (rss):")
            for mem_rss, pid, name in procs[:5]:
                print(f"  {pid} {name} {round(mem_rss/1024/1024,2)}MB")
        except Exception:
            pass
    except Exception as e:
        print("System monitor error:", e)
    pause()

# ---------------- UI: menu show & theme ----------------
def show_menu():
    clear()
    # banner + tagline
    print(colored_banner())
    print("\n" + C["title"] + "    " + S["tag"] + C["reset"])
    print(C["accent"] + "══════════════════════════════════════════════════════════" + C["reset"])
    now = datetime.now().strftime("%H:%M:%S")
    print(f"🕒 [{now}]  {C['title']}{S['menu_title']}{C['reset']}")
    print(C["accent"] + "──────────────────────────────────────────────" + C["reset"])
    # compute description width
    width = term_width()
    left_col = 6  # "[1] " etc + spacing
    name_col = 20
    desc_width = max(20, width - (left_col + name_col + 8))
    for i, (tid, default_desc) in enumerate(MENU_LIST, start=1):
        title = tid.replace("_", " ").title()
        # try to get meta desc short
        meta_desc = ""
        md = TOOLS_DIR / tid / "meta.json"
        if md.exists():
            try:
                j = json.loads(md.read_text())
                meta_desc = j.get("desc") or j.get("desc_id") or j.get("desc_en") or ""
            except Exception:
                meta_desc = ""
        desc = meta_desc or default_desc
        desc = shorten(desc, desc_width)
        print(f"{C['num']}[{i}]{C['reset']} {C['title']}{title:<{name_col}}{C['reset']} - {C['desc']}{desc}{C['reset']}")
    print(C["accent"] + "──────────────────────────────────────────────" + C["reset"])
    print(f"{C['num']}[U]{C['reset']} Update GitHub     - tarik update dari repo")
    print(f"{C['num']}[T]{C['reset']} Tema             - ganti tema")
    print(f"{C['num']}[S]{C['reset']} System Monitor    - info lengkap sistem")
    print(f"{C['num']}[A]{C['reset']} Tentang EraldForge - informasi versi & author")
    print(f"{C['num']}[0]{C['reset']} Keluar            - tutup program")
    print(C["accent"] + "══════════════════════════════════════════════════════════" + C["reset"])

def theme_menu():
    global CURRENT_THEME, C
    clear()
    print("=== Pilih Tema ===")
    names = list(THEMES.keys())
    for i, n in enumerate(names, start=1):
        print(f"[{i}] {n}")
    print("[B] Kembali")
    choice = input("Pilih: ").strip().lower()
    if choice == "b":
        return
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(names):
            CURRENT_THEME = names[idx]
            C = THEMES[CURRENT_THEME]
            print("Tema diganti:", CURRENT_THEME)
        else:
            print("Pilihan tidak valid.")
    except Exception:
        print("Pilihan tidak valid.")
    pause()

def about_menu():
    clear()
    print(f"EraldForge {VERSION}")
    print("Pengembang : Gerald (G-R4L)")
    print("Repo       : https://github.com/G-R4L/EraldForge")
    print("Tujuan     : Multitool Termux, aman & ethical")
    pause()

# ---------------- commands handling ----------------
def handle_choice(ch):
    ch = ch.strip().lower()
    if not ch:
        return
    if ch in ("0", "q", "exit"):
        print("Bye."); sys.exit(0)
    if ch == "u":
        try:
            subprocess.run(["git", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            p = subprocess.run(["git", "pull"], cwd=str(BASE))
            if p.returncode == 0:
                print(S["update_ok"])
            else:
                print(S["update_none"])
        except Exception as e:
            print("git error:", e)
        pause(); return
    if ch == "t":
        theme_menu(); return
    if ch == "s":
        system_monitor(); return
    if ch == "a":
        about_menu(); return
    # numeric menu 1..8
    if ch.isdigit():
        n = int(ch)
        if 1 <= n <= len(MENU_LIST):
            tid = MENU_LIST[n-1][0]
            td = TOOLS_DIR / tid
            # check meta for security
            meta = td / "meta.json"
            security = False
            desc = ""
            if meta.exists():
                try:
                    j = json.loads(meta.read_text())
                    security = bool(j.get("security", False))
                    desc = j.get("desc") or j.get("desc_id") or j.get("desc_en") or ""
                except Exception:
                    pass
            if security:
                print(S["consent_title"])
                print(desc or MENU_LIST[n-1][1])
                ok = input(S["consent_prompt"]).strip().lower() == "yes"
                if not ok:
                    print(S["consent_denied"]); pause(); return
                tgt = input("Target (IP/domain) atau kosong: ").strip() or None
                save_consent(desc or tid, tgt)
                if tgt:
                    os.environ["ERALDFORGE_TARGET"] = tgt
            # try to run external tool folder entry
            if td.exists() and td.is_dir():
                ran = run_tool_dir(td)
                if ran:
                    return
            # fallback mapping
            if tid == "calculator":
                fallback_calculator(); return
            if tid == "clipboard":
                fallback_clipboard(); return
            if tid == "file_explorer":
                fallback_file_explorer(); return
            if tid == "port_scanner" or tid == "port_scanner":
                fallback_portscanner(); return
            if tid == "todo":
                fallback_todo(); return
            if tid == "wifi_info":
                fallback_wifi_info(); return
            if tid == "password_generator":
                builtin_password_generator(); return
            if tid == "qrcode_generator":
                builtin_qrcode(); return
            # generic fallback
            print("Tool tidak ditemukan dan tidak ada fallback.")
            pause(); return
    print(S["invalid"])
    pause()

# ---------------- startup animation (spinner + progress) ----------------
def startup_anim():
    clear()
    print("Starting EraldForge ...")
    spinner = "|/-\\"
    for i in range(14):
        sys.stdout.write("\r" + spinner[i % 4] + " Initializing modules...")
        sys.stdout.flush()
        time.sleep(0.08)
    # small progress bar
    width = 30
    for p in range(width + 1):
        bar = "[" + "#" * p + " " * (width - p) + "]"
        sys.stdout.write("\r" + "Boot " + bar)
        sys.stdout.flush()
        time.sleep(0.02)
    sys.stdout.write("\n")
    time.sleep(0.12)

# ---------------- main ----------------
def main():
    TOOLS_DIR.mkdir(parents=True, exist_ok=True)
    startup_anim()
    while True:
        show_menu()
        ch = input("\n" + S["prompt"])
        handle_choice(ch)

if __name__ == "__main__":
    main()
