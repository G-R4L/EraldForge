#!/data/data/com.termux/files/usr/bin/env python3
# EraldForge - Calculator (Erald Ultimate Edition)
# Versi: Modern, Canggih, Profesional, Aman, Statistik

import os, ast, math, readline, sys
from fractions import Fraction
from datetime import datetime
from collections import Counter
import textwrap

# --- Konfigurasi Dasar ---
HOME = os.path.expanduser("~")
HIST_FILE = os.path.join(HOME, ".eraldforge_calc_history")
WAKTU_SEKARANG = datetime.now()

# --- Definisi Warna (Skema Neon High-Tech) ---
R = "\033[91m"     # Merah Terang (Error)
G = "\033[92m"     # Hijau Terang (Prompt Input)
C_BOX = "\033[96m"  # Cyan Terang (Garis Box, Batas, Info)
C_NEON = "\033[93m" # Kuning Terang/Neon (Full Banner & Highlighting)
C_RESULT = "\033[97m"  # Putih Terang (Hasil Perhitungan)
W = "\033[0m"
BOLD = "\033[1m"
ULINE = "\033[4m" # Garis Bawah

# --- Banner ASCII Klasik Erald (Full Neon Kuning) ---
BANNER_LINES = [
    " ················································· ",
    " :  ____      _            _       _             : ",
    " : / ___|__ _| | ___ _   _| | __ _| |_ ___  _ __ : ",
    " :| |   / _` | |/ __| | | | |/ _` | __/ _ \| '__|: ",
    " :| |__| (_| | | (__| |_| | | (_| | || (_) | |   : ",
    " : \____\__,_|_|\___|\__,_|_|\__,_|\__\___/|_|   : ",
    " ················································· ",
]

def print_banner():
    """Mencetak banner full Kuning Neon."""
    out = [C_NEON + line.replace(" ", " ") + W for line in BANNER_LINES]
    print("\n".join(out))

# --- FITUR BARU: Statistik Dasar (Mean, Median, Modus) ---
def hitung_statistik(data_list):
    if not all(isinstance(x, (int, float)) for x in data_list):
        raise ValueError("Semua elemen list harus berupa angka (int/float).")
    
    n = len(data_list)
    if n == 0:
        raise ValueError("List data tidak boleh kosong.")
    
    # Mean (Rata-rata)
    mean = sum(data_list) / n
    
    # Median
    data_list_sorted = sorted(data_list)
    if n % 2 == 1:
        median = data_list_sorted[n // 2]
    else:
        median = (data_list_sorted[n // 2 - 1] + data_list_sorted[n // 2]) / 2
        
    # Modus
    counts = Counter(data_list)
    max_count = max(counts.values())
    modus = [key for key, value in counts.items() if value == max_count]
    
    # Format output custom untuk statistik
    output = f"\n{C_NEON} STATISTIK HASIL:{W}\n"
    output += f"   {BOLD}Mean (Rata-rata):{W} {mean}\n"
    output += f"   {BOLD}Median:{W} {median}\n"
    output += f"   {BOLD}Modus:{W} {', '.join(map(str, modus))}"
    
    return output

# --- Fungsi Geometri (Luas) ---
def hitung_luas(jenis, *args):
    """Menghitung luas berbagai bangun datar."""
    jenis = jenis.lower()
    if jenis == 'persegi':
        if len(args) == 1: return args[0] ** 2
        else: raise ValueError("luas('persegi', sisi)")
    elif jenis == 'segitiga':
        if len(args) == 2: return 0.5 * args[0] * args[1] # Alas, Tinggi
        else: raise ValueError("luas('segitiga', alas, tinggi)")
    elif jenis == 'lingkaran':
        if len(args) == 1: return math.pi * (args[0] ** 2) # Jari-jari
        else: raise ValueError("luas('lingkaran', jari_jari)")
    elif jenis == 'persegipanjang':
        if len(args) == 2: return args[0] * args[1] # Panjang, Lebar
        else: raise ValueError("luas('persegipanjang', panjang, lebar)")
    else:
        raise ValueError(f"Bangun datar '{jenis}' tidak didukung. Coba: persegi, segitiga, lingkaran, persegipanjang.")

# --- Lingkungan Matematika Aman (Safe Math Environment) ---
SAFE_FUNCS = {
    'akar': math.sqrt, 'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
    'log': math.log, 'log10': math.log10, 'exp': math.exp,
    'pangkat': pow, 'abs': abs, 'bulatkan': round, 
    'bulatkan_bawah': math.floor, 'bulatkan_atas': math.ceil,
    'pi': math.pi, 'e': math.e, 'Pecahan': Fraction,
    'umur': lambda y: WAKTU_SEKARANG.year - y,
    'hari_sejak': lambda y,m,d: (WAKTU_SEKARANG - datetime(y,m,d)).days,
    'tahun_ini': lambda: WAKTU_SEKARANG.year,
    'luas': hitung_luas,
    'stat': hitung_statistik # FUNGSI BARU CANGGIH
}
ALLOWED_NODES = (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Num, ast.Constant,
                 ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow, ast.Mod, ast.FloorDiv,
                 ast.USub, ast.UAdd, ast.Call, ast.Load, ast.Name, ast.Tuple, ast.List,
                 ast.BitXor, ast.BitAnd, ast.BitOr, ast.LShift, ast.RShift)

# --- Kelas SafeEval (Inti Logika) ---
class SafeEval(ast.NodeVisitor):
    def generic_visit(self, node):
        if type(node) not in ALLOWED_NODES:
            raise ValueError(f"Ekspresi/Node '{type(node).__name__}' tidak diizinkan.")
        return super().generic_visit(node)
    def visit_Expression(self, node): return self.visit(node.body)
    def visit_BinOp(self, node):
        l, r = self.visit(node.left), self.visit(node.right)
        ops = {
            ast.Add: l + r, ast.Sub: l - r, ast.Mult: l * r, ast.Div: l / r,
            ast.FloorDiv: l // r, ast.Mod: l % r, ast.Pow: l ** r,
            ast.BitXor: l ^ r, ast.BitAnd: l & r, ast.BitOr: l | r,
            ast.LShift: l << r, ast.RShift: l >> r
        }
        if type(node.op) in ops: return ops[type(node.op)]
        raise ValueError("Operator tidak didukung")
    def visit_UnaryOp(self, node):
        v = self.visit(node.operand)
        if isinstance(node.op, ast.UAdd): return +v
        if isinstance(node.op, ast.USub): return -v
        raise ValueError("Operator Unary tidak diizinkan")
    def visit_Num(self, node): return node.n
    def visit_Constant(self, node):
        if isinstance(node.value, (int, float, str)): return node.value # Mengizinkan string untuk 'luas' dan list untuk 'stat'
        raise ValueError("Hanya konstanta numerik (angka), string, atau list sederhana.")
    def visit_Call(self, node):
        if not isinstance(node.func, ast.Name): raise ValueError("Hanya pemanggilan fungsi sederhana")
        fname = node.func.id
        if fname not in SAFE_FUNCS: raise ValueError(f"Fungsi '{fname}' tidak diizinkan")
        args = [self.visit(a) for a in node.args]
        return SAFE_FUNCS[fname](*args) if fname not in ('stat') else SAFE_FUNCS[fname](args[0]) # Penanganan khusus untuk stat
    def visit_Name(self, node):
        if node.id in SAFE_FUNCS: return SAFE_FUNCS[node.id]
        raise ValueError(f"Nama/Variabel '{node.id}' tidak diizinkan")
    def visit_Tuple(self, node):
        return [self.visit(e) for e in node.elts] # Mengizinkan tuple/list untuk args fungsi (misal: luas, stat)
    def visit_List(self, node):
        return [self.visit(e) for e in node.elts] # Mengizinkan list untuk args fungsi (misal: stat)

def safe_eval(expr):
    node = ast.parse(expr, mode='eval')
    return SafeEval().visit(node)

# --- Fungsi Utilitas (Riwayat, Konversi) ---
def history_load():
    try:
        if os.path.exists(HIST_FILE):
            with open(HIST_FILE) as f:
                return [l.strip() for l in f.readlines() if l.strip()]
    except Exception: pass
    return []

def history_save(hist):
    try:
        with open(HIST_FILE,"w") as f:
            f.write("\n".join(hist[-200:]))
    except Exception: pass

def conv_cmd(parts):
    if len(parts) != 3:
        print(R + "Penggunaan: conv <angka> <basis_tujuan (2/8/10/16)>" + W)
        return
    
    try:
        n = int(parts[1], 0)
        base = int(parts[2])
        
        print(C_BOX + f"BASE CONVERT > Desimal: {n}" + W)
        if base == 2: print(f"Biner: {bin(n)}")
        elif base == 8: print(f"Oktal: {oct(n)}")
        elif base == 10: print(f"Desimal: {str(n)}")
        elif base == 16: print(f"Heksadesimal: {hex(n)}")
        else: print(R + "Error: Basis harus 2, 8, 10, atau 16." + W)
    except Exception: 
        print(R + "Error konversi: Format angka tidak valid." + W)

def prog_view(x):
    try:
        n = int(x, 0)
        print(C_BOX + BOLD + "┌— MODE PROGRAMMER —" + W)
        print(f" {C_NEON}DESIMAL (DEC):{W} {n}")
        print(f" {C_NEON}HEKSADESIMAL (HEX):{W} {hex(n)}")
        print(f" {C_NEON}OKTAL (OCT):{W} {oct(n)}")
        print(f" {C_NEON}BINER (BIN):{W} {bin(n)}")
        print(C_BOX + BOLD + "└——————————————————" + W)
    except Exception: 
        print(R + "Error: Format angka tidak valid." + W)

# --- Fungsi Untuk Menampilkan Menu Utama (Header) ---
def display_main_menu():
    os.system('clear')
    print_banner()
    
    # Header Info & Waktu
    print(C_BOX + "══════════════════════════════════════════════════════════" + W)
    print(f"{C_BOX} [ {C_NEON}{datetime.now().strftime('%H:%M:%S')}{C_BOX} ] {BOLD}Erald Calculator | Aman, Canggih, & Profesional" + W)
    print(C_BOX + "══════════════════════════════════════════════════════════" + W)
    
    print(f"{BOLD}{ULINE}PANDUAN PENGGUNAAN INTERAKTIF:{W}")
    print(f"Ketik '{C_NEON}bantuan{W}' untuk melihat daftar fungsi lengkap.")
    
    # Daftar Perintah Utama yang Jelas
    print("\n" + C_BOX + "1. PERHITUNGAN DASAR & ILMIAH (TIPE: Ekspresi)" + W)
    print(f"   • Ketik ekspresi matematika: {BOLD}10 * (sin(pi/6)) + akar(81){W}")
    print(f"   • {C_NEON}Fitur Canggih:{W} Mendukung: {BOLD}+, -, *, /, **, %{W} dan fungsi ilmiah.")
    
    print("\n" + C_BOX + "2. STATISTIK 📊 & GEOMETRI 📐 (FITUR CANGGIH: Fungsi Khusus)" + W)
    print(f"   • {BOLD}stat([angka, ...]){W} : Hitung Rata-rata, Median, Modus.")
    print(f"     Contoh: {C_NEON}stat([1, 2, 2, 4, 6]){W}")
    print(f"   • {BOLD}luas('jenis', arg1, ...){W} : Hitung Luas Bangun Datar.")
    print(f"     Contoh: {C_NEON}luas('lingkaran', 7){W}")
    
    print("\n" + C_BOX + "3. KONVERSI & NAVIGASI (TIPE: Command)" + W)
    print(f"   • {BOLD}prog <angka>{W} : Tampilkan Desimal, Hexa, Oktal, Biner.")
    print(f"     Contoh: {C_NEON}prog 0xbeef{W}")
    print(f"   • {BOLD}menu{W} : Kembali menampilkan panduan ini.")
    print(f"   • {BOLD}keluar{W} : Tutup program.")
    
    print(C_BOX + "══════════════════════════════════════════════════════════" + W)

# --- Fungsi Utama REPL (Read-Eval-Print Loop) ---
def repl():
    hist = history_load()
    display_main_menu() # Panggil menu di awal
    
    while True:
        try:
            # Prompt Hijau Terang Profesional
            s = input(G + BOLD + "EraldCalc > " + W).strip()
        except (EOFError, KeyboardInterrupt):
            print("\n" + R + BOLD + "Keluar dari Erald Calculator. Sampai jumpa!" + W); break
        
        if not s: continue
        if s.lower() in ("exit","quit","keluar"): break
        
        if s.lower() in ("menu", "main"): # Perintah: Kembali ke Menu Utama
            display_main_menu(); continue
        
        if s.lower() in ("help", "bantuan"):
            func_list = ", ".join(sorted(k for k in SAFE_FUNCS if k[0].isalpha() and k not in ('luas', 'stat', 'umur', 'hari_sejak', 'tahun_ini')))
            print(f"""
{C_NEON}{BOLD}Panduan Penggunaan Lengkap Erald Calculator{W}

{C_BOX}FUNGSI STATISTIK, GEOMETRI & WAKTU:{W}
   • {BOLD}stat([angka, ...]){W} : Mean, Median, Modus (Contoh: stat([1, 2, 3]))
   • {BOLD}luas('jenis', arg1, ...){W} : Luas bangun datar.
   • {BOLD}umur(YYYY){W}, {BOLD}hari_sejak(YYYY,MM,DD){W}

{C_BOX}FUNGSI ILMIAH & MATEMATIKA DASAR:{W}
{func_list}
(Contoh penggunaan: {BOLD}akar(25){W}, {BOLD}bulatkan(3.1415, 2){W})

{C_BOX}Perintah Utilitas Tambahan:{W}
   • {BOLD}prog <angka>{W}, {BOLD}conv <angka> <basis>{W}, {BOLD}menu{W}, {BOLD}history{W}, {BOLD}clear{W}.
""")
            continue
        
        # Command Handling
        parts = s.split()
        cmd = parts[0].lower()
        
        if cmd == "conv":
            conv_cmd(parts); hist.append(s); history_save(hist); continue
        elif cmd == "prog":
            if len(parts) > 1: prog_view(parts[1]); hist.append(s); history_save(hist); continue
            else: print(R + "Error: Perintah prog memerlukan argumen angka." + W); continue
        elif cmd == "history":
            print(C_BOX + "--- RIWAYAT PERHITUNGAN (50 terakhir) ---" + W)
            for i,l in enumerate(hist[-50:],start=1): print(f"{C_NEON}{i:02}.{W} {l}")
            print(C_BOX + "----------------------------------------" + W)
            continue
        elif cmd == "clear":
            hist = []; history_save(hist); print(C_BOX + "Riwayat telah dihapus." + W); continue
        
        # Expression Evaluation
        try:
            res = safe_eval(s)
            
            # Tampilan Hasil yang Menonjol dan Profesional
            print(C_BOX + BOLD + "┌— HASIL —" + W)
            
            # Penanganan khusus untuk output STATISTIK
            if isinstance(res, str) and res.startswith('\n STATISTIK HASIL:'):
                print(res)
            else:
                print(C_RESULT + BOLD + str(res) + W)
            
            print(C_BOX + BOLD + "└—————————" + W)
            
            hist.append(s); history_save(hist)
        except Exception as e:
            # Tampilan Error Merah Terang
            print(R + BOLD + "!! ERROR PERHITUNGAN !!" + W)
            print(R + str(e) + W)

if __name__ == "__main__":
    if readline.get_current_history_length() > 0:
        readline.clear_history()
    repl()