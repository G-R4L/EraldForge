#!/data/data/com.termux/files/usr/bin/env python3
# EraldForge - Todo Manager (Pro Edition - Complete)
# Upgraded for 8 features, including Filter/Sort, Refresh, and Clear Completed.

import json
import os
import sys
from pathlib import Path
from datetime import datetime

# ---------------- Configuration & File Paths ----------------
HOME = Path.home()
FILE = HOME / ".eraldforge_todo.json"
# Global state for filtering
CURRENT_FILTER = "all" # 'all', 'high', 'med', 'low', 'done', 'todo'

# ---------------- Colors & Style ----------------
C_NEON = "\033[93m"     # Neon Yellow (Banner, High Priority)
C_BOX  = "\033[96m"     # Cyan (Box/Headers - Dibuat kontras dengan banner)
G      = "\033[32m"     # Green (DONE status)
R      = "\033[91m"     # Red (DELETE / WARNING)
Y      = "\033[33m"     # Yellow (General Text, Medium Priority)
W      = "\033[0m"      # Reset
BOLD   = "\033[1m"
DIM    = "\033[2m"      # Dim (For completed tasks)

# ---------------- Banner ASCII (KUNING NEON KESELURUHAN) ----------------
# Menggunakan C_NEON (Kuning Neon) untuk semua elemen visual banner
# Panjang total setiap baris adalah 25 karakter.
BANNER_LINES = [
    C_NEON + "·························" + W,
    C_NEON + ":" + BOLD + C_NEON + " _____         _       " + W + C_NEON + ":" + W,
    C_NEON + ":" + BOLD + C_NEON + "|_   _|__   __| | ___  " + W + C_NEON + ":" + W,
    C_NEON + ":" + BOLD + C_NEON + "  | |/ _ \ / _` |/ _ \ " + W + C_NEON + ":" + W,
    C_NEON + ":" + BOLD + C_NEON + "  | | (_) | (_| | (_) |" + W + C_NEON + ":" + W,
    C_NEON + ":" + BOLD + C_NEON + "  |_|\___/ \__,_|\___/ " + W + C_NEON + ":" + W,
    C_NEON + "·························" + W,
]

def print_banner():
    """Mencetak banner dan header utama aplikasi."""
    os.system("clear")
    for line in BANNER_LINES:
        print(line)
    # Header di bawah banner tetap menggunakan C_BOX (Cyan) agar kontras
    print(C_BOX + BOLD + "EraldForge Todo Manager (Pro Edition)" + W)
    print(C_BOX + "══════════════════════════════════════════" + W)

# ---------------- Core Data Functions ----------------
def load():
    """Memuat data todo dari file JSON."""
    try:
        if FILE.exists():
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

# ---------------- New Feature: Clean Done Tasks ----------------
def clean_done_tasks(data):
    """Menghapus semua tugas yang ditandai 'done'."""
    initial_count = len(data)
    # Filter tugas yang TIDAK selesai (done=False)
    updated_data = [t for t in data if not t.get("done", False)]
    deleted_count = initial_count - len(updated_data)
    
    if deleted_count > 0:
        save(updated_data)
        print_banner()
        print(f"{G}{BOLD}✅ Berhasil membersihkan {deleted_count} tugas yang sudah selesai.{W}")
    else:
        print_banner()
        print(f"{Y}Tidak ada tugas yang selesai untuk dibersihkan.{W}")
    input(f"{C_BOX}Tekan Enter untuk melanjutkan...{W}")
    return updated_data # Return updated data to main loop

# ---------------- Filter and Sort Logic ----------------
def apply_filters(data):
    """Menerapkan filter dan sorting pada data."""
    
    # 1. Filtering based on CURRENT_FILTER global state
    filtered_data = []
    if CURRENT_FILTER == "all":
        filtered_data = data
    elif CURRENT_FILTER == "done":
        filtered_data = [t for t in data if t.get("done")]
    elif CURRENT_FILTER == "todo":
        filtered_data = [t for t in data if not t.get("done")]
    else: # high, med, low (priority filters)
        filtered_data = [t for t in data if t.get("priority", "med").lower() == CURRENT_FILTER]
        
    # 2. Sorting: Belum selesai (False) di atas, Selesai (True) di bawah,
    #    dan diurutkan berdasarkan prioritas (High > Med > Low) di antara yang belum selesai.
    def sort_key(t):
        prio_map = {"high": 3, "med": 2, "low": 1}
        # Gunakan .get("priority", "med").lower() untuk memastikan perbandingan yang benar
        prio_val = prio_map.get(t.get("priority", "med").lower(), 0)
        
        # Primary sort: done (False/0 before True/1)
        # Secondary sort: priority (descending: -prio_val)
        # Tertiary sort: due date (ascending) - menggunakan string date agar dapat diurutkan
        due_date = t.get("due", "9999-12-31")
        return (t.get("done", False), -prio_val, due_date)

    return sorted(filtered_data, key=sort_key)


# ---------------- Display Function (Aesthetics) ----------------
def get_prio_style(pr):
    """Memberikan warna dan padding 4 karakter berdasarkan prioritas."""
    pr = pr.lower().strip()
    if pr == "high":
        # Menggunakan R (Red) untuk HIGH
        return BOLD + R, "HIGH"
    elif pr == "low":
        return DIM + C_BOX, "LOW "
    else:
        return Y, "MED "

def show(data):
    """Menampilkan daftar tugas dengan tata letak profesional dan warna yang rata."""
    global CURRENT_FILTER
    
    # Apply filter and sort
    display_data = apply_filters(data)

    if not display_data:
        print(C_BOX + "══════════════════════════════════════════" + W)
        if CURRENT_FILTER == "all":
            print(Y + "🎉 Semua tugas selesai atau belum ada tugas. Selamat!" + W)
        else:
            print(Y + f"Tidak ada tugas yang cocok dengan filter '{CURRENT_FILTER.upper()}'." + W)
        print(C_BOX + "══════════════════════════════════════════" + W)
        return
        
    print(C_BOX + BOLD + f"\n===== DAFTAR TUGAS ({len(display_data)} DITAMPILKAN) - FILTER: {CURRENT_FILTER.upper()} =====" + W)
    # Header alignment: No(2) | Prio(4) | Due Date(10) | Status(6) | Tugas
    print(f"{C_BOX}No | Prio | Due Date | Status | Tugas{W}")
    print(C_BOX + "---+------+----------+--------+--------------------------" + W)

    for i, t in enumerate(display_data, start=1):
        is_done = t.get("done", False)
        
        # 1. Prioritas (4 karakter)
        pr_color, pr_text = get_prio_style(t.get("priority", "med"))
        pr_display = pr_color + pr_text + W
        
        # 2. Due Date (10 karakter) - Highlight Overdue
        due_str = t.get("due", "-").ljust(10)
        due = due_str
        if due_str.strip() != "-" and not is_done:
            try:
                # Membersihkan spasi sebelum parsing
                due_date = datetime.strptime(due_str.strip(), "%Y-%m-%d").date()
                if due_date < datetime.now().date():
                    due = f"{R}OVERDUE{W}" # Highlight Overdue
            except ValueError:
                # Jika format tanggal salah, biarkan saja
                pass 
        
        # 3. Status (Dibuat 6 karakter visual agar rata)
        if is_done:
            status_text = f"{G}√ DONE{W}"    # Teks 6 karakter
            task_color = DIM # Selesai, teks diredupkan
        else:
            status_text = f"{Y} TODO {W}"  # Teks 6 karakter (diberi spasi di awal dan akhir)
            task_color = W # Belum, teks normal
        
        # Output line (menggunakan index dari daftar yang difilter/sortir)
        print(f"{C_BOX}{str(i).ljust(2)}{W} | {pr_display} | {due} | {status_text} | {task_color}{t.get('task')}{W}")

    print(C_BOX + "══════════════════════════════════════════" + W)


def handle_filter_command():
    """Mengubah filter global."""
    global CURRENT_FILTER
    print(f"\n{C_BOX}Pilih Filter:{W}")
    print(f" {G}a{W}: All | {R}h{W}: High | {Y}m{W}: Medium | {C_BOX}l{W}: Low")
    print(f" {G}d{W}: Done | {Y}t{W}: ToDo")
    filter_cmd = input(f"{C_BOX}▶ Filter Saat Ini ({CURRENT_FILTER.upper()}): {W}").strip().lower()
    
    if filter_cmd == "a": CURRENT_FILTER = "all"
    elif filter_cmd == "h": CURRENT_FILTER = "high"
    elif filter_cmd == "m": CURRENT_FILTER = "med"
    elif filter_cmd == "l": CURRENT_FILTER = "low"
    elif filter_cmd == "d": CURRENT_FILTER = "done"
    elif filter_cmd == "t": CURRENT_FILTER = "todo"
    else: 
        print(f"{R}Filter tidak valid.{W}")
        input(f"{C_BOX}Tekan Enter untuk melanjutkan...{W}")
        return # Keluar dari fungsi filter
    
    print_banner()
    if CURRENT_FILTER != "all":
        print(f"{C_NEON}Filter diubah menjadi: {CURRENT_FILTER.upper()}{W}")

# ---------------- Main Interaction Loop ----------------
def main():
    global CURRENT_FILTER
    
    print_banner()
    while True:
        try:
            data = load()
            show(data)
            
            # Menu Pilihan Baru dan Canggih (8 Opsi)
            print(f"\n{C_BOX}{BOLD}===== MENU AKSI =====" + W)
            print(f"{C_BOX}1.{W} {G}a{W}: Add Task      | {C_BOX}2.{W} {G}t{W}: Toggle Done/Todo | {C_BOX}3.{W} {G}e{W}: Edit Detail")
            print(f"{C_BOX}4.{W} {R}d{W}: Delete Task   | {C_BOX}5.{W} {Y}f{W}: Filter/Sort      | {C_BOX}6.{W} {C_BOX}r{W}: Refresh List")
            print(f"{C_BOX}7.{W} {R}c{W}: Clean DONE    | {C_BOX}8.{W} {C_NEON}q{W}: Quit")
            print(C_BOX + "══════════════════════════════════════════" + W)
            
            cmd = input(f"{C_BOX}▶ Pilihan Anda: {W}").strip().lower()

            if cmd == "a":
                # Tambah
                task = input(f"{G}Task:{W} ").strip()
                if not task: continue
                # Ambil input dan pastikan 'med' adalah default
                pr_input = input(f"{Y}Priority (low/med/high) [med]:{W} ").strip()
                pr = pr_input.lower() if pr_input else "med"
                due = input(f"{Y}Due (YYYY-MM-DD) [blank]:{W} ").strip()
                
                data.append({"task": task, "priority": pr, "due": due, "done": False})
                save(data)
                print_banner()
                print(f"{G}Task '{task}' ditambahkan.{W}")
                
            elif cmd == "t":
                # Toggle
                raw_idx = input(f"{G}Nomor tugas untuk di-toggle (dari list di atas):{W} ").strip()
                try: idx_display = int(raw_idx) - 1
                except ValueError: print(f"{R}Input harus angka.{W}"); input(f"{C_BOX}Tekan Enter...{W}"); print_banner(); continue
                
                display_data = apply_filters(data)
                if 0 <= idx_display < len(display_data):
                    original_task = display_data[idx_display]
                    original_index = data.index(original_task) 
                    
                    data[original_index]["done"] = not data[original_index].get("done", False)
                    save(data)
                    status = "DONE" if data[original_index]["done"] else "TODO"
                    print_banner()
                    print(f"{G}Status tugas {raw_idx} diubah menjadi {status}.{W}")
                else: print(f"{R}Indeks tidak valid.{W}"); input(f"{C_BOX}Tekan Enter...{W}"); print_banner()
                
            elif cmd == "e":
                # Edit
                raw_idx = input(f"{G}Nomor tugas untuk di-edit (dari list di atas):{W} ").strip()
                try: idx_display = int(raw_idx) - 1
                except ValueError: print(f"{R}Input harus angka.{W}"); input(f"{C_BOX}Tekan Enter...{W}"); print_banner(); continue
                
                display_data = apply_filters(data)
                if 0 <= idx_display < len(display_data):
                    current = display_data[idx_display]
                    original_index = data.index(current)
                    
                    print_banner()
                    print(f"{C_BOX}Mengedit Tugas {raw_idx}: '{current['task']}'{W}")
                    
                    # Edit fields
                    new_task = input(f"Task baru [{current['task']}]: ").strip()
                    if new_task: data[original_index]["task"] = new_task

                    new_prio = input(f"Priority baru [{current.get('priority', 'med')}]: ").strip().lower()
                    if new_prio: data[original_index]["priority"] = new_prio
                    
                    new_due = input(f"Due baru [{current.get('due', '')}]: ").strip()
                    if new_due: data[original_index]["due"] = new_due

                    save(data)
                    
                    print_banner()
                    print(f"{G}Tugas {raw_idx} berhasil diperbarui.{W}")
                else: print(f"{R}Indeks tidak valid.{W}"); input(f"{C_BOX}Tekan Enter...{W}"); print_banner()
                
            elif cmd == "d":
                # Delete
                raw_idx = input(f"{R}Nomor tugas untuk di-HAPUS (dari list di atas):{W} ").strip()
                try: idx_display = int(raw_idx) - 1
                except ValueError: print(f"{R}Input harus angka.{W}"); input(f"{C_BOX}Tekan Enter...{W}"); print_banner(); continue
                
                display_data = apply_filters(data)
                if 0 <= idx_display < len(display_data):
                    original_task = display_data[idx_display]
                    original_index = data.index(original_task) 
                    
                    task_name = data[original_index]["task"]
                    data.pop(original_index)
                    save(data)
                    print_banner()
                    print(f"{R}Tugas '{task_name}' Dihapus.{W}")
                else: print(f"{R}Indeks tidak valid.{W}"); input(f"{C_BOX}Tekan Enter...{W}"); print_banner()
                
            elif cmd == "f":
                # Filter/Sort
                print_banner()
                handle_filter_command()

            elif cmd == "r":
                # Refresh Menu
                print_banner()
                print(f"{C_BOX}Daftar berhasil diperbarui!{W}")
            
            elif cmd == "c":
                # Clean Done Tasks
                # Peringatan sebelum menghapus
                print_banner()
                print(f"{R}{BOLD}⚠️ PERINGATAN!{W} Ini akan menghapus PERMANEN semua tugas yang sudah selesai (DONE).")
                confirm = input(f"{R}Ketik 'YES' untuk konfirmasi: {W}").strip()
                
                if confirm == "YES":
                    data = clean_done_tasks(data) # Pastikan data di-update
                else:
                    print_banner()
                    print(f"{Y}Penghapusan dibatalkan.{W}")
                    input(f"{C_BOX}Tekan Enter untuk melanjutkan...{W}")
                
            elif cmd in ("q", "quit", "exit"):
                print(f"{C_NEON}Keluar dari EraldForge Todo. Sampai jumpa!{W}")
                break
            else:
                print(f"{R}Pilihan tidak dikenal. Masukkan a, t, e, d, f, r, c, atau q.{W}")
                input(f"{C_BOX}Tekan Enter untuk melanjutkan...{W}")
                print_banner()
                
        except EOFError:
            print(f"\n{C_NEON}Keluar dari EraldForge Todo.{W}")
            sys.exit(0)
        except Exception as e:
            print(f"{R}Terjadi error tak terduga: {e}{W}")
            input(f"{C_BOX}Tekan Enter untuk melanjutkan...{W}")
            print_banner()

if __name__ == "__main__":
    main()