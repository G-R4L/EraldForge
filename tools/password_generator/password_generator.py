#!/data/data/com.termux/files/usr/bin/env python3
"""
EraldForge - Generator Kata Sandi
Alat profesional untuk menghasilkan kata sandi acak yang kuat dengan opsi kustomisasi mendalam.
"""
import os
import sys
import secrets
import string
import subprocess
import re

# ---------------- Tema & Warna ----------------

def get_theme_colors():
    """Mengambil skema warna berdasarkan tema lingkungan (default: clean)."""
    # Menggunakan Kuning Neon untuk banner dan Cyan/Biru untuk output utama
    t = os.environ.get("ERALDFORGE_THEME", "clean")
    if t == "hacker":
        return {
            "P": "\033[93m", # Neon Yellow (Primary Banner)
            "R": "\033[91m", # Red (Error)
            "X": "\033[0m",  # Reset
            "B": "\033[36m", # Cyan (Generated Password)
            "G": "\033[32m"  # Green (Success/Info)
        }
    else:
        return {
            "P": "\033[93m", # Neon Yellow (Primary Banner)
            "R": "\033[91m", # Red (Error)
            "X": "\033[0m",  # Reset
            "B": "\033[34m", # Blue (Generated Password)
            "G": "\033[32m"  # Green (Success/Info)
        }

C = get_theme_colors()

# ---------------- Banner ASCII (Kuning Neon & Alignment Sempurna) ----------------

# Total lebar bingkai: 51 karakter. Konten (antara ':') harus 49 karakter.
BANNER_LINES = [
    C["P"] + "·················································" + C["X"], # 51
    C["P"] + "\033[1m" + ": ____                                     _      " + C["P"] + ":", # 49 content
    C["P"] + "\033[1m" + ":|  _ \ __ _ ___ _____      _____  _ __ __| |  " + C["P"] + ":", # 49 content
    C["P"] + "\033[1m" + ":| |_) / _` / __/ __\ \ /\ / / _ \| '__/ _` |  " + C["P"] + ":", # 49 content
    C["P"] + "\033[1m" + ":|  __/ (_| \__ \__ \\ V  V / (_) | | | (_| |  " + C["P"] + ":", # 49 content
    C["P"] + "\033[1m" + ":|_|___\__,_|___/___/ \_/\_/ \___/|_|  \__,_|  " + C["P"] + ":", # 49 content
    C["P"] + "\033[1m" + ": / ___| ___ _ __   ___ _ __ __ _| |_ ___  _ __  " + C["P"] + ":", # 49 content
    C["P"] + "\033[1m" + ":| |  _ / _ \ '_ \ / _ \ '__/ _` | __/ _ \| '__| " + C["P"] + ":", # 49 content
    C["P"] + "\033[1m" + ":| |_| |  __/ | | |  __/ | | (_| | || (_) | |  " + C["P"] + ":", # 49 content
    C["P"] + "\033[1m" + ": \____|\___|_| |_|\___|_|  \__,_|\__\___/|_|  " + C["P"] + ":", # 49 content
    C["P"] + "·················································" + C["X"], # 51
]

def display_banner():
    """Mencetak banner ASCII EraldForge Password Generator."""
    os.system('clear')
    for line in BANNER_LINES:
        print(line)
    print(C["G"] + "Generator Kata Sandi Acak Kuat" + C["X"])
    print(C["G"] + "===================================================" + C["X"] + "\n")

# ---------------- Logika Utama Generator ----------------

def generate_password(length, use_lower, use_upper, use_digits, use_symbols, exclude_chars=""):
    """
    Menghasilkan kata sandi acak menggunakan modul secrets.
    """
    alphabet = ""
    
    if use_lower:
        alphabet += string.ascii_lowercase
    if use_upper:
        alphabet += string.ascii_uppercase
    if use_digits:
        alphabet += string.digits
    if use_symbols:
        # Menambahkan simbol yang umum dan aman
        alphabet += "!@#$%^&*()-_=+[]{};:,.<>?"
    
    # Menghapus karakter yang dikecualikan
    for char in exclude_chars:
        alphabet = alphabet.replace(char, "")

    if not alphabet:
        raise ValueError("Tidak ada karakter yang tersedia untuk generasi kata sandi. Pastikan Anda memilih setidaknya satu jenis karakter.")

    # Menghasilkan kata sandi
    return "".join(secrets.choice(alphabet) for _ in range(length))

def get_valid_length(default=16):
    """Meminta input panjang dan memvalidasinya."""
    while True:
        try:
            prompt = f"Panjang Kata Sandi (minimal 8, maksimal 128) [{default}]: "
            length_input = input(prompt).strip() or str(default)
            length = int(length_input)
            if 8 <= length <= 128:
                return length
            else:
                print(f"{C['R']}Panjang harus antara 8 dan 128.{C['X']}")
        except ValueError:
            print(f"{C['R']}Input tidak valid. Masukkan angka.{C['X']}")

def get_user_confirmation(prompt, default='y'):
    """Mendapatkan konfirmasi Y/N dari pengguna."""
    default_text = "[Y/n]" if default == 'y' else "[y/N]"
    while True:
        choice = input(f"{prompt} {default_text}: ").strip().lower() or default
        if choice in ('y', 'ya', 't', 'true'):
            return True
        elif choice in ('n', 'tidak', 'f', 'false'):
            return False
        else:
            print(f"{C['R']}Input tidak valid. Silakan masukkan 'y' atau 'n'.{C['X']}")

def get_excluded_chars():
    """Meminta input karakter yang ingin dikecualikan."""
    
    # Karakter yang sering ambigu (Il1O0)
    ambiguous_chars = "Il1O0" 
    
    # Tawarkan pengecualian karakter ambigu
    if get_user_confirmation(f"Kecualikan karakter ambigu (misalnya {ambiguous_chars})?", default='y'):
        excluded = ambiguous_chars
    else:
        excluded = ""
    
    # Tawarkan pengecualian manual
    manual_exclude = input("Karakter tambahan yang ingin dikecualikan (kosongkan jika tidak ada): ").strip()
    
    # Gabungkan dan hapus duplikasi
    final_exclude = "".join(sorted(list(set(excluded + manual_exclude))))
    
    return final_exclude

def copy_to_clipboard(password):
    """Menyalin kata sandi ke clipboard (khusus Termux)."""
    try:
        # Cek apakah perintah termux-clipboard-set tersedia
        subprocess.run(["which", "termux-clipboard-set"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Salin
        subprocess.run(["termux-clipboard-set"], input=password.encode('utf-8'), check=False)
        print(f"\n{C['G']}✅ Kata sandi berhasil disalin ke clipboard (via termux-clipboard-set).{C['X']}")
    except subprocess.CalledProcessError:
        print(f"\n{C['R']}❌ Perintah 'termux-clipboard-set' tidak tersedia.{C['X']}")
        print(f"{C['R']}Instal 'termux-api' untuk fitur ini: pkg install termux-api{C['X']}")
    except FileNotFoundError:
        # 'which' command not found, or other general error
        pass
    except Exception as e:
        print(f"\n{C['R']}❌ Gagal menyalin ke clipboard: {e}{C['X']}")


def main():
    display_banner()
    
    print(C["G"] + "Pilih Mode Keamanan:" + C["X"])
    print(f"  {C['B']}1{C['X']}. {C['B']}Dasar{C['X']} (Lower-Awal: 8 chars, Tanpa Simbol)")
    print(f"  {C['B']}2{C['X']}. {C['B']}Standar{C['X']} (Lower/Upper/Digit: 16 chars, Tanpa Simbol)")
    print(f"  {C['B']}3{C['X']}. {C['X']}Kuat (Full Custom: 24 chars, Semua Karakter)")
    print(f"  {C['B']}4{C['X']}. {C['X']}Kustom (Tentukan sendiri)")
    
    mode = input(f"\nPilihan mode (1-4) [{C['B']}3{C['X']}]: ").strip() or "3"
    
    # Default Settings based on Mode
    length = 24
    use_lower = True
    use_upper = True
    use_digits = True
    use_symbols = True
    excluded_chars = "Il1O0" # Default, akan ditimpa jika mode Kustom dipilih

    if mode == '1': # Dasar
        length = 8
        use_upper = False
        use_digits = True
        use_symbols = False
        excluded_chars = "Il1O0"
    elif mode == '2': # Standar
        length = 16
        use_upper = True
        use_digits = True
        use_symbols = False
        excluded_chars = "Il1O0"
    elif mode == '4': # Kustom
        print("\n--- Pengaturan Kustom ---")
        length = get_valid_length(default=length)
        use_lower = get_user_confirmation("Sertakan huruf kecil (a-z)?", default='y')
        use_upper = get_user_confirmation("Sertakan huruf besar (A-Z)?", default='y')
        use_digits = get_user_confirmation("Sertakan angka (0-9)?", default='y')
        use_symbols = get_user_confirmation("Sertakan simbol (!@#$%)?", default='y')
        excluded_chars = get_excluded_chars()
        
    print("\n" + C['G'] + "--- Detail Generasi ---" + C['X'])
    print(f"Panjang: {length}")
    print(f"Lower: {'Ya' if use_lower else 'Tidak'}")
    print(f"Upper: {'Ya' if use_upper else 'Tidak'}")
    print(f"Angka: {'Ya' if use_digits else 'Tidak'}")
    print(f"Simbol: {'Ya' if use_symbols else 'Tidak'}")
    print(f"Kecuali: {excluded_chars if excluded_chars else 'Tidak ada'}\n")
    
    try:
        pw = generate_password(
            length=length,
            use_lower=use_lower,
            use_upper=use_upper,
            use_digits=use_digits,
            use_symbols=use_symbols,
            exclude_chars=excluded_chars
        )
        print("Kata sandi yang dihasilkan:\n")
        print(C["B"] + pw + C["X"])
        
        copy_to_clipboard(pw)
        
    except ValueError as e:
        print(f"\n{C['R']}⚠️ ERROR: {e}{C['X']}")
    except Exception as e:
        print(f"\n{C['R']}⚠️ ERROR tak terduga: {e}{C['X']}")
        
    input(f"\n{C['G']}Tekan Enter untuk keluar...{C['X']}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{C['R']}Generator dihentikan oleh pengguna.{C['X']}")
        sys.exit(0)