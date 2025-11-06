#!/data/data/com.termux/files/usr/bin/env python3
# EraldForge - Calculator (Project Zenith: Total Rework)

import os, ast, math, readline, sys
from fractions import Fraction
from datetime import datetime
import textwrap
import time

# --- Konfigurasi Dasar ---
HOME = os.path.expanduser("~")
HIST_FILE = os.path.join(HOME, ".eraldforge_calc_history")
WAKTU_SEKARANG = datetime.now()

# --- Definisi Warna (Skema Zenith: Neon Kuning & Cyan) ---
R = "\033[91m"     # Merah Terang (Error)
G = "\033[92m"     # Hijau Terang (Prompt Input)
C_BOX = "\033[96m"  # Cyan Terang (Garis Box, Batas, Info)
C_NEON = "\033[93m" # Kuning Terang/Neon (Full Banner & Highlighting)
C_RESULT = "\033[97m"  # Putih Terang (Hasil Perhitungan)
W = "\033[0m"
BOLD = "\033[1m"

# --- Banner ASCII Klasik (FULL NEON) ---
# Menggunakan format ASCII klasik yang diminta
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
    out = [C_NEON + line.replace(" ", " ") + W for line in BANNER_LINES]
    print("\n".join(out))

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

# --- Kelas SafeEval (Inti Logika - Tetap Canggih & Aman) ---
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
        print(C_BOX + BOLD + "┌— PROGRAMMER MODE —" + W)
        print(f" {C_NEON}DESIMAL (DEC):{W} {n}")
        print(f" {C_NEON}HEKSADESIMAL (HEX):{W} {hex(n)}")
        print(f" {C_NEON}OKTAL (OCT):{W} {oct(n)}")
        print(f" {C_NEON}BINER (BIN):{W} {bin(n)}")
        print(C_BOX + BOLD + "└—————————————————" + W)
    except Exception: 
        print(R + "Error: Format angka tidak valid." + W)

# --- Fungsi Utama REPL (Read-Eval-Print Loop) ---
def repl():
    os.system('clear')
    print_banner()
    # Menggunakan C_BOX untuk garis pemisah informasi
    print(C_BOX + " Versi 3.3: Aman | Modern | Multifungsi" + W)
    print(C_BOX + "—" * 53 + W) # Garis sepanjang banner (53 karakter)
    
    func_list = ", ".join(sorted(k for k in SAFE_FUNCS if k[0].isalpha()))
    
    help_text = f"""{BOLD}EraldForge Kalkulator Project Zenith{W}
Ketik '{C_NEON}bantuan{W}' untuk panduan, '{C_NEON}keluar{W}' untuk menutup.
{C_BOX}Waktu Server: {WAKTU_SEKARANG.strftime("%d-%m-%Y %H:%M:%S")}{W}

{C_BOX}Fungsi Tersedia:{W} {func_list}
"""
    print(textwrap.fill(help_text, width=os.get_terminal_size().columns))
    print(C_BOX + "—" * 53 + W) # Garis sepanjang banner (53 karakter)
    
    hist = history_load()
    while True:
        try:
            # Prompt Hijau Terang (Standard High-Tech Input)
            s = input(G + BOLD + "EFC_ZENITH > " + W).strip()
        except (EOFError, KeyboardInterrupt):
            print("\n" + R + BOLD + "Keluar dari Project Zenith. Sampai jumpa!" + W); break
        
        if not s: continue
        if s.lower() in ("exit","quit","keluar"): break
        
        if s.lower() in ("help", "bantuan"):
            print(f"""
{C_NEON}Panduan Penggunaan Kalkulator (Project Zenith){W}

{C_BOX}1. Perhitungan Dasar & Ilmiah:{W}
   Ketik ekspresi matematika Anda. (Contoh: {BOLD}(10 * sin(pi/6)) / 2 + akar(144){W})

{C_BOX}2. Mode Programmer (Konversi Basis):{W}
   - {BOLD}prog <angka>{W} : Tampilkan Desimal, Hexa, Oktal, Biner.
     (Contoh: {C_NEON}prog 0xBE EF{W} atau {C_NEON}prog 1000{W})
   - {BOLD}conv <angka> <basis>{W} : Konversi ke basis tertentu (2/8/10/16).
     (Contoh: {C_NEON}conv 0b10110 10{W})

{C_BOX}3. Fungsi Waktu & Pecahan:{W}
   - {BOLD}umur(YYYY){W} (Contoh: {C_NEON}umur(1995){W})
   - {BOLD}hari_sejak(YYYY, MM, DD){W} (Contoh: {C_NEON}hari_sejak(2023, 1, 1){W})
   - {BOLD}Pecahan(num, den){W} (Contoh: {C_NEON}Pecahan(2/3) + Pecahan(1/4){W})

{C_BOX}4. Perintah Utilitas:{W}
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
            print(C_BOX + "--- RIWAYAT PERHITUNGAN (50 terakhir) ---" + W)
            for i,l in enumerate(hist[-50:],start=1): print(f"{C_NEON}{i:02}.{W} {l}")
            print(C_BOX + "----------------------------------------" + W)
            continue
        elif cmd == "clear":
            hist = []; history_save(hist); print(C_BOX + "Riwayat telah dihapus." + W); continue
        
        # Expression Evaluation
        try:
            res = safe_eval(s)
            
            # Tampilan Hasil yang Sangat Menonjol dan Profesional
            print(C_BOX + BOLD + "┌— HASIL —" + W)
            print(C_RESULT + BOLD + str(res) + W)
            print(C_BOX + BOLD + "└—————————" + W)
            
            hist.append(s); history_save(hist)
        except Exception as e:
            print(R + BOLD + "ERROR! " + W + str(e))

if __name__ == "__main__":
    if readline.get_current_history_length() > 0:
        readline.clear_history()
    repl()