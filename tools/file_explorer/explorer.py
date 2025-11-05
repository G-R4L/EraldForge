#!/data/data/com.termux/files/usr/bin/env python3
# EraldForge - File Explorer (upgraded)
import os, shutil, stat, zipfile
from pathlib import Path
HOME=Path.home()

def theme():
    t=os.environ.get("ERALDFORGE_THEME","").lower()
    if t in ("hacker","clean"): return t
    t=input("Tema [hacker/clean] (default clean): ").strip().lower()
    return t if t in ("hacker","clean") else "clean"
THEME=theme()
if THEME=="hacker":
    G="\033[32m"; W="\033[0m"; Y="\033[33m"; R="\033[31m"
else:
    G="\033[34m"; W="\033[0m"; Y="\033[33m"; R="\033[31m"

def human(n):
    for unit in ('B','KB','MB','GB'):
        if n<1024: return f"{n:.0f}{unit}"
        n/=1024
    return f"{n:.1f}TB"

def list_dir(p):
    p=Path(p).expanduser()
    if not p.exists(): return []
    items=sorted(p.iterdir(), key=lambda x:(not x.is_dir(), x.name.lower()))
    res=[]
    for it in items:
        typ="<DIR>" if it.is_dir() else human(it.stat().st_size)
        res.append((it.name, typ, it))
    return res

def preview(path):
    try:
        with open(path,"rb") as f:
            data=f.read(4096)
            try: print(data.decode(errors="replace"))
            except: print(data)
    except Exception as e:
        print("Cannot open:",e)

def zip_folder(src):
    src=Path(src)
    if not src.exists(): print("Not found"); return
    out=str(src.name)+".zip"
    shutil.make_archive(str(src), 'zip', root_dir=str(src))
    print("Created", out)

def main():
    cwd=HOME
    while True:
        print(G+f"Current: {cwd}"+W)
        items=list_dir(cwd)
        for i,(n,s,_) in enumerate(items, start=1):
            print(f"{i}. {n} ({s})")
        print("u=up, z=zip, c=copy, m=move, p=preview, q=quit")
        cmd=input("Choice/name: ").strip()
        if cmd in ("q","quit"): break
        if cmd=="u": cwd=cwd.parent; continue
        if cmd=="z":
            name=input("Folder name: ").strip()
            zip_folder(cwd/name); continue
        if cmd=="c":
            src=input("Source (relative): ").strip(); dst=input("Dest (relative): ").strip()
            try:
                shutil.copy(cwd/src, cwd/dst); print("Copied")
            except Exception as e: print("Err:",e)
            continue
        if cmd=="m":
            src=input("Source (relative): ").strip(); dst=input("Dest (relative): ").strip()
            try:
                shutil.move(str(cwd/src), str(cwd/dst)); print("Moved")
            except Exception as e: print("Err:",e)
            continue
        if cmd=="p":
            target=input("File name: ").strip()
            t=cwd/target
            if t.exists() and t.is_file(): preview(t); input("Enter to continue")
            else: print("Not found")
            continue
        # numeric
        try:
            idx=int(cmd)-1
            if idx<0 or idx>=len(items): print("Invalid"); continue
            entry=items[idx][2]
            if entry.is_dir(): cwd=entry
            else: preview(entry); input("Enter to continue")
        except:
            p=cwd/cmd
            if p.exists():
                if p.is_dir(): cwd=p
                else: preview(p); input("Enter to continue")
            else:
                print("Not found")
if __name__=="__main__":
    main()
