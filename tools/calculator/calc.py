#!/data/data/com.termux/files/usr/bin/env python3
# EraldForge - Calculator (upgraded)
import os, ast, math, readline, sys
from fractions import Fraction
from datetime import datetime
HOME = os.path.expanduser("~")
HIST_FILE = os.path.join(HOME, ".eraldforge_calc_history")

# themes
def get_theme():
    t = os.environ.get("ERALDFORGE_THEME","").lower()
    if t in ("hacker","clean"): return t
    ans = input("Pilih tema [hacker/clean] (enter default hacker): ").strip().lower()
    return ans if ans in ("hacker","clean") else "hacker"

THEME = get_theme()
if THEME=="hacker":
    R="\033[31m"; G="\033[32m"; C="\033[36m"; W="\033[0m"; BOLD="\033[1m"
else:
    R="\033[31m"; G="\033[34m"; C="\033[36m"; W="\033[0m"; BOLD="\033[1m"

SAFE_FUNCS = {
    'sqrt': math.sqrt, 'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
    'log': math.log, 'log10': math.log10, 'exp': math.exp,
    'pow': pow, 'abs': abs, 'round': round, 'floor': math.floor, 'ceil': math.ceil,
    'pi': math.pi, 'e': math.e, 'Fraction': Fraction
}

ALLOWED = (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Num, ast.Constant,
           ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow, ast.Mod, ast.FloorDiv,
           ast.USub, ast.UAdd, ast.Call, ast.Load, ast.Name, ast.Tuple, ast.List,
           ast.BitXor, ast.BitAnd, ast.BitOr, ast.LShift, ast.RShift)

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
        if fname not in SAFE_FUNCS: raise ValueError(f"Function {fname} not allowed")
        args=[self.visit(a) for a in node.args]
        return SAFE_FUNCS[fname](*args)
    def visit_Name(self,node):
        if node.id in SAFE_FUNCS: return SAFE_FUNCS[node.id]
        raise ValueError(f"Name {node.id} not allowed")

def safe_eval(expr):
    node=ast.parse(expr,mode='eval')
    return SafeEval().visit(node)

def history_load():
    try:
        with open(HIST_FILE) as f:
            return [l.strip() for l in f.readlines() if l.strip()]
    except: return []

def history_save(hist):
    try:
        with open(HIST_FILE,"w") as f:
            f.write("\n".join(hist[-200:]))
    except: pass

def conv_cmd(parts):
    try:
        n=int(parts[1],0); base=int(parts[2])
        if base==2: print(bin(n))
        elif base==8: print(oct(n))
        elif base==10: print(str(n))
        elif base==16: print(hex(n))
        else: print("Base must be 2/8/10/16")
    except Exception as e: print("Error:",e)

def prog_view(x):
    try:
        n=int(x,0)
        print(f"dec: {n}\nhex: {hex(n)}\noct: {oct(n)}\nbin: {bin(n)}")
    except: print("Invalid number")

def repl():
    print(G + BOLD + "EraldForge Calculator — interactive. Type 'help'." + W)
    hist = history_load()
    while True:
        try:
            s=input(G+"calc> "+W).strip()
        except (EOFError,KeyboardInterrupt):
            print(); break
        if not s: continue
        if s in ("exit","quit"): break
        if s=="help":
            print("""Commands:
  conv <num> <base>   convert number
  prog <num>          show bin/hex/oct
  history             show history
  clear               clear history
  help                this help
  exit                quit
You can use functions: """ + ", ".join(sorted(k for k in SAFE_FUNCS if k.isalpha())))
            continue
        if s.startswith("conv "):
            conv_cmd(s.split()); hist.append(s); history_save(hist); continue
        if s.startswith("prog "):
            prog_view(s.split()[1]); hist.append(s); history_save(hist); continue
        if s=="history":
            for i,l in enumerate(hist[-50:],start=1): print(i,l)
            continue
        if s=="clear":
            hist=[]; history_save(hist); print("History cleared."); continue
        try:
            res = safe_eval(s)
            print(C + str(res) + W)
            hist.append(s); history_save(hist)
        except Exception as e:
            print(R + "Error: " + str(e) + W)

if __name__=="__main__":
    repl()
