#!/data/data/com.termux/files/usr/bin/env python3
# EraldForge - Calculator (Erald Edition)
# Versi: Modern & Multifungsi

import os, ast, math, readline, sys
from fractions import Fraction
from datetime import datetime

# --- Konfigurasi Dasar ---
HOME = os.path.expanduser("~")
HIST_FILE = os.path.join(HOME, ".eraldforge_calc_history")
WAKTU_SEKARANG = datetime.now()

# --- Definisi Warna (Neon Kuning & Cyan) ---
R = "\033[91m"        # Merah Terang (Error)
G = "\033[92m"        # Hijau Terang (Input Prompt)
C_BOX = "\033[96m"    # Cyan Terang (Box / Info)
C_NEON = "\033[93m"   # Kuning Neon (Banner & Highlight)
C_RESULT = "\033[97m" # Putih Terang (Hasil)
W = "\033[0m"         # Reset
BOLD = "\033[1m"
ULINE = "\033[4m"

# --- Banner ASCII Neon ---
BANNER_LINES = [
    " ____ ___ __ ____ ",
    " /\\ _\\ /\\_ \\ /\\ \\ /\\ _\\ ",
    " \\ \\ \\L\\_\\ _ __ __ \\//\\ \\ \\_\\ \\ \\ \\L\\_\\___ _ __ __ __ ",
    " \\ \\ _\\L /\\'__\\/'__\\ \\ \\ \\ /'_ \\ \\ _\\/ __\\/\\'__\\/'_ \\ /'__\\ ",
    " \\ \\ \\L\\ \\ \\ \\ \\ \\ \\L\\ \\ \\ \\ \\ \\ \\ \\L\\ \\ \\ \\ \\L\\ \\ /\\ __/ ",
    " \\ \\____/\\ \\_\\\\ \\__/.\\_/\\____\\ \\___,_\\ \\_\\ \\ \\____/\\ \\_\\\\ \\ \\____ \\ \\____\\",
    " \\/___/ \\/_/ \\/__/\\/_/\\/____/\\/__,_/\\/_/ \\/___/ \\/_/ \\/___L\\ \\/____/",
    " /\\____/",
    " \\_/__/",
]

def print_banner():
    """Cetak banner full neon kuning."""
    out = [C_NEON + line + W for line in BANNER_LINES]
    print("\n".join(out))

# --- Lingkungan Matematika Aman ---
SAFE_FUNCS = {
    'akar': math.sqrt,
    'sin': math.sin,
    'cos': math.cos,
    'tan': math.tan,
    'log': math.log,
    'log10': math.log10,
    'exp': math.exp,
    'pangkat': pow,
    'abs': abs,
    'bulatkan': round,
    'bulatkan_bawah': math.floor,
    'bulatkan_atas': math.ceil,
    'pi': math.pi,
    'e': math.e,
    'Pecahan': Fraction,
    'umur': lambda y: WAKTU_SEKARANG.year - y,
    'hari_sejak': lambda y,m,d: (WAKTU_SEKARANG - datetime(y,m,d)).days,
    'tahun_ini': lambda: WAKTU_SEKARANG.year
}

ALLOWED_NODES = (
    ast.Expression, ast.BinOp, ast.UnaryOp, ast.Num, ast.Constant,
    ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow, ast.Mod, ast.FloorDiv,
    ast.USub, ast.UAdd, ast.Call, ast.Load, ast.Name, ast.Tuple, ast.List,
    ast.BitXor, ast.BitAnd, ast.BitOr, ast.LShift, ast.RShift
)

# --- Evaluasi Ekspresi Aman ---
class SafeEval(ast.NodeVisitor):
    def generic_visit(self, node):
        if type(node) not in ALLOWED_NODES:
            raise ValueError(f"Ekspresi/Node '{type(node).__name__}' tidak diizinkan.")
        return super().generic_visit(node)

    def visit_Expression(self, node):
        return self.visit(node.body)

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
        if isinstance(node.value, (int, float)): return node.value
        raise ValueError("Hanya konstanta numerik (angka).")

    def visit_Call(self, node):
        if not isinstance(node.func, ast.Name):
            raise ValueError("Hanya pemanggilan fungsi sederhana")
        fname = node.func.id
        if fname not in SAFE_FUNCS:
            raise ValueError(f"Fungsi '{fname}' tidak diizinkan")
        args = [self.visit(a) for a in node.args]
        return SAFE_FUNCS[fname](*args)

    def visit_Name(self, node):
        if node.id in SAFE_FUNCS: return SAFE_FUNCS[node.id]
        raise ValueError(f"Nama/Variabel '{node.id}' tidak diizinkan")

def safe_eval(expr):
    node = ast.parse(expr, mode='eval')
    return SafeEval().visit(node)

# --- Fungsi Riwayat ---
def history_load():
    try:
        if os.path.exists(HIST_FILE):
            with open(HIST_FILE) as f:
                return [l.strip() for l in f.readlines() if l.strip()]
    except: pass
    return []

def history_save(hist):
    try:
        with open(HIST_FILE,"w") as f:
            f.write("\n".join(hist[-200:]))
    except: pass

# --- Fungsi Konversi & Programmer Mode ---
def conv_cmd(parts):
    if len(parts) != 3:
        print(R + "Penggunaan: conv <angka> <basis_tujuan (2/8/10/16)>" + W)
        return
    try:
        n = int(parts[1],0)
        base = int(parts[2])
        print(C_BOX + f"BASE CONVERT > Desimal: {n}" + W)
        if base == 2: print(f"Biner: {bin(n)}")
        elif base == 8: print(f"Oktal: {oct(n)}")
        elif base == 10: print(f"Desimal: {str(n)}")
        elif base == 16: print(f"Heksadesimal: {hex(n)}")
        else: print(R + "Error: Basis harus 2, 8, 10, atau 16." + W)
    except: print(R + "Error konversi: Format angka tidak valid." + W)

def prog_view(x):
    try:
        n = int(x, 0)
        print(C_BOX + BOLD + "┌— MODE PROGRAMMER —" + W)
        print(f" {C_NEON}DESIMAL (DEC):{W} {n}")
        print(f" {C_NEON}HEKSADESIMAL (HEX):{W} {hex(n)}")
        print(f" {C_NEON}OKTAL (OCT):{W} {oct(n)}")
        print(f" {C_NEON}BINER (BIN):{W} {bin(n)}")
        print(C_BOX + BOLD + "└——————————————————" + W)
    except: print(R + "Error: Format angka tidak valid." + W)

# --- REPL Utama ---
def repl():
    os.system('clear')
    print_banner()
    print(C_BOX + "══════════════════════════════════════════════════════════" + W)
    print(C_BOX + f" Erald Calculator | Aman & Multifungsi" + W)
    print(C_BOX + "══════════════════════════════════════════════════════════" + W)
    print(f"{BOLD}{ULINE}Panduan Cepat:{W}")
    print(f"Ketik '{C_NEON}bantuan{W}' untuk detail penuh.")

    hist = history_load()
    while True:
        try: s = input(G + BOLD + "EraldCalc> " + W).strip()
        except (EOFError, KeyboardInterrupt):
            print("\n" + R + BOLD + "Keluar dari Erald Calculator. Sampai jumpa!" + W); break
        if not s: continue
        if s.lower() in ("exit","quit","keluar"): break

        if s.lower() in ("help","bantuan"):
            func_list = ", ".join(sorted(k for k in SAFE_FUNCS if k[0].isalpha()))
            print(f"""
{C_NEON}{BOLD}Panduan Lengkap Erald Calculator{W}

{C_BOX}Fungsi Matematika & Ilmiah:{W} {func_list}

{C_BOX}Contoh Fungsi Khusus:{W} {BOLD}umur(1995){W}, {BOLD}hari_sejak(2023,1,1){W}, {BOLD}Pecahan(2/3){W}

{C_BOX}Perintah Khusus:
 • {BOLD}prog <angka>{W} : Tampilkan Desimal, Hexa, Oktal, Biner
 • {BOLD}conv <angka> <basis>{W} : Konversi ke basis tertentu (2/8/10/16)
 • {BOLD}history{W} : Tampilkan riwayat 50 entri terakhir
 • {BOLD}clear{W} : Hapus semua riwayat
 • {BOLD}keluar{W}/{BOLD}exit{W} : Tutup program
""")
            continue

        parts = s.split()
        cmd = parts[0].lower()

        if cmd == "conv":
            conv_cmd(parts); hist.append(s); history_save(hist); continue
        elif cmd == "prog":
            if len(parts) > 1: prog_view(parts[1]); hist.append(s); history_save(hist); continue
            else: print(R + "Error: Perintah prog memerlukan argumen angka." + W); continue
        elif cmd == "history":
            print(C_BOX + "--- RIWAYAT PERHITUNGAN (50 terakhir) ---" + W)
            for i,l in enumerate(hist[-50:], start=1): print(f"{C_NEON}{i:02}.{W} {l}")
            print(C_BOX + "----------------------------------------" + W)
            continue
        elif cmd == "clear":
            hist = []; history_save(hist); print(C_BOX + "Riwayat telah dihapus." + W); continue

        # Ekspresi Matematika
        try:
            res = safe_eval(s)
            print(C_BOX + BOLD + "┌— HASIL —" + W)
            print(C_RESULT + BOLD + str(res) + W)
            print(C_BOX + BOLD + "└—————————" + W)
            hist.append(s); history_save(hist)
        except Exception as e:
            print(R + BOLD + "ERROR! " + W + str(e))

if __name__ == "__main__":
    if readline.get_current_history_length() > 0: readline.clear_history()
    repl()
