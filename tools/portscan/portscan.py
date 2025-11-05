#!/data/data/com.termux/files/usr/bin/env python3
import os, subprocess, sys

TARGET = os.environ.get("ERALDFORGE_TARGET","").strip()

def check_nmap():
    try:
        subprocess.check_output(["nmap","--version"])
        return True
    except Exception:
        return False

def run_scan(target):
    if not check_nmap():
        print("nmap tidak ditemukan. Install dengan 'pkg install nmap'.")
        return
    print(f"Menjalankan nmap scan ringan pada {target} (TCP SYN top ports)...")
    cmd = ["nmap", "-Pn", "-sS", "--top-ports", "100", "-oN", "-"]
    cmd.append(target)
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("Dibatalkan.")
    except Exception as e:
        print("Error:", e)

def main():
    global TARGET
    if not TARGET:
        TARGET = input("Masukkan target IP atau domain: ").strip()
    if not TARGET:
        print("Tidak ada target.")
        return
    # Double-check user consent already logged by launcher; still reconfirm
    ans = input(f"Anda yakin ingin memindai {TARGET}? (yes/no): ").strip().lower()
    if ans != "yes":
        print("Batal.")
        return
    run_scan(TARGET)

if __name__ == "__main__":
    main()
