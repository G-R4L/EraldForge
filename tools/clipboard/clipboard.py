#!/data/data/com.termux/files/usr/bin/env python3
import subprocess, sys, json, os
from pathlib import Path

HIST_FILE = Path.home() / ".eraldforge_clipboard.json"

def get_clip():
    try:
        return subprocess.check_output(["termux-clipboard-get"]).decode()
    except Exception as e:
        return None

def set_clip(text):
    try:
        subprocess.run(["termux-clipboard-set", text])
        return True
    except Exception:
        return False

def load_hist():
    if not HIST_FILE.exists():
        return []
    try:
        return json.load(HIST_FILE.open())
    except:
        return []

def save_hist(hist):
    json.dump(hist, HIST_FILE.open("w"), indent=2)

def main():
    print("Clipboard Manager — pilih:")
    print("1. Save current clipboard to history")
    print("2. Show history")
    print("3. Copy entry from history to clipboard")
    print("0. Exit")
    c = input("Pilihan: ").strip()
    hist = load_hist()
    if c == "1":
        txt = get_clip()
        if not txt:
            print("Gagal membaca clipboard atau clipboard kosong.")
            return
        hist.insert(0, {"text": txt, "ts": __import__('time').time()})
        hist = hist[:50]
        save_hist(hist)
        print("Tersimpan.")
    elif c == "2":
        for i, it in enumerate(hist):
            print(f"{i}. {it['text'][:120].replace('\n',' ')}")
    elif c == "3":
        try:
            idx = int(input("Index: ").strip() or "0")
        except Exception:
            print("Index tidak valid.")
            return
        if idx < 0 or idx >= len(hist):
            print("Index tidak valid.")
            return
        ok = set_clip(hist[idx]['text'])
        print("Copied." if ok else "Gagal.")
    else:
        print("Bye.")

if __name__ == "__main__":
    main()
