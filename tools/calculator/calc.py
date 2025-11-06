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
C_BANNER_DARK = "\033[96m" # Cyan Terang (Bagian gelap banner)
C_BANNER_LIGHT = "\033[93m" # Kuning Terang (Bagian terang banner)
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
    """Mencetak banner dengan pewarnaan dua tone (Cyan Terang dan Kuning Terang)."""
    out = []
    
    # Pewarnaan Kustom (Mengganti C_BANNER_DARK dan C_BANNER_LIGHT sesuai baris)
    for line in BANNER_LINES:
        if line.strip().startswith("·"): # Garis tepi
            out.append(C_BANNER_DARK + line + W)
        else:
            # Pewarnaan untuk huruf dan simbol
            # Karakter ':', '/', '|'
            colored_line = (
                C_BANNER_DARK + line[0] + line[1] + line[2] + W + # Sisi Kiri
                C_BANNER_LIGHT + line[3:30] + W + # Bagian terang (CALC)
                C_BANNER_DARK + line[30:] + W # Sisi Kanan
            )
            out.append(colored_line)
    
    print("\n".join(out))

# --- Safe Math Environment ---
SAFE_FUNCS = {
    'sqrt': math.sqrt, 'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
    'log': math.log, 'log10': math.log10, 'exp': math.exp,
    'pow': pow, 'abs': abs, 'round': round, 'floor': math.floor, 'ceil': math.ceil,
    'pi': math.pi, 'e': math.e, 'Fraction': Fraction,
    # Fungsi tambahan: Menghitung umur/hari
    'age': lambda y: datetime.now().year - y,
    'days_since': lambda y,m,d: (datetime.now() - datetime(y,m,d)).days
}

ALLOWED = (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Num, ast.Constant,
           ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow, ast.Mod, ast.FloorDiv,
           ast.USub, ast.UAdd, ast.Call, ast.Load, ast.Name, ast.Tuple, ast.List,
           ast.BitXor, ast.BitAnd, ast.BitOr, ast.LShift, ast.RShift)

# --- AST Node Visitor for Safe Evaluation ---
class SafeEval(ast.NodeVisitor):
    def visit(self,node):
        if type(node) not in ALLOWED:
            raise ValueError("Disallowed expression")
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
        raise ValueError("Unsupported op")
    def visit_UnaryOp(self,node):
        v=self.visit(node.operand)
        if isinstance(node.op,ast.UAdd): return +v
        if isinstance(node.op,ast.USub): return -v
        raise ValueError("Unary op disallowed")
    def visit_Num(self,node): return node.n
    def visit_Constant(self,node):
        if isinstance(node.value,(int,float)): return node.value
        raise ValueError("Only numeric constants")
    def visit_Call(self,node):
        if not isinstance(node.func,ast.Name): raise ValueError("Only simple function calls")
        fname=node.func.id
        if fname not in SAFE_FUNCS: raise ValueError(f"Function '{fname}' not allowed")
        args=[self.visit(a) for a in node.args]
        return SAFE_FUNCS[fname](*args)
    def visit_Name(self,node):
        if node.id in SAFE_FUNCS: return SAFE_FUNCS[node.id]
        raise ValueError(f"Name '{node.id}' not allowed")

def safe_eval(expr):
    node=ast.parse(expr,mode='eval')
    return SafeEval().visit(node)

# --- History and Utility Functions ---
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
        print(R + "Usage: conv <number> <base_to (2/8/10/16)>" + W)
        return
    
    try:
        # Int(string, 0) akan menginterpretasikan basis dari prefix (0x, 0o, 0b)
        n=int(parts[1], 0)
        base=int(parts[2])
        
        print(f"Decimal: {n}")
        if base==2: print(f"Binary: {bin(n)}")
        elif base==8: print(f"Octal: {oct(n)}")
        elif base==10: print(f"Decimal: {str(n)}")
        elif base==16: print(f"Hexadecimal: {hex(n)}")
        else: print(R + "Error: Base must be 2, 8, 10, or 16." + W)
    except ValueError:
        print(R + "Error: Invalid number or base." + W)
    except Exception as e: 
        print(R + "Error: " + str(e) + W)

def prog_view(x):
    """Tampilan mode programmer: prog <num>"""
    try:
        n=int(x,0)
        print(C_BANNER_DARK + "--- Programmer View ---" + W)
        print(f" {BOLD}DEC:{W} {n}")
        print(f" {BOLD}HEX:{W} {hex(n)}")
        print(f" {BOLD}OCT:{W} {oct(n)}")
        print(f" {BOLD}BIN:{W} {bin(n)}")
    except ValueError: 
        print(R + "Error: Invalid number format. Use 10, 0x, 0o, or 0b." + W)
    except Exception:
        print(R + "Error: Could not process number." + W)

def repl():
    os.system('clear')
    print_banner()
    print(C_BANNER_DARK + "—" * 53 + W)
    
    func_list = ", ".join(sorted(k for k in SAFE_FUNCS if k[0].isalpha()))
    help_text = f"""{BOLD}EraldForge Calculator v{os.environ.get("ERALDFORGE_VERSION", "2.x")}{W}
Type '{BOLD}help{W}' for commands, '{BOLD}exit{W}' to quit.

{C_BANNER_DARK}Available Functions:{W} {func_list}
{C_BANNER_DARK}Special Functions:{W} age(year), days_since(y,m,d)
"""
    print(textwrap.fill(help_text, width=os.get_terminal_size().columns))
    print(C_BANNER_DARK + "—" * 53 + W)
    
    hist = history_load()
    while True:
        try:
            # Menggunakan Hijau Terang untuk prompt input
            s=input(G + BOLD + "EFC> " + W).strip()
        except (EOFError,KeyboardInterrupt):
            print(R + "Exiting..." + W); break
        
        if not s: continue
        if s in ("exit","quit"): break
        
        if s=="help":
            print(f"""
{BOLD}Commands:{W}
 {BOLD}conv{W} <num> <base> - Convert number to base (2/8/10/16).
 {BOLD}prog{W} <num>       - Show binary, hexadecimal, and octal for number.
 {BOLD}history{W}         - Show last 50 entries.
 {BOLD}clear{W}           - Clear history file.
 {BOLD}help{W}            - Show this help.
 {BOLD}exit{W}            - Quit calculator.
""")
            continue
        
        # Command Handling
        parts = s.split()
        cmd = parts[0]
        if cmd=="conv":
            conv_cmd(parts); hist.append(s); history_save(hist); continue
        if cmd=="prog":
            if len(parts) > 1: prog_view(parts[1]); hist.append(s); history_save(hist); continue
            else: print(R + "Error: prog requires a number argument." + W); continue
        if cmd=="history":
            print(C_BANNER_DARK + "--- History (last 50) ---" + W)
            for i,l in enumerate(hist[-50:],start=1): print(f"{i:02}. {l}")
            print(C_BANNER_DARK + "-------------------------" + W)
            continue
        if cmd=="clear":
            hist=[]; history_save(hist); print(C_BANNER_DARK + "History cleared." + W); continue
        
        # Expression Evaluation
        try:
            res = safe_eval(s)
            print(C_RESULT + str(res) + W)
            hist.append(s); history_save(hist)
        except Exception as e:
            print(R + BOLD + "Error: " + W + str(e))

if __name__=="__main__":
    # Menghapus readline history default agar tidak mengganggu history kustom
    if readline.get_current_history_length() > 0:
        readline.clear_history() 
    repl()