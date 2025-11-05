#!/data/data/com.termux/files/usr/bin/env python3
"""
EraldForge - Launcher utama
Usage: eraldforge
"""
import os
import json
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
TOOLS_DIR = BASE / "tools"
CONSENT_LOG = Path.home() / ".eraldforge_consent.log"

def list_tools():
    tools = []
    if not TOOLS_DIR.exists():
        return tools
    for d in sorted(TOOLS_DIR.iterdir()):
        if d.is_dir():
            meta = d / "meta.json"
            if meta.exists():
                try:
                    m = json.load(meta.open())
                    tools.append((d.name, m.get("name", d.name), m.get("desc","")))
                except Exception:
                    tools.append((d.name, d.name, ""))
            else:
                tools.append((d.name, d.name, ""))
    return tools

def run_tool(tool_dir):
    meta_path = tool_dir / "meta.json"
    entry = None
    if meta_path.exists():
        meta = json.load(meta_path.open())
        entry = meta.get("entry")
    if not entry:
        print("Entry script not found in meta.json.")
        return
    entry_path = tool_dir / entry
    if not entry_path.exists():
        print(f"Entry file {entry} missing.")
        return
    # If python script
    if entry_path.suffix in (".py",):
        subprocess.run([sys.executable, str(entry_path)])
    else:
        subprocess.run([str(entry_path)])

def consent_prompt(action_desc, target=None):
    print("\n=== Persetujuan wajib untuk fitur security ===")
    print("Anda akan menjalankan:", action_desc)
    if target:
        print("Target:", target)
    print("Pastikan Anda punya izin eksplisit untuk melakukan tindakan ini.")
    ans = input("Ketik 'yes' untuk melanjutkan: ").strip().lower()
    if ans == "yes":
        with open(CONSENT_LOG, "a") as f:
            f.write(f"{__import__('datetime').datetime.utcnow().isoformat()} | {action_desc} | target={target}\n")
        return True
    print("Dibatalkan oleh pengguna.")
    return False

def main():
    tools = list_tools()
    if not tools:
        print("Tidak ada tools ditemukan di folder 'tools/'.")
        return
    print("=== EraldForge Launcher ===")
    for i,(idn,name,desc) in enumerate(tools, start=1):
        print(f"{i}. {name} — {desc}")
    print("0. Keluar")
    try:
        choice = int(input("Pilih nomor: ").strip())
    except Exception:
        print("Input tidak valid.")
        return
    if choice == 0:
        print("Bye.")
        return
    if 1 <= choice <= len(tools):
        tool_id = tools[choice-1][0]
        tool_dir = TOOLS_DIR / tool_id
        # check meta for security flag
        meta = {}
        mfile = tool_dir / "meta.json"
        if mfile.exists():
            meta = json.load(mfile.open())
        if meta.get("security", False):
            # security tool requires consent
            desc = meta.get("desc","(no desc)")
            target = input("Masukkan target (IP/domain) atau kosong: ").strip() or None
            if not consent_prompt(desc, target):
                return
            # pass target to tool via env var
            os.environ["ERALDFORGE_TARGET"] = target or ""
        run_tool(tool_dir)
    else:
        print("Pilihan di luar jangkauan.")

if __name__ == "__main__":
    main()
