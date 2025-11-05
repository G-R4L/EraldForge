#!/data/data/com.termux/files/usr/bin/env python3
# EraldForge - Port Scanner (upgraded)
import os, subprocess, socket, sys, time
from concurrent.futures import ThreadPoolExecutor

TARGET=os.environ.get("ERALDFORGE_TARGET","").strip()

def theme(): t=os.environ.get("ERALDFORGE_THEME","").lower(); return t if t in ("hacker","clean") else "hacker"
THEME=theme()
if THEME=="hacker": G="\033[32m"; W="\033[0m"; Y="\033[33m"; R="\033[31m"
else: G="\033[34m"; W="\033[0m"; Y="\033[33m"; R="\033[31m"

def has_nmap():
    try:
        subprocess.run(["nmap","--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except: return False

def run_nmap(tgt, args):
    cmd=["nmap","-Pn","-sS","--top-ports","200"]+args+[tgt]
    print(G+"Running: "+" ".join(cmd)+W)
    subprocess.run(cmd)

def socket_scan(tgt, ports, timeout=0.5):
    open_ports=[]
    def scan_port(p):
        try:
            s=socket.socket()
            s.settimeout(timeout)
            s.connect((tgt,p))
            s.close()
            return p
        except: return None
    with ThreadPoolExecutor(max_workers=100) as ex:
        for res in ex.map(scan_port, ports):
            if res: open_ports.append(res)
    return sorted(open_ports)

def main():
    global TARGET
    print(G+"EraldForge Port Scanner"+W)
    if not TARGET:
        TARGET=input("Masukkan target IP/domain: ").strip()
    if not TARGET:
        print(R+"No target"); return
    if has_nmap():
        print("Detected nmap -> using nmap")
        run_nmap(TARGET,[])
    else:
        print("nmap not found -> fallback to socket scan (top ports)")
        top=[22,80,443,21,23,25,53,110,143,445,3389,3306,8080, uranium_port if False else 0]  # keep small list
        # adjust to sensible default:
        top=[22,80,443,21,23,25,53,110,143,445,3389,3306,8080]
        print("Scanning (this may take a while)...")
        opens=socket_scan(TARGET, top)
        if opens:
            print(G+"Open ports: "+",".join(map(str,opens))+W)
        else:
            print(Y+"No open top ports found"+W)

if __name__=="__main__":
    main()
