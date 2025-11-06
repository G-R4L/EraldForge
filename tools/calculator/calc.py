#!/data/data/com.termux/files/usr/bin/env python3
# EraldForge - Calculator (upgraded & enhanced)
import os, ast, math, readline, sys
from fractions import Fraction
from datetime import datetime
import textwrap
import time

HOME = os.path.expanduser("~")
HIST_FILE = os.path.join(HOME, ".eraldforge_calc_history")

# --- Color Definitions (Simplified/Professional Theme) ---
# Menggunakan warna terang untuk tampilan yang lebih modern & high-tech
R = "\033[91m" # Merah Terang (Error)
G = "\033[92m" # Hijau Terang (Prompt)
C_BANNER_DARK = "\033[96m" # Cyan Terang (Garis tepi banner)
C_BANNER_LIGHT = "\033[93m" # Kuning Terang/Neon (Teks "CALCULATOR" di banner)
C_RESULT = "\033[97m" # Putih Terang (Hasil)
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
    """Mencetak banner dengan pewarnaan dua tone (Cyan Terang dan Kuning Neon)."""
    out = []
    
    # Pewarnaan Kustom
    for line in BANNER_LINES:
        if line.strip().startswith("·"): # Garis tepi
            out.append(C_BANNER_DARK + line + W)
        else:
            # Pewarnaan untuk huruf dan simbol
            # Karakter ':', '/', '|'
            colored_line = (
                C_BANNER_DARK + line[0] + line[1] + line[2] + W + # Sisi Kiri (Tanda :)
                C_BANNER_LIGHT + line[3:30] + W + # Bagian Kuning Neon (Teks CALCULATOR)
                C_BANNER_DARK + line[30:] + W # Sisi Kanan (Tanda :)
            )
            out.append(colored_line)
    
    print("\n".join(out))

# --- Safe Math Environment ---
SAFE_FUNCS = {
    'akar': math.sqrt, 'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
    'log': math.log, 'log10': math.log10, 'exp': math.exp,
    'pangkat': pow, 'abs': abs, 'bulatkan': round, 'bulatkan_bawah': math.floor, 'bulatkan_atas': math.ceil,
    'pi': math.pi, 'e': math.e, 'Pecahan': Fraction,
    # Fungsi tambahan: Menghitung umur/hari
    'umur': lambda y: datetime.now().year - y,
    'hari_sejak': lambda y,m,d: (datetime.now() - datetime(y,m,d)).days
}

ALLOWED = (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Num, ast.Constant,
           ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow, ast.Mod, ast.FloorDiv,
           ast.USub, ast.UAdd, ast.Call, ast.Load, ast.Name, ast.Tuple, ast.List,
           ast.BitXor, ast.BitAnd, ast.BitOr, ast.LShift, ast.RShift)

# --- AST Node Visitor for Safe Evaluation (Tidak diubah) ---
class SafeEval(ast.NodeVisitor):
    def visit(self,node):
        if type(node) not in ALLOWED:
            raise ValueError("Ekspresi tidak diizinkan")
        return super().visit(node)
    def visit_Expression(self,node): return self.visit(node.body)
    def visit_BinOp(self,node):
        l=self.visit(node.left); r=self.visit(node.right); op=node.op
        if isinstance(op,ast.Add): return l+r
        if isinstance(op,ast.Sub): return l-r
        if isinstance(op,ast.Mult): return l*r
        if isinstance(op,ast.Div): return l/r
        if isinstance(op,ast.FloorDiv): return l//r
        if isinstance(op,ast.Mod): return l%r
        if isinstance(op,ast.Pow): return l**r
        if isinstance(op,ast.BitXor): return l^r
        if isinstance(op,ast.BitAnd): return l&r
        if isinstance(op,ast.BitOr): return l|r
        if isinstance(op,ast.LShift): return l<<r
        if isinstance(op,ast.RShift): return l>>r
        raise ValueError("Operator tidak didukung")
    def visit_UnaryOp(self,node):
        v=self.visit(node.operand)
        if isinstance(node.op,ast.UAdd): return +v
        if isinstance(node.op,ast.USub): return -v
        raise ValueError("Operator Unary tidak diizinkan")
    def visit_Num(self,node): return node.n
    def visit_Constant(self,node):
        if isinstance(node.value,(int,float)): return node.value
        raise ValueError("Hanya konstanta numerik")
    def visit_Call(self,node):
        if not isinstance(node.func,ast.Name): raise ValueError("Hanya pemanggilan fungsi sederhana")
        fname=node.func.id
        if fname not in SAFE_FUNCS: raise ValueError(f"Fungsi '{fname}' tidak diizinkan")
        args=[self.visit(a) for a in node.args]
        return SAFE_FUNCS[fname](*args)
    def visit_Name(self,node):
        if node.id in SAFE_FUNCS: return SAFE_FUNCS[node.id]
        raise ValueError(f"Nama '{node.id}' tidak diizinkan")

def safe_eval(expr):
    node=ast.parse(expr,mode='eval')
    return SafeEval().visit(node)

# --- History and Utility Functions (diterjemahkan) ---
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
    """Konversi basis: conv <num> <base_to>"""
    if len(parts) != 3:
        print(R + "Penggunaan: conv <angka> <basis_tujuan (2/8/10/16)>" + W)
        return
    
    try:
        n=int(parts[1], 0)
        base=int(parts[2])
        
        print(f"Desimal: {n}")
        if base==2: print(f"Biner: {bin(n)}")
        elif base==8: print(f"Oktal: {oct(n)}")
        elif base==10: print(f"Desimal: {str(n)}")
        elif base==16: print(f"Heksadesimal: {hex(n)}")
        else: print(R + "Error: Basis harus 2, 8, 10, atau 16." + W)
    except ValueError:
        print(R + "Error: Angka atau basis tidak valid." + W)
    except Exception as e: 
        print(R + "Error: " + str(e) + W)

def prog_view(x):
    """Tampilan mode programmer: prog <num>"""
    try:
        n=int(x,0)
        print(C_BANNER_DARK + "--- Tampilan Programmer ---" + W)
        print(f" {BOLD}DES:{W} {n}")
        print(f" {BOLD}HEX:{W} {hex(n)}")
        print(f" {BOLD}OKT:{W} {oct(n)}")
        print(f" {BOLD}BIN:{W} {bin(n)}")
    except ValueError: 
        print(R + "Error: Format angka tidak valid. Gunakan 10, 0x, 0o, atau 0b." + W)
    except Exception:
        print(R + "Error: Gagal memproses angka." + W)

def repl():
    os.system('clear')
    print_banner()
    print(C_BANNER_DARK + "—" * 53 + W)
    
    func_list = ", ".join(sorted(k for k in SAFE_FUNCS if k[0].isalpha()))
    help_text = f"""{BOLD}EraldForge Kalkulator v{os.environ.get("ERALDFORGE_VERSION", "2.x")}{W}
Kalkulator interaktif dengan fitur keamanan (safe-eval).
Ketik '{BOLD}bantuan{W}' untuk panduan, '{BOLD}keluar{W}' untuk menutup.

{C_BANNER_DARK}Fungsi yang Tersedia:{W} {func_list}
{C_BANNER_DARK}Contoh Penggunaan Fungsi Khusus:{W}
- {BOLD}umur(1995){W}
- {BOLD}hari_sejak(2023, 1, 1){W}

{C_BANNER_DARK}Contoh Ekspresi:{W}
- {BOLD}10 * (sin(pi/2) + 2) + 1{W}
- {BOLD}akar(25) + 3 * log10(100){W}
"""
    print(textwrap.fill(help_text, width=os.get_terminal_size().columns))
    print(C_BANNER_DARK + "—" * 53 + W)
    
    hist = history_load()
    while True:
        try:
            # Menggunakan Hijau Terang untuk prompt input
            s=input(G + BOLD + "EFC> " + W).strip()
        except (EOFError,KeyboardInterrupt):
            print(R + "Keluar..." + W); break
        
        if not s: continue
        if s in ("exit","quit","keluar"): break
        
        if s in ("help", "bantuan"):
            print(f"""
{BOLD}Panduan Penggunaan Kalkulator:{W}
1. {BOLD}EKSPRESI MATEMATIKA:{W} Ketik ekspresi seperti biasa.
   Contoh: 15 / 3 + 2**4

2. {BOLD}FUNGSI:{W} Gunakan fungsi yang tersedia (contoh: {BOLD}akar(9){W}, {BOLD}sin(pi/6){W}).

{BOLD}Perintah Khusus:{W}
 {BOLD}conv{W} <angka> <basis> - Konversi basis angka.
   Contoh: {BOLD}conv 0xFF 2{W} (mengkonversi 0xFF ke basis 2/biner)
 {BOLD}prog{W} <angka>       - Tampilkan Biner, Hexa, dan Oktal dari sebuah angka.
   Contoh: {BOLD}prog 45{W}
 {BOLD}history{W}           - Tampilkan 50 entri terakhir.
 {BOLD}clear{W}             - Hapus riwayat (history) yang tersimpan.
 {BOLD}bantuan{W}           - Tampilkan panduan ini.
 {BOLD}keluar{W}            - Tutup kalkulator.
""")
            continue
        
        # Command Handling
        parts = s.split()
        cmd = parts[0]
        if cmd=="conv":
            conv_cmd(parts); hist.append(s); history_save(hist); continue
        if cmd=="prog":
            if len(parts) > 1: prog_view(parts[1]); hist.append(s); history_save(hist); continue
            else: print(R + "Error: Perintah prog memerlukan argumen angka." + W); continue
        if cmd=="history":
            print(C_BANNER_DARK + "--- Riwayat (50 terakhir) ---" + W)
            for i,l in enumerate(hist[-50:],start=1): print(f"{i:02}. {l}")
            print(C_BANNER_DARK + "----------------------------" + W)
            continue
        if cmd=="clear":
            hist=[]; history_save(hist); print(C_BANNER_DARK + "Riwayat telah dihapus." + W); continue
        
        # Expression Evaluation
        try:
            res = safe_eval(s)
            print(C_RESULT + str(res) + W)
            hist.append(s); history_save(hist)
        except Exception as e:
            print(R + BOLD + "Error: " + W + str(e))

if __name__=="__main__":
    if readline.get_current_history_length() > 0:
        readline.clear_history() 
    repl()