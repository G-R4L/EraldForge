#!/data/data/com.termux/files/usr/bin/env python3
"""
EraldForge v2.0 — Advanced Termux Multi-Tool Launcher
By Gerald (G-R4L)
"""

import os, sys, json, subprocess, platform, time, socket, psutil
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).resolve().parent
TOOLS_DIR = BASE / "tools"
CONSENT_LOG = Path.home() / ".eraldforge_consent.log"
VERSION = "2.0"

# Color themes
THEMES = {
    "default": {"r":"\033[31m","b":"\033[34m","y":"\033[33m","g":"\033[32m","c":"\033[36m","w":"\033[37m"},
    "matrix":  {"r":"\033[32m","b":"\033[32m","y":"\033[92m","g":"\033[92m","c":"\033[32m","w":"\033[37m"},
    "cyberpunk":{"r":"\033[35m","b":"\033[36m","y":"\033[95m","g":"\033[96m","c":"\033[36m","w":"\033[37m"},
}
theme_name = "default"
C = THEMES[theme_name]
C["reset"] = "\033[0m"; C["bold"] = "\033[1m"

# Banner
BANNER = f"""
{C['r']} _______  ______ _______        {C['b']}______  _______  _____   ______  ______ _______
{C['r']} |______ |_____/ |_____| |      {C['b']}|     \\ |______ |     | |_____/ |  ____ |______
{C['r']} |______ |    \\_ |     | |_____ {C['b']}|_____/ |       |_____| |    \\_ |_____| |______
{C['reset']}
"""

def clear(): os.system("clear" if os.name != "nt" else "cls")

def animate_startup():
    clear()
    boot_lines = [
        "[BOOT] Initializing EraldForge kernel...",
        "[BOOT] Loading tool registry...",
        "[OK] Modules loaded successfully.",
        "[OK] Environment ready.",
        ""
    ]
    for line in boot_lines:
        print(f"\033[32m{line}\033[0m")
        time.sleep(0.5)
    time.sleep(0.4)

def fade_banner():
    clear()
    for _ in range(3):
        print(BANNER)
        time.sleep(0.2)
        clear()
    print(BANNER)
    time.sleep(0.3)

def print_banner():
    fade_banner()
    print(f"{C['c']}        ✦ Ethical • Modular • Termux-Native ✦{C['reset']}")
    print(f"{C['y']}══════════════════════════════════════════════════════════{C['reset']}\n")

def list_tools():
    tools = []
    if TOOLS_DIR.exists():
        for d in sorted(TOOLS_DIR.iterdir()):
            if d.is_dir():
                meta = d / "meta.json"
                info = {"id":d.name,"name":d.name,"desc":"","entry":None,"security":False}
                if meta.exists():
                    try:
                        m = json.load(meta.open())
                        info.update({k:m.get(k,info[k]) for k in info})
                    except: pass
                info["dir"] = d
                tools.append(info)
    return tools

def run_entry(script_path):
    if script_path.suffix == ".py": subprocess.run([sys.executable,str(script_path)])
    else: subprocess.run([str(script_path)])

def consent_prompt(action_desc,target=None):
    print(C["y"] + "\n=== Persetujuan wajib untuk fitur security ===" + C["reset"])
    print("Anda akan menjalankan:", action_desc)
    if target: print("Target:", target)
    print("Pastikan Anda memiliki izin eksplisit untuk tindakan ini.")
    ans = input(C["bold"] + "Ketik 'yes' untuk melanjutkan: " + C["reset"]).strip().lower()
    if ans=="yes":
        with open(CONSENT_LOG,"a") as f:
            f.write(f"{datetime.utcnow().isoformat()} | {action_desc} | target={target}\n")
        return True
    print("❌ Dibatalkan oleh pengguna.")
    return False

def check_for_updates(auto=False):
    try:
        subprocess.run(["git","--version"],check=True,stdout=subprocess.DEVNULL)
        result = subprocess.run(["git","pull"],cwd=str(BASE))
        if result.returncode==0 and not auto:
            print(f"{C['g']}✔ Update selesai! Jalankan ulang EraldForge jika ada perubahan.{C['reset']}")
        elif not auto:
            print(f"{C['y']}Tidak ada update baru.{C['reset']}")
    except Exception as e:
        if not auto: print(f"{C['r']}git error: {e}{C['reset']}")

def system_info():
    clear()
    print("═══════════ ERALD SYSTEM MONITOR ═══════════")

    # CPU Usage
    cpu_usage = psutil.cpu_percent(interval=1)

    # RAM
    mem = psutil.virtual_memory()
    ram_used = round(mem.used / (1024 ** 2))
    ram_total = round(mem.total / (1024 ** 2))

    # Disk
    disk = psutil.disk_usage('/')
    disk_used = round(disk.used / (1024 ** 3), 1)
    disk_total = round(disk.total / (1024 ** 3), 1)

    # Network
    net = psutil.net_io_counters()
    rx = round(net.bytes_recv / 1024, 1)
    tx = round(net.bytes_sent / 1024, 1)

    # Processes
    processes = len(psutil.pids())

    # Battery (optional)
    try:
        battery = psutil.sensors_battery()
        if battery:
            batt = f"{battery.percent}% ({'Charging' if battery.power_plugged else 'Discharging'})"
        else:
            batt = "N/A"
    except Exception:
        batt = "N/A"

    # Temperature
    try:
        temps = psutil.sensors_temperatures()
        temp = list(temps.values())[0][0].current if temps else 37.0
    except Exception:
        temp = 37.0

    # Uptime
    uptime_seconds = time.time() - psutil.boot_time()
    uptime = time.strftime("%Hh %Mm %Ss", time.gmtime(uptime_seconds))

    # Date & Time
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # OS Info
    os_version = f"{platform.system()} {platform.release()} ({platform.machine()})"
    kernel = platform.version()

    # CPU Info
    cpu_count = psutil.cpu_count(logical=True)
    cpu_arch = platform.machine()

    # IP
    try:
        ip = socket.gethostbyname(socket.gethostname())
    except:
        ip = "Tidak terdeteksi"

    print(f"CPU Usage       : {cpu_usage}%")
    print(f"RAM Usage       : {ram_used}MB / {ram_total}MB")
    print(f"Storage Usage   : {disk_used}GB / {disk_total}GB")
    print(f"Network RX/TX   : {rx}KB ↓   {tx}KB ↑")
    print(f"Processes       : {processes} aktif")
    print(f"Battery Level   : {batt}")
    print(f"Device Temp     : {temp}°C")
    print(f"System Uptime   : {uptime}")
    print(f"Date & Time     : {now}")
    print(f"OS Version      : {os_version}")
    print(f"Kernel Version  : {kernel[:40]}...")
    print(f"CPU Cores       : {cpu_count} Cores ({cpu_arch})")
    print(f"IP Address      : {ip}")
    print("════════════════════════════════════════════")
    input("Tekan [Enter] untuk kembali ke menu utama.")

def about():
    print(f"{C['b']}EraldForge {VERSION}{C['reset']}")
    print("Developer : Gerald (G-R4L)")
    print("Repo      : https://github.com/G-R4L/EraldForge")
    print("Purpose   : Termux Multi-Tool Launcher for ethical testing & automation")
    print()

def switch_theme():
    global theme_name,C
    print("Tema tersedia:")
    for t in THEMES.keys(): print("-",t)
    new_t = input("Pilih tema: ").strip().lower()
    if new_t in THEMES:
        theme_name=new_t; C=THEMES[new_t]; C["reset"]="\033[0m"; C["bold"]="\033[1m"
        print(f"Tema diganti ke {new_t}.")
        time.sleep(1)
    else: print("Tema tidak dikenal.")

def show_menu(tools):
    now=datetime.now().strftime("%H:%M:%S")
    print(f"{C['b']}[{now}] {C['c']}EraldForge Main Menu{C['reset']}")
    print(f"{C['y']}──────────────────────────────────────────────{C['reset']}")
    for i,t in enumerate(tools,1):
        sec=f"{C['r']}⚠{C['reset']}" if t['security'] else ""
        print(f"{C['g']}[{i}] {C['bold']}{t['name']}{C['reset']} {sec}")
        print(f"    {C['w']}{t['desc']}{C['reset']}")
        print(f"{C['y']}──────────────────────────────────────────────{C['reset']}")
    print(f"{C['b']}[U]{C['reset']} Periksa update")
    print(f"{C['b']}[T]{C['reset']} Ganti tema")
    print(f"{C['b']}[I]{C['reset']} Info sistem")
    print(f"{C['b']}[A]{C['reset']} Tentang EraldForge")
    print(f"{C['r']}[0]{C['reset']} Keluar")
    print(f"{C['y']}══════════════════════════════════════════════════════════{C['reset']}")

def main():
    animate_startup()
    check_for_updates(auto=True)
    while True:
        print_banner()
        tools=list_tools()
        if not tools:
            print(f"{C['r']}Tidak ada tool di folder /tools.{C['reset']}")
            input("Tekan Enter...")
            break
        show_menu(tools)
        ch=input(f"\n{C['bold']}Pilih nomor/huruf: {C['reset']}").strip().lower()
        if ch in ("0","q","exit"): print(f"{C['y']}Sampai jumpa!{C['reset']}"); break
        elif ch=="u": check_for_updates(); input("Enter...")
        elif ch=="i": system_info()
        elif ch=="a": about(); input("Enter...")
        elif ch=="t": switch_theme(); continue
        else:
            try:
                idx=int(ch)-1
                if idx<0 or idx>=len(tools): raise ValueError
                t=tools[idx]
                if t["security"]:
                    target=input("Masukkan target (IP/domain): ").strip() or None
                    if not consent_prompt(t["desc"],target): continue
                    os.environ["ERALDFORGE_TARGET"]=target or ""
                entry_path=t["dir"]/t["entry"]
                if not entry_path.exists(): print("Entry tidak ditemukan."); continue
                run_entry(entry_path)
            except ValueError:
                print("Input tidak valid.")
        input(f"\n{C['y']}Tekan Enter untuk kembali ke menu...{C['reset']}")

if __name__=="__main__":
    main()
