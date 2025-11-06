#!/data/data/com.termux/files/usr/bin/env python3
"""
EraldForge v2.2 — Advanced Termux Multi-Tool Launcher (final)
By Gerald (G-R4L)
"""

import os
import sys
import json
import subprocess
import socket
import time
import platform
from pathlib import Path
from datetime import datetime

# optional psutil; not required (launcher toleran jika psutil tak terpasang)
try:
    import psutil
except Exception:
    psutil = None

# --- Paths & persistent config files ---
BASE = Path(__file__).resolve().parent
TOOLS_DIR = BASE / "tools"
LANG_CFG = Path.home() / ".eraldforge_lang.cfg"
CONSENT_LOG = Path.home() / ".eraldforge_consent.log"
VERSION = "2.2"

# --- Runtime language (launcher will set this later via load_lang()) ---
# default value (will be overwritten by load_lang() call)
LANG = os.environ.get("ERALDFORGE_LANG", "id")

# --- Terminal color palette (simple) ---
COL = {
    "red": "\033[31m",
    "blue": "\033[34m",
    "cyan": "\033[36m",
    "yellow": "\033[33m",
    "green": "\033[32m",
    "white": "\033[37m",
    "bold": "\033[1m",
    "reset": "\033[0m"
}

# --- Helper: run python script and pass ERALDFORGE_LANG to its env ---
def run_python_with_lang(script_path, extra_env=None):
    """
    Run a Python script at script_path while ensuring ERALDFORGE_LANG is set
    in the child's environment. extra_env (dict) merges into env.
    """
    env = os.environ.copy()
    # ensure the current launcher LANG is passed to children
    env["ERALDFORGE_LANG"] = str(LANG)
    if extra_env:
        env.update(extra_env)
    # Use same python interpreter as launcher
    return subprocess.run([sys.executable, str(script_path)], env=env)

# --- Helper: run arbitrary executable with launcher lang in env ---
def run_command_with_lang(cmd_list, extra_env=None, cwd=None):
    env = os.environ.copy()
    env["ERALDFORGE_LANG"] = str(LANG)
    if extra_env:
        env.update(extra_env)
    return subprocess.run(cmd_list, env=env, cwd=cwd)

# ---------------- Colors / Theme ----------------
COL = {
    "red": "\033[31m",
    "blue": "\033[34m",
    "cyan": "\033[36m",
    "yellow": "\033[33m",
    "green": "\033[32m",
    "white": "\033[37m",
    "bold": "\033[1m",
    "reset": "\033[0m"
}

# ---------------- Banner ASCII (your art) ----------------
BANNER_LINES = [
" ____                   ___       __  ____                               ",
"/\\  _`\\                /\\_ \\     /\\ \\ /\\  _`\\                            ",
"\\ \\ \\L\\_\\  _ __    __  \\//\\ \\    \\_\\ \\ \\ \\L\\_\\___   _ __    __      __   ",
" \\ \\  _\\L /\\`'__\\/\'__`\\  \\ \\ \\   /'_` \\ \\  _\\/ __`\\/\\`'__\\/'_ `\\  /'__`\\ ",
"  \\ \\ \\L\\ \\ \\ \\//\\ \\L\\.\\_ \\_\\ \\_/\\ \\L\\ \\ \\ \\/\\ \\L\\ \\ \\ \\//\\ \\L\\ \\/\\  __/ ",
"   \\ \\____/\\ \\_\\\\ \\__/.\\_\\/\\" "\\____\\ \\___,_\\ \\_\\ \\____/\\ \\_\\\\ \\____ \\ \\____\\",
"    \\/___/  \\/_/ \\/__/\\/_/\\/____/\\/__,_ /\\/ _/\\/___/  \\/_/ \\/___L\\ \\/____/",
"                                                            /\\____/      ",
"                                                            \\_/__/       "
]
# Note: the ascii has some backslashes and quotes - keep raw-like content. We'll color lines: top 5 as red (Erald), last 4 as blue (Forge region)

def colored_banner():
    out = []
    # choose split: lines 0-4 = Erald (red), rest = Forge (blue)
    for i, ln in enumerate(BANNER_LINES):
        if i <= 4:
            out.append(COL["red"] + ln + COL["reset"])
        else:
            out.append(COL["blue"] + ln + COL["reset"])
    return "\n".join(out)

# ---------------- Translations ----------------
STR = {
    "id": {
        "tag": "✦ Ethical • Modular • Termux-Native ✦",
        "menu_title": "EraldForge Main Menu",
        "prompt": "Pilih nomor atau huruf: ",
        "update": "Periksa update (git pull)",
        "theme": "Ganti tema",
        "lang": "Ganti bahasa",
        "about": "Tentang EraldForge",
        "exit": "Keluar",
        "no_tools": "Tidak ada tool ditemukan di folder 'tools/'.",
        "press": "Tekan Enter untuk kembali...",
        "consent_title": "=== Persetujuan wajib untuk fitur keamanan ===",
        "consent_prompt": "Ketik 'yes' untuk melanjutkan: ",
        "consent_denied": "Dibatalkan oleh pengguna.",
        "invalid": "Pilihan tidak valid.",
        "ok_update": "✔ Update selesai!",
        "no_update": "Tidak ada update baru."
    },
    "en": {
        "tag": "✦ Ethical • Modular • Termux-Native ✦",
        "menu_title": "EraldForge Main Menu",
        "prompt": "Select number or letter: ",
        "update": "Check for updates (git pull)",
        "theme": "Change theme",
        "lang": "Change language",
        "about": "About EraldForge",
        "exit": "Exit",
        "no_tools": "No tools found in 'tools/' folder.",
        "press": "Press Enter to return...",
        "consent_title": "=== Required consent for security features ===",
        "consent_prompt": "Type 'yes' to continue: ",
        "consent_denied": "Canceled by user.",
        "invalid": "Invalid choice.",
        "ok_update": "✔ Update complete!",
        "no_update": "No new updates."
    }
}

# load language (or ask once)
def load_lang():
    if LANG_CFG.exists():
        v = LANG_CFG.read_text().strip()
        if v in STR:
            return v
    # ask once
    print("Select language / Pilih bahasa:")
    print("1) Bahasa Indonesia")
    print("2) English")
    ch = input("Choice [1/2]: ").strip()
    lang = "en" if ch == "2" else "id"
    try:
        LANG_CFG.write_text(lang)
    except Exception:
        pass
    return lang

LANG = load_lang()
S = STR[LANG]

# ---------------- Utilities ----------------
def clear():
    os.system("clear" if os.name != "nt" else "cls")

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

# ---------------- Tool detection / description (language-aware) ----------------
def list_tools():
    res = []
    if not TOOLS_DIR.exists():
        return res
    for d in sorted(TOOLS_DIR.iterdir()):
        if not d.is_dir(): continue
        meta = d / "meta.json"
        name = d.name
        desc = ""
        entry = None
        sec = False
        if meta.exists():
            try:
                j = json.loads(meta.read_text())
                name = j.get("name", name)
                # prefer language-specific description if available
                if LANG == "en":
                    desc = j.get("desc_en") or j.get("desc") or ""
                else:
                    desc = j.get("desc") or j.get("desc_id") or ""
                entry = j.get("entry")
                sec = bool(j.get("security", False))
            except Exception:
                pass
        res.append({"id": d.name, "name": name, "desc": desc, "entry": entry, "security": sec, "dir": d})
    return res

def find_tool_entry(tool_dir):
    # return entry script filename if present (from meta or default guess)
    meta = tool_dir / "meta.json"
    if meta.exists():
        try:
            j = json.loads(meta.read_text())
            if j.get("entry"):
                return j.get("entry")
        except Exception:
            pass
    # try defaults
    for candidate in ("main.py", "run.py", "start.py", f"{tool_dir.name}.py"):
        if (tool_dir / candidate).exists():
            return candidate
    return None

def run_tool_dir(tool_dir):
    entry = find_tool_entry(tool_dir)
    if not entry:
        return False
    path = tool_dir / entry
    if not path.exists():
        return False
    subprocess.run([sys.executable, str(path)])
    return True

# ---------------- Built-in safe fallbacks ----------------
def builtin_portscanner():
    clear()
    print("=== Port Scanner (fallback, safe TCP connect) ===")
    tgt = input("Target (IP/host): ").strip()
    if not tgt:
        print("No target.")
        pause(); return
    rng = input("Range (e.g. 20-1024) [1-1024]: ").strip() or "1-1024"
    try:
        a,b = rng.split("-"); a=int(a); b=int(b)
    except Exception:
        a,b = 1,1024
    print(f"Scanning {tgt} ports {a}-{b} ... (Ctrl-C to stop)")
    open_ports = []
    for p in range(a, b+1):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)
            if s.connect_ex((tgt, p)) == 0:
                open_ports.append(p)
            s.close()
        except KeyboardInterrupt:
            print("Cancelled by user.")
            break
        except Exception:
            pass
    if open_ports:
        print("Open ports:", ", ".join(map(str, open_ports)))
    else:
        print("No open ports found in scanned range (or host blocked).")
    pause()

def builtin_network_info():
    clear()
    print("=== Network Info (fallback) ===")
    # local outbound IP
    ip = "N/A"
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]; s.close()
    except Exception:
        try:
            ip = socket.gethostbyname(socket.gethostname())
        except Exception:
            ip = "N/A"
    print("Local IP:", ip)
    # gateway via ip route
    gw = "N/A"
    try:
        out = subprocess.check_output(["ip", "route"], stderr=subprocess.DEVNULL).decode(errors="ignore")
        for L in out.splitlines():
            if L.startswith("default"):
                parts = L.split()
                if "via" in parts:
                    gw = parts[parts.index("via")+1]
                break
    except Exception:
        pass
    print("Gateway:", gw)
    # DNS
    dns = []
    try:
        with open("/etc/resolv.conf","r") as f:
            for ln in f:
                ln = ln.strip()
                if ln.startswith("nameserver"):
                    dns.append(ln.split()[1])
    except Exception:
        pass
    print("DNS:", ", ".join(dns) if dns else "N/A")
    # try termux-wifi-connectioninfo
    try:
        out = subprocess.check_output(["termux-wifi-connectioninfo"], stderr=subprocess.DEVNULL).decode(errors="ignore")
        print("\ntermux-wifi-connectioninfo:")
        print(out)
    except Exception:
        print("\nSSID / Wi-Fi details: not available (termux-api required)")
    pause()

def builtin_password_generator():
    clear()
    print("=== Password Generator (fallback) ===")
    try:
        n = int(input("Length [12]: ").strip() or "12")
    except Exception:
        n = 12
    import secrets, string
    chars = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
    pw = "".join(secrets.choice(chars) for _ in range(n))
    print("\nGenerated password:\n", pw)
    # try copy to termux clipboard
    try:
        subprocess.run(["termux-clipboard-set", pw], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("(Copied to clipboard)")
    except Exception:
        pass
    pause()

def builtin_qrcode():
    clear()
    print("=== QR Code Generator (fallback) ===")
    txt = input("Text or URL: ").strip()
    if not txt:
        print("No input."); pause(); return
    # try qrcode lib
    try:
        import qrcode
        img = qrcode.make(txt)
        fname = BASE / f"qrcode_{int(time.time())}.png"
        img.save(str(fname))
        print("Saved PNG:", fname)
    except Exception:
        print("qrcode library not installed. Install with: pip install qrcode pillow")
        print("Fallback display (raw text):")
        print(txt)
    pause()

# ---------------- Menu and runner ----------------
MENU_LIST = [
    ("Port Scanner", "Pemindai port cepat berbasis socket", "portscan"),
    ("IP Tracker", "Melacak IP target (fitur sensitif)", "iptracker"),
    ("File Explorer", "Jelajahi file & direktori lokal", "file_explorer"),
    ("System Monitor", "Cek CPU, RAM, dan penyimpanan", "system_monitor"),
    ("Network Info", "Menampilkan detail koneksi", "network_info"),
    ("Todo CLI", "Todo list sederhana (lokal file)", "todo"),
    ("Password Generator", "Buat password acak & aman", "password_generator"),
    ("QR Code Generator", "Buat QR dari teks/URL (simpan PNG)", "qrcode_generator"),
]

def show_menu():
    clear()
    print(colored_banner())
    print("\n" + COL["cyan"] + "        " + S["tag"] + COL["reset"])
    print(COL["yellow"] + "══════════════════════════════════════════════════════════" + COL["reset"])
    now = datetime.now().strftime("%H:%M:%S")
    print(f"🕒 [{now}]  {S['menu_title']}")
    print(COL["yellow"] + "──────────────────────────────────────────────" + COL["reset"])
    tools = list_tools()
    # map displayed menu to available items: always show 1..8 fixed but prefer descriptions from tools if present
    for idx, (title_id, default_desc, tid) in enumerate(MENU_LIST, start=1):
        # try find tool
        tmeta = next((t for t in tools if t["id"] == tid), None)
        desc = default_desc
        if tmeta:
            if LANG == "en":
                desc = tmeta.get("desc") or tmeta.get("desc_en") or desc
            else:
                desc = tmeta.get("desc") or tmeta.get("desc_id") or desc
            title = tmeta.get("name") or title_id
        else:
            title = title_id
        print(f"[{idx}] {title:<20} - {desc}")
    print(COL["yellow"] + "──────────────────────────────────────────────" + COL["reset"])
    print(f"[U] {S['update']}")
    print(f"[T] {S['theme']}")
    print(f"[L] {S['lang']}")
    print(f"[A] {S['about']}")
    print(f"[0] {S['exit']}")
    print(COL["yellow"] + "══════════════════════════════════════════════════════════" + COL["reset"])

def change_language():
    global LANG, S
    print("1) Bahasa Indonesia")
    print("2) English")
    c = input("Choice [1/2]: ").strip()
    LANG = "en" if c == "2" else "id"
    S = STR[LANG]
    try:
        LANG_CFG.write_text(LANG)
    except Exception:
        pass
    print("Language saved.")
    pause()

def about_show():
    clear()
    if LANG == "en":
        print(f"EraldForge {VERSION}")
        print("Developer : Gerald (G-R4L)")
        print("Repo      : https://github.com/G-R4L/EraldForge")
        print("Purpose   : Termux Multi-Tool Launcher for ethical testing & automation")
    else:
        print(f"EraldForge {VERSION}")
        print("Pengembang : Gerald (G-R4L)")
        print("Repo       : https://github.com/G-R4L/EraldForge")
        print("Tujuan     : Launcher multitool Termux untuk pengujian ethical & otomasi")
    pause()

def attempt_run_menu_item(index):
    # index 0-based
    _, _, tid = MENU_LIST[index]
    # check tool folder first
    td = TOOLS_DIR / tid
    if td.exists() and td.is_dir():
        entry = find_tool_entry(td)
        meta = td / "meta.json"
        security = False
        desc = tid
        if meta.exists():
            try:
                j = json.loads(meta.read_text())
                security = bool(j.get("security", False))
                desc = j.get("desc") or j.get("desc_en") or desc
            except Exception:
                pass
        if security:
            print(S["consent_title"])
            print(desc)
            tgt = input("Target (IP/domain) or leave blank: ").strip() or None
            ok = input(S["consent_prompt"]).strip().lower() == "yes"
            if not ok:
                print(S["consent_denied"]); pause(); return
            save_consent(desc, tgt)
            if tgt:
                os.environ["ERALDFORGE_TARGET"] = tgt
        # run
        if entry:
            run_ok = run_tool_dir(td)
            if not run_ok:
                print("Failed to run tool entry.")
                pause()
            return
    # if external missing, run fallback per tid
    if tid == "portscan":
        builtin_portscanner()
    elif tid == "network_info":
        builtin_network_info()
    elif tid == "system_monitor":
        # show small system monitor
        clear()
        print("=== System Monitor (fallback) ===")
        if psutil:
            try:
                cpu = psutil.cpu_percent(interval=1)
                mem = psutil.virtual_memory()
                print(f"CPU: {cpu}%")
                print(f"RAM: {round(mem.used/1024/1024)}MB / {round(mem.total/1024/1024)}MB ({mem.percent}%)")
            except Exception as e:
                print("psutil error:", e)
        else:
            print("psutil not installed. Install with: pip install psutil")
        pause()
    elif tid == "password_generator":
        builtin_password_generator()
    elif tid == "qrcode_generator":
        builtin_qrcode()
    elif tid == "file_explorer":
        # try to run external else run simple explorer fallback
        builtin_file_explorer()
    elif tid == "iptracker":
        builtin_ip_tracker()
    elif tid == "todo":
        builtin_todo()
    else:
        print("No fallback implemented for this feature yet.")
        pause()

# Provide minimal builtins for other menu items referenced
def builtin_file_explorer():
    clear()
    print("=== File Explorer (fallback) ===")
    cwd = Path.home()
    while True:
        print("\nCurrent:", cwd)
        items = list(sorted(cwd.iterdir()))
        for i, it in enumerate(items, start=1):
            print(f"{i}. {it.name}{'/' if it.is_dir() else ''}")
        print("u. up  q. quit")
        ch = input("Choice: ").strip()
        if ch == "q": break
        if ch == "u":
            cwd = cwd.parent; continue
        try:
            ix = int(ch)-1
            it = items[ix]
            if it.is_dir():
                cwd = it
            else:
                try:
                    print(it.open('r', errors="replace").read(4096))
                except Exception as e:
                    print("Cannot open file:", e)
        except Exception:
            print("Unknown choice.")
    pause()

def builtin_ip_tracker():
    clear()
    print("=== IP Tracker (fallback) ===")
    tgt = input("IP/domain: ").strip()
    if not tgt:
        pause(); return
    # try ipinfo.io
    try:
        p = subprocess.run(["curl","-s", f"https://ipinfo.io/{tgt}/json"], capture_output=True, text=True, timeout=8)
        if p.returncode == 0 and p.stdout:
            print(p.stdout)
        else:
            print("Lookup failed; try 'nslookup' or 'dig'")
    except Exception as e:
        print("Error:", e)
    pause()

def builtin_todo():
    TF = Path.home() / ".eraldforge_todo.json"
    def loadt(): 
        try: return json.loads(TF.read_text())
        except: return []
    def savet(x):
        try: TF.write_text(json.dumps(x, indent=2))
        except: pass
    while True:
        items = loadt()
        clear(); print("=== Todo ===")
        for i,it in enumerate(items): print(f"{i}. [{'x' if it.get('done') else ' '}] {it.get('task')}")
        print("a add, t toggle, d del, q quit")
        c = input("Choice: ").strip().lower()
        if c == "q": break
        if c == "a":
            t = input("Task: ").strip()
            if t: items.append({"task":t,"done":False}); savet(items)
        elif c == "t":
            try: ix = int(input("Index: ").strip()); items[ix]['done'] = not items[ix].get('done', False); savet(items)
            except: print("Invalid")
        elif c == "d":
            try: ix = int(input("Index: ").strip()); items.pop(ix); savet(items)
            except: print("Invalid")
    pause()

# ---------------- Main loop ----------------
def main():
    # ensure tools dir exists
    TOOLS_DIR.mkdir(parents=True, exist_ok=True)

    # quick startup animation
    clear()
    for l in ("[BOOT] Initializing EraldForge...", "[BOOT] Scanning tools...", "[OK] Ready."):
        print(l); time.sleep(0.2)
    time.sleep(0.15)

    while True:
        show_menu()
        choice = input("\n" + S["prompt"]).strip().lower()
        if not choice:
            continue
        if choice in ("0","q","exit"):
            print("Bye.")
            break
        if choice == "u":
            # git pull
            try:
                subprocess.run(["git","--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                p = subprocess.run(["git","pull"], cwd=str(BASE))
                if p.returncode == 0:
                    print(S["ok_update"])
                else:
                    print(S["no_update"])
            except Exception as e:
                print("git error:", e)
            pause(); continue
        if choice == "t":
            print("Theme switching not implemented beyond default.")
            pause(); continue
        if choice == "l":
            change_language(); continue
        if choice == "a":
            about_show(); continue
        # numeric 1..8
        if choice.isdigit():
            n = int(choice)
            if 1 <= n <= len(MENU_LIST):
                attempt_run_menu_item(n-1)
                continue
        print(S["invalid"])
        pause()

if __name__ == "__main__":
    main()
