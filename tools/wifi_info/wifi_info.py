#!/data/data/com.termux/files/usr/bin/env python3
# EraldForge - WiFi Info (upgraded)
import os, json, subprocess
from pathlib import Path

def theme():
    t=os.environ.get("ERALDFORGE_THEME","").lower()
    if t in ("hacker","clean"): return t
    t=input("Tema [hacker/clean] (default clean): ").strip().lower()
    return t if t in ("hacker","clean") else "clean"

THEME=theme()
if THEME=="hacker":
    G="\033[32m"; W="\033[0m"; Y="\033[33m"
else:
    G="\033[34m"; W="\033[0m"; Y="\033[33m"

def run_scan():
    try:
        out=subprocess.check_output(["termux-wifi-scaninfo"], stderr=subprocess.DEVNULL).decode()
        data=json.loads(out)
        return data
    except Exception as e:
        return str(e)

def main():
    print(G+"EraldForge WiFi Info"+W)
    res=run_scan()
    if isinstance(res,str):
        print("Error or termux-wifi-scaninfo not available:", res); return
    for ap in res:
        ssid=ap.get("SSID") or ap.get("ssid") or "-"
        bssid=ap.get("BSSID") or ap.get("bssid") or "-"
        level=ap.get("level",ap.get("rssi","n/a"))
        freq=ap.get("frequency","-")
        print(f"{G}SSID:{W} {ssid}  {G}BSSID:{W} {bssid}  {G}level:{W} {level}  {G}freq:{W} {freq}")

if __name__=="__main__":
    main()
