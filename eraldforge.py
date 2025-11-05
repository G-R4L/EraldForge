#!/data/data/com.termux/files/usr/bin/env python3
"""
EraldForge v2.1 - Launcher utama
By Gerald (G-R4L)

Catatan:
- Launcher mendeteksi tools di folder tools/
- Theme: "hacker" atau "clean" (env ERALDFORGE_THEME atau pilih saat runtime)
- Language: disimpan di ~/.eraldforge_lang.cfg (values: "id" atau "en")
- Tidak memaksa pemasangan paket; tool yang butuh pip akan memberikan pesan instruksi jika belum terpasang.
"""

import os
import sys
import json
import subprocess
import time
import socket
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).resolve().parent
TOOLS_DIR = BASE / "tools"
CONSENT_LOG = Path.home() / ".eraldforge_consent.log"
LANG_CFG = Path.home() / ".eraldforge_lang.cfg"
VERSION = "2.1"

# Themes: hacker (green-ish) and clean (blue/cyan)
THEMES = {
    "hacker": {"primary":"\033[32m","accent":"\033[36m","muted":"\033[37m","warn":"\033[33m","err":"\033[31m","bold":"\033[1m","reset":"\033[0m"},
    "clean":  {"primary":"\033[34m","accent":"\033[36m","muted":"\033[37m","warn":"\033[33m","err":"\033[31m","bold":"\033[1m","reset":"\033[0m"}
}
# default theme
THEME_NAME = os.environ.get("ERALDFORGE_THEME","").lower() or "clean"
if THEME_NAME not in THEMES: THEME_NAME = "clean"
C = THEMES[THEME_NAME]

# Banner (as requested)
BANNER = (
"   ____         __   ______                 \n"
"  / __/______ _/ /__/ / __/__  _______ ____ \n"
" / _// __/ _ `/ / _  / _// _ \\/ __/ _ `/ -_)\n"
"/___/_/  \\_,_/_/\\_,_/_/  \\___/_/  \\_, /\\__/ \n"
"                                 /___/      \n"
)

# translations
STRINGS = {
    "en": {
        "tagline":"✦ Ethical • Modular • Termux-Native ✦",
        "menu_title":"EraldForge Main Menu",
        "update":"Periksa update (git pull)",
        "theme":"Ganti tema",
        "lang":"Ganti bahasa",
        "about":"Tentang EraldForge",
        "exit":"Keluar",
        "prompt":"Pilih nomor atau huruf: ",
        "no_tools":"Tidak ada tool ditemukan di folder 'tools/'.",
        "press_enter":"Tekan Enter untuk kembali...",
        "consent_title":"=== Required consent for security tools ===",
        "consent_prompt":"Type 'yes' to continue: ",
        "consent_denied":"Canceled by user.",
        "invalid":"Pilihan tidak valid.",
        "ok_update":"✔ Update selesai!",
        "no_update":"Tidak ada update baru."
    },
    "id": {
        "tagline":"✦ Ethical • Modular • Termux-Native ✦",
        "menu_title":"Menu Utama EraldForge",
        "update":"Periksa update (git pull)",
        "theme":"Ganti tema",
        "lang":"Ganti bahasa",
        "about":"Tentang EraldForge",
        "exit":"Keluar",
        "prompt":"Pilih nomor atau huruf: ",
        "no_tools":"Tidak ada tool ditemukan di folder 'tools/'.",
        "press_enter":"Tekan Enter untuk kembali...",
        "consent_title":"=== Persetujuan wajib untuk fitur keamanan ===",
        "consent_prompt":"Ketik 'yes' untuk melanjutkan: ",
        "consent_denied":"Dibatalkan oleh pengguna.",
        "invalid":"Pilihan tidak valid.",
        "ok_update":"✔ Update selesai!",
        "no_update":"Tidak ada update baru."
    }
}

# load language setting or ask once
def load_lang():
    if LANG_CFG.exists():
        v = LANG_CFG.read_text().strip()
        if v in ("id","en"): return v
    # ask
    print("Select language / Pilih bahasa:")
    print("1) Bahasa Indonesia")
    print("2) English")
    a = input("Choice [1/2, default 1]: ").strip()
    v = "en" if a=="2" else "id"
    try:
        LANG_CFG.write_text(v)
    except Exception:
        pass
    return v

LANG = load_lang()
S = STRINGS[LANG]

def clear():
    os.system("clear" if os.name!="nt" else "cls")

def animate_startup():
    clear()
    print(C["primary"] + "[BOOT] Initializing EraldForge..." + C["reset"])
    time.sleep(0.25)
    print(C["primary"] + "[BOOT] Scanning tools directory..." + C["reset"])
    time.sleep(0.25)
    print(C["primary"] + "[BOOT] Ready." + C["reset"])
    time.sleep(0.2)

def check_for_updates(auto=False):
    # run git pull
    try:
        subprocess.run(["git","--version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        if not auto:
            print(f"{C['err']}git not available: {e}{C['reset']}")
        return
    try:
        p = subprocess.run(["git","pull"], cwd=str(BASE))
        if p.returncode==0 and not auto:
            print(f"{C['primary']}{S['ok_update']}{C['reset']}")
        elif not auto:
            print(f"{C['warn']}{S['no_update']}{C['reset']}")
    except Exception as e:
        if not auto:
            print(f"{C['err']}git error: {e}{C['reset']}")

def list_tools():
    tools=[]
    if not TOOLS_DIR.exists(): return tools
    for d in sorted(TOOLS_DIR.iterdir()):
        if d.is_dir():
            meta = d / "meta.json"
            info = {"id":d.name, "name":d.name, "desc":"", "entry":None, "security":False, "dir":d}
            if meta.exists():
                try:
                    m=json.load(meta.open())
                    info["name"]=m.get("name", info["name"])
                    info["desc"]=m.get("desc", info["desc"])
                    info["entry"]=m.get("entry", info["entry"])
                    info["security"]=bool(m.get("security", False))
                except Exception:
                    pass
            tools.append(info)
    return tools

def consent_prompt(action_desc, target=None):
    print(C["warn"] + S["consent_title"] + C["reset"])
    print(action_desc)
    if target: print("Target:", target)
    ans = input(C["bold"] + S["consent_prompt"] + C["reset"]).strip().lower()
    if ans=="yes":
        try:
            with open(CONSENT_LOG,"a") as f:
                f.write(f"{datetime.utcnow().isoformat()} | {action_desc} | target={target}\n")
        except Exception:
            pass
        return True
    print(C["err"] + S["consent_denied"] + C["reset"])
    return False

def run_entry(p:Path):
    if not p.exists():
        print(f"{C['err']}Entry file not found: {p}{C['reset']}")
        return
    if p.suffix==".py":
        subprocess.run([sys.executable, str(p)])
    else:
        subprocess.run([str(p)])

def switch_theme():
    global THEME_NAME, C
    print("Available themes:")
    for t in THEMES:
        print("-",t)
    t = input("Choose theme: ").strip().lower()
    if t in THEMES:
        THEME_NAME = t
        C = THEMES[t]
        print(f"Theme changed to {t}.")
    else:
        print("Unknown theme.")

def switch_language():
    global LANG, S
    print("1) Bahasa Indonesia")
    print("2) English")
    c = input("Choose [1/2]: ").strip()
    LANG = "en" if c=="2" else "id"
    S = STRINGS[LANG]
    try:
        LANG_CFG.write_text(LANG)
    except Exception:
        pass
    print("Language saved.")

def about():
    print(f"EraldForge {VERSION}")
    print("Developer: Gerald (G-R4L)")
    print("Repo: https://github.com/G-R4L/EraldForge")
    print("Purpose: Ethical testing & handy Termux utilities")

# menu display (neat, no emoji)
def show_menu(tools):
    now = datetime.now().strftime("%H:%M:%S")
    print(C["accent"] + "        " + S["tagline"] + C["reset"])
    print(C["warn"] + "══════════════════════════════════════════════════════════" + C["reset"])
    print(f"[{now}]  {C['accent']}{S['menu_title']}{C['reset']}")
    print(C["warn"] + "──────────────────────────────────────────────" + C["reset"])
    # show up to first 8 tools mapped 1..8
    for i, t in enumerate(tools[:8], start=1):
        sec = " ⚠" if t["security"] else ""
        name = t["name"]
        desc = t["desc"]
        # align columns: name padded to 22 chars
        print(f"[{i}] {name:<22} {sec}  {desc}")
    print(C["warn"] + "──────────────────────────────────────────────" + C["reset"])
    print(f"[U] {S['update']}")
    print(f"[T] {S['theme']}")
    print(f"[L] {S['lang']}")
    print(f"[A] {S['about']}")
    print(f"[0] {S['exit']}")
    print(C["warn"] + "══════════════════════════════════════════════════════════" + C["reset"])

def main():
    animate_start = True
    animate_startup()
    check_for_updates(auto=True)
    while True:
        clear()
        tools = list_tools()
        if not tools:
            print(C["err"] + S["no_tools"] + C["reset"])
            input(S["press_enter"])
            break
        show_menu(tools)
        choice = input("\n" + S["prompt"]).strip().lower()
        if choice in ("0","q","exit"):
            print("Goodbye.")
            break
        if choice == "u":
            check_for_updates(); input(S["press_enter"]); continue
        if choice == "t":
            switch_theme(); input(S["press_enter"]); continue
        if choice == "l":
            switch_language(); input(S["press_enter"]); continue
        if choice == "a":
            about(); input(S["press_enter"]); continue
        # numeric tool selection
        try:
            idx = int(choice) - 1
            if idx < 0 or idx >= len(tools[:8]):
                print(C["err"] + S["invalid"] + C["reset"]); input(S["press_enter"]); continue
            tool = tools[idx]
            if tool["security"]:
                target = input("Enter target (IP/domain) or leave blank: ").strip() or None
                if not consent_prompt(tool["desc"], target):
                    input(S["press_enter"]); continue
                os.environ["ERALDFORGE_TARGET"] = target or ""
            entry = tool["dir"] / (tool["entry"] or "")
            if not entry.exists():
                print(C["err"] + "Entry not found: " + str(entry) + C["reset"])
                input(S["press_enter"])
                continue
            run_entry(entry)
            input(S["press_enter"])
        except ValueError:
            print(C["err"] + S["invalid"] + C["reset"])
            input(S["press_enter"])

if __name__ == "__main__":
    main()
