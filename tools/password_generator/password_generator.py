#!/data/data/com.termux/files/usr/bin/env python3
"""
EraldForge - Generator Kata Sandi
Alat profesional untuk menghasilkan kata sandi acak yang kuat dengan opsi kustomisasi mendalam, 
termasuk analisis kekuatan (Entropi Bit) dan mode batch.
"""
import os
import sys
import secrets
import string
import subprocess
import re
import math # Diperlukan untuk perhitungan entropi

# ---------------- Tema & Warna ----------------

def get_theme_colors():
    """Mengambil skema warna berdasarkan tema lingkungan (default: clean)."""
    t = os.environ.get("ERALDFORGE_THEME", "clean")
    if t == "hacker":
        return {
            "P": "\033[93m", # Neon Yellow (Primary Banner)
            "R": "\033[91m", # Red (Error)
            "X": "\033[0m",  # Reset
            "B": "\033[36m", # Cyan (Generated Password)
            "G": "\033[32m", # Green (Success/Info/Strong)
            "W": "\033[97m", # White/Detail
        }
    else:
        return {
            "P": "\033[93m", # Neon Yellow (Primary Banner)
            "R": "\033[91m", # Red (Error)
            "X": "\033[0m",  # Reset
            "B": "\033[34m", # Blue (Generated Password)
            "G": "\033[32m", # Green (Success/Info/Strong)
            "W": "\033[97m", # White/Detail
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
    print(C["G"] + "Generator Kata Sandi Acak Kuat & Analisis Entropi" + C["X"])
    print(C["G"] + "===================================================" + C["X"] + "\n")

# ---------------- Logika Utama Generator & Entropi ----------------

def calculate_entropy(length, pool_size):
    """Menghitung entropi (kekuatan) kata sandi dalam bit."""
    # Entropy (bits) = L * log2(N)
    # L = Length, N = Pool Size (jumlah karakter unik yang mungkin)
    if pool_size <= 1:
        return 0.0
    return length * math.log2(pool_size)

def generate_password(length, use_lower, use_upper, use_digits, use_symbols, exclude_chars=""):
    """
    Menghasilkan kata sandi acak menggunakan modul secrets.
    Mengembalikan tuple: (kata_sandi, ukuran_kumpulan_karakter)
    """
    alphabet = ""
    
    if use_lower:
        alphabet += string.ascii_lowercase
    if use_upper:
        alphabet += string.ascii_uppercase
    if use_digits:
        alphabet += string.digits
    
    # Simbol yang umum dan aman, dipecah agar mudah dimodifikasi
    SAFE_SYMBOLS = "!@#$%^&*()-_=+[]{};:,.<>?"

    if use_symbols:
        alphabet += SAFE_SYMBOLS
    
    # Menghapus karakter yang dikecualikan
    for char in exclude_chars:
        # Menghapus secara aman
        alphabet = alphabet.replace(char, "")

    pool_size = len(alphabet)

    if pool_size < 4:
        raise ValueError(f"Ukuran kumpulan karakter terlalu kecil ({pool_size}). Pilih opsi lebih banyak.")

    # Memastikan kata sandi memenuhi panjang yang diminta
    if length > 0:
        pw = "".join(secrets.choice(alphabet) for _ in range(length))
    else:
        pw = ""

    return pw, pool_size

# ---------------- Fungsi Pendukung I/O ----------------

def get_valid_length(default=16, min_len=8, max_len=128):
    """Meminta input panjang dan memvalidasinya."""
    while True:
        try:
            prompt = f"Panjang Kata Sandi (minimal {min_len}, maksimal {max_len}) [{default}]: "
            length_input = input(prompt).strip() or str(default)
            length = int(length_input)
            if min_len <= length <= max_len:
                return length
            else:
                print(f"{C['R']}Panjang harus antara {min_len} dan {max_len}.{C['X']}")
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
    excluded = ""
    if get_user_confirmation(f"Kecualikan karakter ambigu (misalnya {ambiguous_chars})?", default='y'):
        excluded = ambiguous_chars
    
    # Tawarkan pengecualian manual
    manual_exclude = input("Karakter tambahan yang ingin dikecualikan (pisahkan tanpa spasi): ").strip()
    
    # Gabungkan dan hapus duplikasi
    final_exclude = "".join(sorted(list(set(excluded + manual_exclude))))
    
    return final_exclude

def copy_to_clipboard(password):
    """Menyalin kata sandi ke clipboard (khusus Termux)."""
    try:
        # Menggunakan 'tee' untuk menghindari masalah input terminal
        proc = subprocess.Popen(["termux-clipboard-set"], stdin=subprocess.PIPE, text=True, check=False)
        proc.communicate(input=password, timeout=1)
        print(f"\n{C['G']}✅ Kata sandi berhasil disalin ke clipboard (via termux-clipboard-set).{C['X']}")
    except FileNotFoundError:
        # Ini adalah penyebab utama kegagalan
        print(f"\n{C['R']}❌ Gagal menyalin: Perintah 'termux-clipboard-set' tidak ditemukan.{C['X']}")
        print(f"{C['R']}Mohon instal Termux:API dengan perintah: {C['P']}pkg install termux-api{C['R']} lalu pastikan Anda memberikan izin akses.{C['X']}")
    except Exception as e:
        # Catch timeout or other general errors
        print(f"\n{C['R']}❌ Gagal menyalin ke clipboard: {type(e).__name__}. Coba salin manual.{C['X']}")

def print_strength_analysis(entropy, length):
    """Menganalisis dan mencetak kekuatan kata sandi berdasarkan entropi."""
    if entropy >= 120:
        strength_color = C['G']
        rating = "BRUTAL (Extreme)"
    elif entropy >= 90:
        strength_color = C['G']
        rating = "SANGAT KUAT (Excellent)"
    elif entropy >= 60:
        strength_color = C['P']
        rating = "KUAT (Strong)"
    elif entropy >= 40:
        strength_color = C['P']
        rating = "SEDANG (Moderate)"
    else:
        strength_color = C['R']
        rating = "LEMAH (Weak)"
        
    # Standard keamanan minimum yang direkomendasikan adalah 80-100 bit.
    
    print("\n" + C['W'] + "--- Analisis Kekuatan ---" + C['X'])
    print(f"  Panjang: {length}")
    print(f"  Entropi Bit: {C['W']}{entropy:.2f} bits{C['X']}")
    print(f"  Rating Keamanan: {strength_color}{rating}{C['X']}")
    print("-" * 25 + C['X'])


# ---------------- Alur Menu & Mode ----------------

def get_custom_settings(default_length=24):
    """Mengumpulkan semua pengaturan kustom dari pengguna."""
    print("\n" + C['W'] + "--- Pengaturan Kustomisasi ---" + C['X'])
    length = get_valid_length(default=default_length, min_len=8, max_len=128)
    use_lower = get_user_confirmation("Sertakan huruf kecil (a-z)?", default='y')
    use_upper = get_user_confirmation("Sertakan huruf besar (A-Z)?", default='y')
    use_digits = get_user_confirmation("Sertakan angka (0-9)?", default='y')
    use_symbols = get_user_confirmation("Sertakan simbol (!@#$%)?", default='y')
    excluded_chars = get_excluded_chars()
    
    return length, use_lower, use_upper, use_digits, use_symbols, excluded_chars

def setup_generation(mode):
    """Menetapkan pengaturan berdasarkan mode pilihan."""
    
    # Default Settings
    length = 24
    use_lower = True
    use_upper = True
    use_digits = True
    use_symbols = True
    excluded_chars = "Il1O0" # Default

    if mode == '1': # Dasar
        length = 10
        use_upper = False
        use_symbols = False
    elif mode == '2': # Standar
        length = 16
        use_upper = True
        use_symbols = False
    elif mode == '3': # Kuat
        length = 24
        use_symbols = True
    elif mode == '4': # Kustom
        length, use_lower, use_upper, use_digits, use_symbols, excluded_chars = get_custom_settings(default_length=length)
    else:
        # Fallback to Kuat if invalid input
        pass 
        
    # Tampilkan detail final sebelum generasi
    print("\n" + C['G'] + "--- Detail Generasi ---" + C['X'])
    print(f"  Panjang: {length}")
    print(f"  Lower (a-z): {'Ya' if use_lower else 'Tidak'}")
    print(f"  Upper (A-Z): {'Ya' if use_upper else 'Tidak'}")
    print(f"  Angka (0-9): {'Ya' if use_digits else 'Tidak'}")
    print(f"  Simbol (!@#): {'Ya' if use_symbols else 'Tidak'}")
    print(f"  Kecuali: {C['R']}{excluded_chars if excluded_chars else 'Tidak ada'}{C['X']}")
    print("-" * 25 + C['X'])

    # Pastikan setidaknya ada satu jenis karakter
    if not (use_lower or use_upper or use_digits or use_symbols):
        raise ValueError("Setidaknya satu set karakter (huruf, angka, atau simbol) harus dipilih.")

    return length, use_lower, use_upper, use_digits, use_symbols, excluded_chars

def generate_single_password_flow():
    """Alur untuk menghasilkan satu kata sandi dan analisis penuh."""
    display_banner()
    
    print(C["G"] + "Pilih Mode Keamanan (Single Password):" + C["X"])
    print(f"  {C['B']}1{C['X']}. {C['W']}Dasar (10 chars, a-z, 0-9)" + C['X'])
    print(f"  {C['B']}2{C['X']}. {C['W']}Standar (16 chars, Full Alpha-Numeric)" + C['X'])
    print(f"  {C['B']}3{C['X']}. {C['G']}Kuat (24 chars, Semua Karakter)" + C['X'])
    print(f"  {C['B']}4{C['X']}. {C['P']}Kustom (Tentukan sendiri)" + C['X'])
    
    mode = input(f"\nPilihan mode (1-4) [{C['B']}3{C['X']}]: ").strip() or "3"

    try:
        length, use_lower, use_upper, use_digits, use_symbols, excluded_chars = setup_generation(mode)
        
        pw, pool_size = generate_password(
            length=length,
            use_lower=use_lower, use_upper=use_upper, 
            use_digits=use_digits, use_symbols=use_symbols,
            exclude_chars=excluded_chars
        )
        
        entropy = calculate_entropy(length, pool_size)

        print("\nHasil Generasi Kata Sandi:\n")
        print(f"{C['B']}{pw}{C['X']}")
        
        print_strength_analysis(entropy, length)
        
        copy_to_clipboard(pw)
        
    except ValueError as e:
        print(f"\n{C['R']}⚠️ ERROR Konfigurasi: {e}{C['X']}")
    except Exception as e:
        print(f"\n{C['R']}⚠️ ERROR tak terduga: {e}{C['X']}")

def generate_multiple_passwords_flow():
    """Alur untuk menghasilkan banyak kata sandi sekaligus (Batch Mode)."""
    display_banner()
    print(C['G'] + "--- Mode Generasi Batch (Massal) ---" + C['X'])
    
    # 1. Tentukan jumlah batch
    while True:
        try:
            count = int(input("Jumlah kata sandi yang ingin dibuat (1-20) [5]: ").strip() or "5")
            if 1 <= count <= 20:
                break
            print(f"{C['R']}Jumlah harus antara 1 dan 20.{C['X']}")
        except ValueError:
            print(f"{C['R']}Input tidak valid. Masukkan angka.{C['X']}")

    # 2. Ambil pengaturan (dipaksa Kustom/Kuat untuk batch)
    print("\nPengaturan akan digunakan untuk SEMUA kata sandi dalam batch.")
    
    # Meminta pengaturan kustom
    try:
        length, use_lower, use_upper, use_digits, use_symbols, excluded_chars = get_custom_settings(default_length=16)

        print("\n" + C['G'] + "--- Proses Generasi (Batch) ---" + C['X'])
        generated_passwords = []
        
        # Hitung entropi pool size sebelum loop
        _, pool_size = generate_password(
            length=1, # Hanya perlu panjang 1 untuk mendapatkan pool_size
            use_lower=use_lower, use_upper=use_upper, 
            use_digits=use_digits, use_symbols=use_symbols,
            exclude_chars=excluded_chars
        )

        for i in range(count):
            pw, _ = generate_password(
                length=length,
                use_lower=use_lower, use_upper=use_upper, 
                use_digits=use_digits, use_symbols=use_symbols,
                exclude_chars=excluded_chars
            )
            entropy = calculate_entropy(length, pool_size)
            
            # Tampilkan hasil dalam format list
            print(f"{C['W']}{i+1}.{C['X']} {C['B']}{pw}{C['X']} ({entropy:.0f} bits)")
            generated_passwords.append(pw)

        # Hanya salin yang pertama ke clipboard untuk menghindari kekacauan
        if generated_passwords:
            print(f"\n{C['P']}⚠️ Hanya kata sandi pertama ({generated_passwords[0]}) yang akan disalin ke clipboard.{C['X']}")
            copy_to_clipboard(generated_passwords[0])

    except ValueError as e:
        print(f"\n{C['R']}⚠️ ERROR Konfigurasi: {e}{C['X']}")
    except Exception as e:
        print(f"\n{C['R']}⚠️ ERROR tak terduga: {e}{C['X']}")


def main_menu():
    """Menampilkan menu utama dan mengarahkan ke alur yang dipilih."""
    while True:
        display_banner()
        print(C["W"] + "Menu Utama Generator Kata Sandi:" + C["X"])
        print(f"  {C['B']}1{C['X']}. {C['G']}Buat SATU Kata Sandi Kuat (Analisis Penuh)" + C['X'])
        print(f"  {C['B']}2{C['X']}. {C['P']}Mode Batch (Buat Banyak Kata Sandi Sekaligus)" + C['X'])
        print(f"  {C['R']}3{C['X']}. {C['R']}Keluar" + C['X']) # Diubah dari 9 menjadi 3
        
        choice = input(f"\nPilihan (1/2/3): ").strip() # Diperbarui

        if choice == '1':
            generate_single_password_flow()
        elif choice == '2':
            generate_multiple_passwords_flow()
        elif choice in ('3', 'exit', 'quit'): # Diperbarui
            print(f"\n{C['G']}Terima kasih, EraldForge Generator Kata Sandi ditutup.{C['X']}")
            break
        else:
            print(f"\n{C['R']}Pilihan tidak valid. Silakan coba lagi.{C['X']}")
            
        input(f"\n{C['G']}Tekan Enter untuk kembali ke Menu Utama...{C['X']}")
        

def main():
    """Fungsi utama."""
    try:
        main_menu()
    except KeyboardInterrupt:
        print(f"\n{C['R']}Generator dihentikan oleh pengguna.{C['X']}")
        sys.exit(0)

if __name__ == "__main__":
    main()