#!/data/data/com.termux/files/usr/bin/env python3
import subprocess, json, sys

def wifi_scan():
    try:
        out = subprocess.check_output(["termux-wifi-scaninfo"]).decode()
        try:
            data = json.loads(out)
            return data
        except:
            return out
    except Exception as e:
        return f"Error running termux-wifi-scaninfo: {e}"

def main():
    print("WiFi Info (readonly) — memindai jaringan terdekat...")
    res = wifi_scan()
    if isinstance(res, str):
        print(res)
        return
    if isinstance(res, list):
        for ap in res:
            ssid = ap.get("SSID") or ap.get("ssid")
            bssid = ap.get("BSSID") or ap.get("bssid")
            level = ap.get("level", ap.get("rssi", "n/a"))
            print(f"SSID: {ssid} | BSSID: {bssid} | level: {level}")
    else:
        print(res)

if __name__ == "__main__":
    main()
