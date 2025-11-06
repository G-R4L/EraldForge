#!/data/data/com.termux/files/usr/bin/env python3
"""
EraldForge v2.3 — Launcher (ID-only)
By Gerald (G-R4L)
Updated: animasi loading, menu System Monitor terpisah, info lengkap
"""

import os, sys, json, subprocess, socket, time, platform
from pathlib import Path
from datetime import datetime, timedelta

# optional psutil
try:
    import psutil
except Exception:
    psutil = None

BASE = Path(__file__).resolve().parent
TOOLS_DIR = BASE / "tools"
CONSENT_LOG = Path.home() / ".eraldforge_consent.log"
VERSION = "2.3"
ERALD_LANG = "id"   # fixed Indonesian

# --- color palettes (themes) ---
THEMES = {
    "default": {"num":"\033[36m","title":"\033[34m","desc":"\033[37m","accent":"\033[33m","reset":"\033[0m","bold":"\033[1m"},
    "matrix":  {"num":"\033[32m","title":"\033[32m","desc":"\033[37m","accent":"\033[92m","reset":"\033[0m","bold":"\033[1m"},
    "cyberpunk":{"num":"\033[95m","title":"\033[96m","desc":"\033[37m","accent":"\033[93m","reset":"\033[0m","bold":"\033[1m"},
    "solarized":{"num":"\033[33m","title":"\033[36m","desc":"\033[37m","accent":"\033[32m","reset":"\033[0m","bold":"\033[1m"}
}
CURRENT_THEME = "default"
C = THEMES[CURRENT_THEME]

# --- Banner ASCII ---
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

# ---------------- translations (ID only) ----------------
S = {
    "tag": "✦ Ethical • Modular • Termux-Native ✦",
    "menu_title": "EraldForge Main Menu",
    "prompt": "Pilih nomor atau huruf: ",
    "update_ok": "✔ Update selesai!",
    "update_none": "Tidak ada update baru.",
    "consent_title": "=== Persetujuan wajib untuk fitur keamanan ===",
    "consent_prompt": "Ketik 'yes' untuk lanjut: ",
    "consent_denied": "Dibatalkan oleh pengguna.",
    "press": "Tekan Enter untuk kembali...",
    "invalid": "Pilihan tidak valid."
}

# ---------------- helpers ----------------
def clear(): os.system("clear" if os.name!="nt" else "cls")
def pause(msg=None):
    if msg is None: msg = S["press"]
    try: input(msg)
    except: pass

def save_consent(action, target=None):
    try:
        with open(CONSENT_LOG,"a") as f:
            f.write(f"{datetime.utcnow().isoformat()} | {action} | target={target}\n")
    except: pass

def run_python(script_path):
    env = os.environ.copy()
    env["ERALDFORGE_LANG"] = ERALD_LANG
    return subprocess.run([sys.executable,str(script_path)], env=env)

def run_tool_dir(tool_dir):
    meta = tool_dir / "meta.json"
    entry = None
    if meta.exists():
        try:
            j = json.loads(meta.read_text())
            entry = j.get("entry")
        except:
            pass
    if not entry:
        for c in ("main.py","run.py","start.py", f"{tool_dir.name}.py"):
            if (tool_dir / c).exists(): entry=c; break
    if not entry: return False
    p = tool_dir / entry
    if p.suffix==".py": run_python(p)
    else: subprocess.run([str(p)])
    return True

# ---------------- menu items ----------------
MENU_LIST=[
    ("calculator","Kalkulator"),
    ("clipboard","Clipboard"),
    ("file_explorer","Jelajahi file"),
    ("port_scanner","Port scanner"),
    ("todo","Todo list"),
    ("wifi_info","Info Wi-Fi")
]

def get_tool_display(tool_id):
    td=TOOLS_DIR/tool_id
    name=tool_id; desc=""
    if td.exists() and (td/"meta.json").exists():
        try:
            j=json.loads((td/"meta.json").read_text())
            name=j.get("name",tool_id)
            desc=j.get("desc") or j.get("desc_id") or ""
        except: pass
    if not desc:
        for k,d in MENU_LIST:
            if k==tool_id: desc=d; break
    return name, desc

# ---------------- fallback tools ----------------
def fallback_calculator():
    clear(); print("== Kalkulator ==")
    expr=input("Masukkan ekspresi: ")
    try: safe={"__builtins__":None}; res=eval(expr,safe,{}); print("Hasil:",res)
    except Exception as e: print("Error:", e)
    pause()

def fallback_clipboard():
    clear(); print("== Clipboard ==")
    try: out=subprocess.check_output(["termux-clipboard-get"],stderr=subprocess.DEVNULL).decode(errors="ignore"); print(out[:1000])
    except: print("termux-api tidak tersedia.")
    pause()

def fallback_todo():
    TF=Path.home()/".eraldforge_todo.json"
    def load(): 
        try: return json.loads(TF.read_text())
        except: return []
    def save(x): 
        try: TF.write_text(json.dumps(x,indent=2))
        except: pass
    while True:
        clear(); items=load(); print("=== Todo ===")
        for i,it in enumerate(items): print(f"{i}. [{'x' if it.get('done') else ' '}] {it.get('task')}")
        print("a add, t toggle, d del, q quit")
        c=input("Pilihan: ").strip().lower()
        if c=="q": break
        if c=="a": t=input("Task: "); items.append({"task":t,"done":False}); save(items)
        if c=="t": 
            try: ix=int(input("Index: ")); items[ix]['done']=not items[ix].get('done',False); save(items)
            except: pass
        if c=="d": 
            try: ix=int(input("Index: ")); items.pop(ix); save(items)
            except: pass
    pause()

# ---------------- system monitor baru ----------------
def system_monitor():
    clear()
    print("=== System Monitor ===")
    if not psutil: print("psutil belum terpasang (pip install psutil)"); pause(); return
    try:
        # CPU
        cpu_all=psutil.cpu_percent(interval=1)
        cpu_per_core=psutil.cpu_percent(interval=0.5, percpu=True)
        print(f"CPU Total   : {cpu_all}%")
        for i,p in enumerate(cpu_per_core): print(f"CPU Core {i} : {p}%")
        # RAM
        mem=psutil.virtual_memory()
        print(f"RAM Used    : {round(mem.used/1024/1024)}MB / {round(mem.total/1024/1024)}MB ({mem.percent}%)")
        # Disk
        disk=psutil.disk_usage("/")
        print(f"Disk Used   : {round(disk.used/1024/1024/1024,1)}GB / {round(disk.total/1024/1024/1024,1)}GB ({disk.percent}%)")
        # Battery
        try: bt=psutil.sensors_battery(); print(f"Battery     : {bt.percent}% {'(Charging)' if bt.power_plugged else ''}" if bt else "Battery     : N/A")
        except: pass
        # Uptime
        uptime_sec=time.time()-psutil.boot_time()
        print("Uptime      :", str(timedelta(seconds=int(uptime_sec))))
        # Network
        try:
            net=psutil.net_io_counters()
            print(f"Network TX  : {round(net.bytes_sent/1024/1024,2)} MB")
            print(f"Network RX  : {round(net.bytes_recv/1024/1024,2)} MB")
        except: pass
    except Exception as e: print("Error:",e)
    pause()

# ---------------- display menu ----------------
def show_main_menu():
    clear(); print(colored_banner())
    print("\n"+C["title"]+"    "+S["tag"]+C["reset"])
    print(C["accent"]+"══════════════════════════════════════════════════════════"+C["reset"])
    now=datetime.now().strftime("%H:%M:%S")
    print(f"🕒 [{now}]  {C['title']}{S['menu_title']}{C['reset']}")
    print(C["accent"]+"──────────────────────────────────────────────"+C["reset"])
    for i,(tid,default_desc) in enumerate(MENU_LIST,start=1):
        title,desc=get_tool_display(tid)
        if len(desc)>25: desc=desc[:22]+"..."
        print(f"{C['num']}[{i}]{C['reset']} {C['title']}{title:<18}{C['reset']} - {C['desc']}{desc}{C['reset']}")
    print(C["accent"]+"──────────────────────────────────────────────"+C["reset"])
    print(f"{C['num']}[U]{C['reset']} Update GitHub")
    print(f"{C['num']}[T]{C['reset']} Tema")
    print(f"{C['num']}[S]{C['reset']} System Monitor")
    print(f"{C['num']}[A]{C['reset']} Tentang")
    print(f"{C['num']}[0]{C['reset']} Keluar")
    print(C["accent"]+"══════════════════════════════════════════════════════════"+C["reset"])

def theme_submenu():
    global CURRENT_THEME, C
    clear(); print("=== Tema ===")
    names=list(THEMES.keys())
    for i,n in enumerate(names,start=1): print(f"[{i}] {n}")
    print("[B] Kembali")
    ch=input("Pilih: ").strip().lower()
    if ch=="b": return
    try: idx=int(ch)-1
    except: idx=-1
    if 0<=idx<len(names):
        CURRENT_THEME=names[idx]; C=THEMES[CURRENT_THEME]; print("Tema diganti:",CURRENT_THEME)
    else: print("Pilihan tidak valid.")
    pause()

def about_menu():
    clear(); print(f"EraldForge {VERSION}\nDeveloper: Gerald (G-R4L)\nRepo: https://github.com/G-R4L/EraldForge"); pause()

# ---------------- main loop ----------------
def handle_choice(choice):
    choice=choice.strip().lower()
    if not choice: return
    if choice in ("0","q","exit"): print("Bye."); sys.exit(0)
    if choice=="u":
        try: subprocess.run(["git","pull"],cwd=str(BASE))
        except: pass; print("Update selesai.")
        pause(); return
    if choice=="t": theme_submenu(); return
    if choice=="s": system_monitor(); return
    if choice=="a": about_menu(); return
    if choice.isdigit():
        n=int(choice)
        if 1<=n<=len(MENU_LIST):
            tid=MENU_LIST[n-1][0]; td=TOOLS_DIR/tid
            # fallback tools
            if tid=="calculator": fallback_calculator(); return
            if tid=="clipboard": fallback_clipboard(); return
            if tid=="todo": fallback_todo(); return
    print(S["invalid"]); pause()

def main():
    TOOLS_DIR.mkdir(parents=True,exist_ok=True)
    # --- animasi booting ---
    clear()
    boot_msgs=["[BOOT] Initializing EraldForge...","[BOOT] Loading modules...","[BOOT] Ready."]
    for msg in boot_msgs: print(msg); time.sleep(0.3)
    while True:
        show_main_menu()
        ch=input("\n"+S["prompt"])
        handle_choice(ch)

if __name__=="__main__":
    main()
