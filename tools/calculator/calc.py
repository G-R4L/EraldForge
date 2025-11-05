#!/data/data/com.termux/files/usr/bin/env python3
"""
EraldForge - Calculator
Usage examples:
  calc.py "2+2"
  calc.py "sqrt(16) + pi"
  calc.py conv 255 16
"""
import argparse, math, sys
from fractions import Fraction

SAFE_FUNCS = {
    'sqrt': math.sqrt, 'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
    'log': math.log, 'pi': math.pi, 'e': math.e, 'Fraction': Fraction,
    'abs': abs, 'round': round, 'pow': pow
}

def eval_expr(expr):
    try:
        return eval(expr, {"__builtins__": None}, SAFE_FUNCS)
    except Exception as e:
        return f"Error: {e}"

def conv(num_str, base):
    try:
        n = int(num_str)
    except:
        try:
            n = int(num_str, 0)
        except Exception as e:
            return f"Invalid number: {e}"
    if base == 2: return bin(n)
    if base == 8: return oct(n)
    if base == 16: return hex(n)
    return str(n)

def main():
    parser = argparse.ArgumentParser(prog="calc")
    parser.add_argument("expr", nargs="+", help="Expression or 'conv N BASE'")
    args = parser.parse_args()
    if args.expr[0] == "conv" and len(args.expr) == 3:
        print(conv(args.expr[1], int(args.expr[2])))
        return
    expr = " ".join(args.expr)
    print(eval_expr(expr))

if __name__ == "__main__":
    main()
