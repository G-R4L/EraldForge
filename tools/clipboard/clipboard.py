#!/data/data/com.termux/files/usr/bin/env python3
# EraldForge - Clipboard (upgraded)
import os, json, subprocess
from pathlib import Path
HOME=Path.home()
HFILE=HOME/".eraldforge_clipboard.json"

def get_theme():
    t=os.environ.get("ERALDFORGE_THEME","").lower()
    if t in ("hacker","clean"): return t
    t=input("Tema [hacker/clean] (default hacker): ").strip().lower()
    return t if t in ("hacker","clean") else "hacker"
THEME=get_theme()
if THEME=="hacker":
    G="\033[32m"; W="\033[0m"; Y="\033[33m"; R="\033[31m"
else:
    G="\033[34m"; W="\033[0m"; Y="\033[33m"; R="\033[31m"

def load_hist():
    if not HFILE.exists(): return []
    try: return json.loads(HFILE.read_text())
    except: return []

def save_hist(h):
    try: HFILE.write_text(json.dumps(h,indent=2))
    except: pass

def get_clip():
    try:
        out=subprocess.check_output(["termux-clipboard-get"]).decode()
        return out
    except Exception as e:
        return None

def set_clip(text):
    try:
        subprocess.run(["termux-clipboard-set", text])
        return True
    except:
        return False

def main():
    print(G+"EraldForge Clipboard Manager"+W)
    hist=load_hist()
    print("1) Save current clipboard  2) List history  3) Paste item to clipboard  4) Search  0) Exit")
    c=input("Pilihan: ").strip()
    if c=="1":
        txt=get_clip()
        if not txt:
            print(R+"Clipboard kosong atau tidak tersedia"+W); return
        hist.insert(0,{"text":txt,"ts":int(__import__("time").time())})
        hist=hist[:200]; save_hist(hist)
        print(G+"Tersimpan."+W); return
    if c=="2":
        for i,it in enumerate(hist[:100],start=1):
            t=it.get("text","").replace("\n"," ")
            print(f"{i}. {t[:120]}")
        return
    if c=="3":
        idx=int(input("Index: ").strip() or "1")-1
        if idx<0 or idx>=len(hist): print(R+"Index invalid"+W); return
        ok=set_clip(hist[idx]["text"])
        print(G+"Copied."+W if ok else R+"Fail"+W); return
    if c=="4":
        q=input("Query: ").strip().lower()
        for i,it in enumerate(hist, start=1):
            if q in it.get("text","").lower():
                print(i, it.get("text")[:200].replace("\n"," "))
        return
    print("Bye")

if __name__=="__main__":
    main()
