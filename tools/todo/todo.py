#!/usr/bin/env python3
# EraldForge - Todo Manager (Pro Edition)
# Ditingkatkan untuk estetika yang lebih baik, status berkode warna, dan tampilan CLI modern.

import json
import os
import sys
from pathlib import Path

# ---------------- Konfigurasi & Jalur File ----------------
# Menggunakan Path.home() untuk mendapatkan direktori home user.
HOME = Path.home()
# File akan disimpan di direktori home, misalnya: /data/data/com.termux/files/home/.eraldforge_todo.json
FILE = HOME / ".eraldforge_todo.json"

# ---------------- Warna & Gaya ANSI ----------------
C_NEON = "\033[93m"    # Neon Yellow (Banner, Prioritas Tinggi)
C_BOX  = "\033[96m"    # Cyan (Box/Header)
G     = "\033[32m"     # Green (Status SELESAI)
R     = "\033[91m"     # Red (HAPUS / Prioritas Tinggi)
Y     = "\033[33m"     # Yellow (Teks Umum, Prioritas Sedang)
W     = "\033[0m"      # Reset
BOLD  = "\033[1m"
DIM   = "\033[2m"     # Redup (Untuk tugas yang sudah selesai)

# ---------------- Banner ASCII ----------------
BANNER_LINES = [
    C_NEON + "·························" + W,
    C_NEON + ": " + BOLD + "_____         _       " + W + C_NEON + ":" + W,
    C_NEON + ": " + BOLD + "|_   _|__   __| | ___  " + W + C_NEON + ":" + W,
    C_NEON + ": " + BOLD + "  | |/ _ \\ / _` |/ _ \\ " + W + C_NEON + ":" + W,
    C_NEON + ": " + BOLD + "  | | (_) | (_| | (_) |" + W + C_NEON + ":" + W,
    C_NEON + ": " + BOLD + "  |_|\\___/ \\__,_|\\___/ " + W + C_NEON + ":" + W,
    C_NEON + "·························" + W,
]

def print_banner():
    """Mencetak banner dan header utama aplikasi."""
    # os.system("clear") # Dikomentari agar tidak menghapus output di Canvas
    for line in BANNER_LINES:
        print(line)
    print(C_BOX + BOLD + "EraldForge Todo Manager (Pro Edition)" + W)
    print(C_BOX + "══════════════════════════════════════════" + W)

# ---------------- Fungsi Data Inti ----------------
def load():
    """Memuat data todo dari file JSON."""
    try:
        if FILE.exists():
            # Mengembalikan list of dictionaries
            return json.loads(FILE.read_text(encoding='utf-8'))
    except json.JSONDecodeError:
        print(f"{R}Error: File JSON rusak. Membuat ulang list kosong.{W}")
    except Exception:
        pass
    return []

def save(data):
    """Menyimpan data todo ke file JSON."""
    try:
        FILE.write_text(json.dumps(data, indent=2), encoding='utf-8')
    except Exception as e:
        print(f"{R}Error menyimpan data: {e}{W}")

# ---------------- Fungsi Tampilan (Estetika) ----------------
def get_prio_style(pr):
    """Memberikan warna dan padding 4 karakter berdasarkan prioritas."""
    pr = pr.lower().strip()
    if pr == "high":
        return BOLD + R, "HIGH"
    elif pr == "low":
        return DIM + C_BOX, "LOW "
    else:
        return Y, "MED "

def show(data):
    """Menampilkan daftar tugas dengan tata letak profesional dan warna yang rata."""
    if not data:
        print(C_BOX + "══════════════════════════════════════════" + W)
        print(Y + "🎉 Semua tugas selesai atau belum ada tugas. Selamat!" + W)
        print(C_BOX + "══════════════════════════════════════════" + W)
        return
        
    print(C_BOX + BOLD + f"\n===== DAFTAR TUGAS ({len(data)} TOTAL) =====" + W)
    # Header alignment: No(2) | Prio(4) | Due Date(10) | Status(6) | Tugas
    print(f"{C_BOX}No | Prio | Due Date | Status | Tugas{W}")
    print(C_BOX + "---+------+----------+--------+--------------------------" + W)

    for i, t in enumerate(data, start=1):
        is_done = t.get("done", False)
        
        # 1. Prioritas (4 karakter)
        pr_color, pr_text = get_prio_style(t.get("priority", "med"))
        pr_display = pr_color + pr_text + W
        
        # 2. Due Date (10 karakter)
        due = t.get("due", "-").ljust(10)
        
        # 3. Status (Dibuat 6 karakter visual agar rata)
        if is_done:
            # Menggunakan 6 karakter visual
            status_text = f"{G}√ DONE{W}"
            task_color = DIM # Selesai, teks diredupkan
        else:
            # Menggunakan 6 karakter visual
            status_text = f"{Y} TODO {W}"
            task_color = W # Belum, teks normal
        
        # Output baris
        # Catatan: Padding ljust() hanya bekerja pada karakter non-ANSI.
        # Karena itu, kita pastikan isi string non-ANSI (nomor) sudah rata.
        print(f"{C_BOX}{str(i).ljust(2)}{W} | {pr_display} | {due} | {status_text} | {task_color}{t.get('task')}{W}")

    print(C_BOX + "══════════════════════════════════════════" + W)


# ---------------- Loop Interaksi Utama ----------------
def main():
    print_banner()
    while True:
        try:
            data = load()
            show(data)
            
            # Menu Pilihan
            print(f"\n{C_BOX}{BOLD}PILIHAN:{W} {G}a{W}:add, {G}t{W}:toggle, {G}e{W}:edit, {R}d{W}:delete, {C_NEON}q{W}:quit")
            cmd = input(f"{C_BOX}▶ Pilihan Anda: {W}").strip().lower()

            if cmd == "a":
                # Tambah
                task = input(f"{G}Task:{W} ").strip()
                if not task: continue
                pr = input(f"{Y}Priority (low/med/high) [med]:{W} ").strip() or "med"
                due = input(f"{Y}Due (YYYY-MM-DD) [blank]:{W} ").strip()
                data.append({"task": task, "priority": pr.lower(), "due": due, "done": False})
                save(data)
                print(f"{G}Task '{task}' ditambahkan.{W}")
                
            elif cmd == "t":
                # Toggle
                raw_idx = input(f"{G}Nomor tugas untuk di-toggle:{W} ").strip()
                try: idx = int(raw_idx) - 1
                except ValueError: print(f"{R}Input harus angka.{W}"); continue
                
                if 0 <= idx < len(data):
                    data[idx]["done"] = not data[idx].get("done", False)
                    save(data)
                    status = "DONE" if data[idx]["done"] else "TODO"
                    print(f"{G}Status tugas {idx+1} diubah menjadi {status}.{W}")
                else: print(f"{R}Indeks tidak valid.{W}")
                
            elif cmd == "e":
                # Edit
                raw_idx = input(f"{G}Nomor tugas untuk di-edit:{W} ").strip()
                try: idx = int(raw_idx) - 1
                except ValueError: print(f"{R}Input harus angka.{W}"); continue
                
                if 0 <= idx < len(data):
                    current = data[idx]
                    print(f"{C_BOX}Mengedit Tugas {idx+1}: '{current['task']}'{W}")
                    current["task"] = input(f"Task baru [{current['task']}]: ").strip() or current["task"]
                    # Pastikan prioritas yang dimasukkan valid, jika tidak, gunakan yang lama
                    new_prio = input(f"Priority baru [{current['priority']}]: ").strip().lower()
                    if new_prio in ["low", "med", "high"] or not new_prio:
                        current["priority"] = new_prio or current["priority"]
                    else:
                        print(f"{R}Prioritas tidak valid, menggunakan prioritas lama: {current['priority']}{W}")
                    
                    current["due"] = input(f"Due baru [{current['due']}]: ").strip() or current["due"]
                    save(data)
                    print(f"{G}Tugas {idx+1} berhasil diperbarui.{W}")
                else: print(f"{R}Indeks tidak valid.{W}")
                
            elif cmd == "d":
                # Delete
                raw_idx = input(f"{R}Nomor tugas untuk di-HAPUS:{W} ").strip()
                try: idx = int(raw_idx) - 1
                except ValueError: print(f"{R}Input harus angka.{W}"); continue
                
                if 0 <= idx < len(data):
                    task_name = data[idx]["task"]
                    data.pop(idx)
                    save(data)
                    print(f"{R}Tugas '{task_name}' Dihapus.{W}")
                else: print(f"{R}Indeks tidak valid.{W}")
                
            elif cmd in ("q", "quit", "exit"):
                print(f"{C_NEON}Keluar dari EraldForge Todo. Sampai jumpa!{W}")
                break
            else:
                # Ini akan dipicu jika user memasukkan "5"
                print(f"{R}Pilihan tidak dikenal. Masukkan a, t, e, d, atau q.{W}")
                
        except EOFError:
            print(f"\n{C_NEON}Keluar dari EraldForge Todo.{W}")
            sys.exit(0)
        except Exception as e:
            print(f"{R}Terjadi error tak terduga: {e}{W}")

if __name__ == "__main__":
    main()