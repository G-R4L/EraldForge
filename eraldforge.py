#!/data/data/com.termux/files/usr/bin/env python3
"""
EraldForge - Termux Multi-Tool Launcher
By Gerald (G-R4L)
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).resolve().parent
TOOLS_DIR = BASE / "tools"
CONSENT_LOG = Path.home() / ".eraldforge_consent.log"

# ANSI colors
C = {
    "r": "\033[31m",  # merah
    "g": "\033[32m",  # hijau
    "y": "\033[33m",  # kuning
    "b": "\033[34m",  # biru
    "c": "\033[36m",  # cyan
    "w": "\033[37m",  # putih
    "reset": "\033[0m",
    "bold": "\033[1m"
}

# Banner warna custom
BANNER = rf"""
{C['r']}   ___                      _        _      {C['b']}___                    __ _          
{C['r']}  | __|     _ _   __ _     | |    __| |    {C['b']}| __|   ___      _ _   / _` |   ___   
{C['r']}  | _|     | '_| / _` |    | |   / _` |    {C['b']}| _|   / _ \    | '_|  \__, |  / -_)  
{C['r']}  |___|   _|_|_  \__,_|   _|_|_  \__,_|   {C['b']}_|_|_   \___/   _|_|_   |___/   \___|  
{C['y']}_|"""""|_|"""""|_|"""""|_|"""""|_|"""""|_| """ |_|"""""|_|"""""|_|"""""|_|"""""|_|"""""| 
{C['y']}"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-' 
{C['reset']}
"""

def clear():
    os.system("clear" if os.name != "nt" else "cls")

def print_banner():
    clear()
    print(BANNER)
    print(f"{C['c']}         ✦ Ethical • Modular • Termux-Native ✦{C['reset']}")
    print(f"{C['y']}══════════════════════════════════════════════════════════{C['reset']}\n")

def list_tools():
    tools = []
    if not TOOLS_DIR.exists():
        return tools
    for d in sorted(TOOLS_DIR.iterdir()):
        if d.is_dir():
            meta = d / "meta.json"
            name = d.name
            desc = ""
            security = False
            entry = None
            if meta.exists():
                try:
                    m = json.load(meta.open())
                    name = m.get("name", name)
                    desc = m.get("desc", "")
                    entry = m.get("entry")
                    security = bool(m.get("security", False))
                except Exception:
                    pass
            tools.append({
                "id": d.name, "name": name, "desc": desc,
                "dir": d, "entry": entry, "security": security
            })
    return tools

def run_entry(script_path):
    script = str(script_path)
    if script_path.suffix == ".py":
        return subprocess.run([sys.executable, script])
    else:
        return subprocess.run([script])

def consent_prompt(action_desc, target=None):
    print(C["y"] + "\n=== Persetujuan wajib untuk fitur security ===" + C["reset"])
    print("Anda akan menjalankan:", action_desc)
    if target:
        print("Target:", target)
    print("Pastikan Anda memiliki izin eksplisit untuk tindakan ini.")
    ans = input(C["bold"] + "Ketik 'yes' untuk melanjutkan: " + C["reset"]).strip().lower()
    if ans == "yes":
        with open(CONSENT_LOG, "a") as f:
            f.write(f"{datetime.utcnow().isoformat()} | {action_desc} | target={target}\n")
        return True
    print("❌ Dibatalkan oleh pengguna.")
    return False

def check_for_updates():
    print(f"{C['c']}Checking for updates from GitHub...{C['reset']}")
    try:
        subprocess.run(["git", "--version"], check=True, stdout=subprocess.DEVNULL)
    except Exception as e:
        print(f"{C['r']}git tidak tersedia: {e}{C['reset']}")
        return
    try:
        p = subprocess.run(["git", "pull"], cwd=str(BASE))
        if p.returncode == 0:
            print(f"\n{C['g']}✔ Update selesai! Jalankan ulang EraldForge jika ada perubahan.{C['reset']}")
        else:
            print(f"\n{C['y']}Tidak ada update baru atau pull gagal.{C['reset']}")
    except Exception as e:
        print(f"{C['r']}Error saat git pull: {e}{C['reset']}")

def show_menu(tools):
    now = datetime.now().strftime("%H:%M:%S")
    print(f"{C['b']}[{now}] {C['c']}EraldForge Main Menu{C['reset']}")
    print(f"{C['y']}──────────────────────────────────────────────{C['reset']}")
    for i, t in enumerate(tools, start=1):
        sec = f"{C['r']}⚠{C['reset']}" if t['security'] else ""
        print(f"{C['g']}[{i}] {C['bold']}{t['name']}{C['reset']} {sec}")
        print(f"    {C['w']}{t['desc']}{C['reset']}")
        print(f"{C['y']}──────────────────────────────────────────────{C['reset']}")
    print(f"{C['b']}[U]{C['reset']} Periksa update (git pull)")
    print(f"{C['r']}[0]{C['reset']} Keluar")
    print(f"{C['y']}══════════════════════════════════════════════════════════{C['reset']}")

def main():
    while True:
        print_banner()
        tools = list_tools()
        if not tools:
            print(f"{C['r']}Tidak ada tool ditemukan di folder /tools.{C['reset']}")
            input(f"{C['w']}Tekan Enter untuk keluar...{C['reset']}")
            break

        show_menu(tools)
        choice = input(f"\n{C['bold']}Pilih nomor atau huruf: {C['reset']}").strip()
        if choice in ("0", "q", "exit"):
            print(f"{C['y']}Sampai jumpa di EraldForge!{C['reset']}")
            break
        if choice.lower() == "u":
            check_for_updates()
            input(f"\n{C['w']}Tekan Enter untuk kembali...{C['reset']}")
            continue

        try:
            idx = int(choice) - 1
            if idx < 0 or idx >= len(tools):
                print(f"{C['r']}Pilihan tidak valid.{C['reset']}")
                input("Enter untuk lanjut...")
                continue
            t = tools[idx]
            if t["security"]:
                target = input("Masukkan target (IP/domain) atau kosong: ").strip() or None
                if not consent_prompt(t["desc"], target):
                    input("Enter untuk kembali...")
                    continue
                os.environ["ERALDFORGE_TARGET"] = target or ""
            entry = t.get("entry")
            if not entry:
                print("Tool ini tidak punya entry di meta.json")
                input("Enter untuk kembali...")
                continue
            entry_path = t["dir"] / entry
            if not entry_path.exists():
                print("File entry tidak ditemukan:", entry_path)
                input("Enter untuk kembali...")
                continue
            run_entry(entry_path)
            input(f"\n{C['y']}Tekan Enter untuk kembali ke menu...{C['reset']}")
        except ValueError:
            print(f"{C['r']}Input tidak dikenali.{C['reset']}")
            input("Enter untuk lanjut...")

if __name__ == "__main__":
    main()
