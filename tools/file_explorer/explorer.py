#!/data/data/com.termux/files/usr/bin/env python3
import os, sys, shutil
from pathlib import Path

def list_dir(p):
    p = Path(p).expanduser()
    if not p.exists(): return []
    res = []
    for it in sorted(p.iterdir()):
        t = "<DIR>" if it.is_dir() else it.stat().st_size
        res.append((it.name, t))
    return res

def main():
    cwd = Path.home()
    while True:
        print(f"\nCurrent: {cwd}")
        for i,(n,s) in enumerate(list_dir(cwd), start=1):
            print(f"{i}. {n} ({s})")
        print("u. up, z. zip folder, q. quit")
        cmd = input("Choice/name: ").strip()
        if cmd == "q": break
        if cmd == "u":
            cwd = cwd.parent
            continue
        if cmd == "z":
            name = input("Folder name to zip (relative): ").strip()
            if not name: continue
            target = cwd / name
            if not target.exists():
                print("Not found.")
                continue
            out = str(target.name)+".zip"
            shutil.make_archive(str(target), 'zip', root_dir=str(target))
            print("Created", out)
            continue
        # try numeric
        try:
            idx = int(cmd)-1
            items = list_dir(cwd)
            if idx < 0 or idx >= len(items):
                print("Invalid index")
                continue
            name = items[idx][0]
            path = cwd / name
            if path.is_dir():
                cwd = path
            else:
                print("--- File content preview (first 4KB) ---")
                print(path.open("rb").read(4096))
        except ValueError:
            # try direct name
            path = cwd / cmd
            if path.exists():
                if path.is_dir():
                    cwd = path
                else:
                    print("--- File content preview (first 4KB) ---")
                    print(path.open("rb").read(4096))
            else:
                print("Not found.")
if __name__ == "__main__":
    main()
