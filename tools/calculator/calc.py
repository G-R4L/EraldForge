#!/data/data/com.termux/files/usr/bin/env python3
# EraldForge - Calculator (Advanced, Secure, and Modern REPL)

import os, ast, math, readline, sys
from fractions import Fraction
from datetime import datetime
import textwrap
import time

# --- Konfigurasi Dasar ---
HOME = os.path.expanduser("~")
HIST_FILE = os.path.join(HOME, ".eraldforge_calc_history")
WAKTU_SEKARANG = datetime.now()

# --- Definisi Warna (Skema Profesional Neon) ---
R = "\033[91m"     # Merah Terang (Error)
G = "\033[92m"     # Hijau Terang (Prompt Input)
C_BANNER_DARK = "\033[96m"  # Cyan Terang (Garis Box, Info, dan Batas)
C_BANNER_LIGHT = "\033[93m" # Kuning Terang/Neon (Teks "Calculator")
C_RESULT = "\033[97m"  # Putih Terang (Hasil)
W = "\033[0m"
BOLD = "\033[1m"

# --- Banner ASCII ---
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
    """Mencetak banner: Box Cyan Terang, Teks Kuning Neon."""
    for line in BANNER_LINES:
        # Pewarnaan Teks Calculator menjadi Kuning Neon (C_BANNER_LIGHT)
        # dan memastikan karakter box (:, |, /, \) berwarna Cyan Terang (C_BANNER_DARK)
        colored_line = (
            C_BANNER_DARK + line[0:3] + W + # Sisi kiri box (termasuk :)
            C_BANNER_LIGHT + line[3:30].replace(' ', ' ') + W + # Teks Calculator (Kucing Neon)
            C_BANNER_DARK + line[30:] + W # Sisi kanan box (termasuk :)
        )
        print(colored_line)

# --- Lingkungan Matematika Aman (Safe Math Environment) ---
SAFE_FUNCS = {
    'akar': math.sqrt, 'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
    'log': math.log, 'log10': math.log10, 'exp': math.exp,
    'pangkat': pow, 'abs': abs, 'bulatkan': round, 
    'bulatkan_bawah': math.floor, 'bulatkan_atas': math.ceil,
    'pi': math.pi, 'e': math.e, 'Pecahan': Fraction,
    'umur': lambda y: WAKTU_SEKARANG.year - y,
    'hari_sejak': lambda y,m,d: (WAKTU_SEKARANG - datetime(y,m,d)).days,
    'tahun_ini': lambda: WAKTU_SEKARANG.year
}

ALLOWED_NODES = (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Num, ast.Constant,
                 ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow, ast.Mod, ast.FloorDiv,
                 ast.USub, ast.UAdd, ast.Call, ast.Load, ast.Name, ast.Tuple, ast.List,
                 ast.BitXor, ast.BitAnd, ast.BitOr, ast.LShift, ast.RShift)

# --- Kelas SafeEval (Tidak ada perubahan signifikan) ---
class SafeEval(ast.NodeVisitor):
    def generic_visit(self, node):
        if type(node) not in ALLOWED_NODES:
            raise ValueError(f"Ekspresi/Node '{type(node).__name__}' tidak diizinkan.")
        return super().generic_visit(node)
        
    def visit_Expression(self, node): return self.visit(node.body)
        
    def visit_BinOp(self, node):
        l, r = self.visit(node.left), self.visit(node.right)
        op = node.op
        ops = {
            ast.Add: l + r, ast.Sub: l - r, ast.Mult: l * r, ast.Div: l / r,
            ast.FloorDiv: l // r, ast.Mod: l % r, ast.Pow: l ** r,
            ast.BitXor: l ^ r, ast.BitAnd: l & r, ast.BitOr: l | r,
            ast.LShift: l << r, ast.RShift: l >> r
        }
        if type(op) in ops: return ops[type(op)]
        raise ValueError("Operator tidak didukung")

    def visit_UnaryOp(self, node):
        v = self.visit(node.operand)
        if isinstance(node.op, ast.UAdd): return +v
        if isinstance(node.op, ast.USub): return -v
        raise ValueError("Operator Unary tidak diizinkan")
        
    def visit_Num(self, node): return node.n
    def visit_Constant(self, node):
        if isinstance(node.value, (int, float)): return node.value
        raise ValueError("Hanya konstanta numerik (angka).")

    def visit_Call(self, node):
        if not isinstance(node.func, ast.Name): raise ValueError("Hanya pemanggilan fungsi sederhana")
        fname = node.func.id
        if fname not in SAFE_FUNCS: raise ValueError(f"Fungsi '{fname}' tidak diizinkan")
        args = [self.visit(a) for a in node.args]
        return SAFE_FUNCS[fname](*args)
        
    def visit_Name(self, node):
        if node.id in SAFE_FUNCS: return SAFE_FUNCS[node.id]
        raise ValueError(f"Nama/Variabel '{node.id}' tidak diizinkan")

def safe_eval(expr):
    node = ast.parse(expr, mode='eval')
    return SafeEval().visit(node)

# --- Fungsi Utilitas (Riwayat, Konversi) ---
def history_load():
    try:
        if os.path.exists(HIST_FILE):
            with open(HIST_FILE) as f:
                return [l.strip() for l in f.readlines() if l.strip()]
    except Exception: return []
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
        
        print(C_BANNER_DARK + f"Desimal: {n}" + W)
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
        print(C_BANNER_DARK + "—" * 25 + W)
        print(C_BANNER_DARK + BOLD + "Tampilan Programmer" + W)
        print(f" {BOLD}DESIMAL (DEC):{W} {n}")
        print(f" {BOLD}HEKSADESIMAL (HEX):{W} {hex(n)}")
        print(f" {BOLD}OKTAL (OCT):{W} {oct(n)}")
        print(f" {BOLD}BINER (BIN):{W} {bin(n)}")
        print(C_BANNER_DARK + "—" * 25 + W)
    except Exception: 
        print(R + "Error: Format angka tidak valid." + W)

# --- Fungsi Utama REPL (Read-Eval-Print Loop) ---
def repl():
    os.system('clear')
    print_banner()
    print(C_BANNER_DARK + "—" * 53 + W)
    
    func_list = ", ".join(sorted(k for k in SAFE_FUNCS if k[0].isalpha()))
    
    help_text = f"""{BOLD}EraldForge Kalkulator v3.1 | Aman & Multifungsi{W}
Ketik '{BOLD}bantuan{W}' untuk panduan, '{BOLD}keluar{W}' untuk menutup.
{C_BANNER_DARK}Tanggal Server: {WAKTU_SEKARANG.strftime("%d-%m-%Y %H:%M:%S")}{W}

{C_BANNER_DARK}Fungsi Tersedia:{W} {func_list}
"""
    print(textwrap.fill(help_text, width=os.get_terminal_size().columns))
    print(C_BANNER_DARK + "—" * 53 + W)
    
    hist = history_load()
    while True:
        try:
            s = input(G + BOLD + "EFC> " + W).strip()
        except (EOFError, KeyboardInterrupt):
            print("\n" + R + BOLD + "Sampai jumpa! Keluar dari kalkulator." + W); break
        
        if not s: continue
        if s.lower() in ("exit","quit","keluar"): break
        
        if s.lower() in ("help", "bantuan"):
            print(f"""
{BOLD}Panduan Penggunaan Kalkulator ({C_BANNER_DARK}Mode Canggih{W}){W}

{BOLD}1. Perhitungan Dasar & Ilmiah:{W}
   Cukup ketik ekspresi matematika Anda.
   Contoh: {BOLD}(10 * sin(pi/6)) / 2 + akar(144){W}

{BOLD}2. Konversi Basis Angka (Programmer):{W}
   - {BOLD}prog <angka>{W} : Tampilkan Desimal, Hexa, Oktal, Biner.
     Contoh: {BOLD}prog 123456{W} atau {BOLD}prog 0xFF{W}
   - {BOLD}conv <angka> <basis>{W} : Konversi ke basis tertentu (2/8/10/16).
     Contoh: {BOLD}conv 0b10110 10{W} (Biner ke Desimal)

{BOLD}3. Fungsi Waktu & Pecahan:{W}
   - {BOLD}umur(YYYY){W}
   - {BOLD}hari_sejak(YYYY, MM, DD){W}
   - {BOLD}Pecahan(num, den){W}

{BOLD}4. Perintah Utilitas:{W}
   - {BOLD}history{W} : Tampilkan riwayat.
   - {BOLD}clear{W} : Hapus riwayat.
   - {BOLD}keluar{W} / {BOLD}exit{W} : Tutup kalkulator.
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
            print(C_BANNER_DARK + "--- Riwayat (50 terakhir) ---" + W)
            for i,l in enumerate(hist[-50:],start=1): print(f"{i:02}. {l}")
            print(C_BANNER_DARK + "----------------------------" + W)
            continue
        elif cmd == "clear":
            hist = []; history_save(hist); print(C_BANNER_DARK + "Riwayat telah dihapus." + W); continue
        
        # Expression Evaluation
        try:
            res = safe_eval(s)
            
            # Peningkatan tampilan hasil: Tambahkan pemisah visual (Cyan Terang)
            print(C_BANNER_DARK + "=" * 10 + W)
            print(C_RESULT + BOLD + str(res) + W)
            print(C_BANNER_DARK + "=" * 10 + W)
            
            hist.append(s); history_save(hist)
        except Exception as e:
            print(R + BOLD + "Error: " + W + str(e))

if __name__ == "__main__":
    if readline.get_current_history_length() > 0:
        readline.clear_history()
    repl()