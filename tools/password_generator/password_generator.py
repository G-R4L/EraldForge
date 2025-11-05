#!/data/data/com.termux/files/usr/bin/env python3
"""
EraldForge - Password Generator
usage: run and ikuti prompt
"""
import os, secrets, string

def get_theme_colors():
    t = os.environ.get("ERALDFORGE_THEME","clean")
    if t=="hacker":
        return {"p":"\033[32m","r":"\033[31m","x":"\033[0m","b":"\033[36m"}
    else:
        return {"p":"\033[34m","r":"\033[31m","x":"\033[0m","b":"\033[36m"}

C = get_theme_colors()

def generate_password(length=16, use_upper=True, use_digits=True, use_symbols=True, avoid_ambiguous=True):
    alphabet = list(string.ascii_lowercase)
    if use_upper: alphabet += list(string.ascii_uppercase)
    if use_digits: alphabet += list(string.digits)
    if use_symbols: alphabet += list("!@#$%^&*()-_=+[]{};:,.<>?")
    if avoid_ambiguous:
        for ch in "Il1O0":
            if ch in alphabet:
                alphabet.remove(ch)
    if not alphabet:
        raise ValueError("No characters available for password generation.")
    return "".join(secrets.choice(alphabet) for _ in range(length))

def main():
    print(C["p"] + "EraldForge — Password Generator" + C["x"])
    try:
        length = int(input("Length (8-64) [16]: ").strip() or "16")
        if length < 4: length = 4
        if length > 256: length = 256
    except:
        length = 16
    ucase = input("Include uppercase? [Y/n]: ").strip().lower()
    digits = input("Include digits? [Y/n]: ").strip().lower()
    syms = input("Include symbols? [Y/n]: ").strip().lower()
    amb = input("Avoid ambiguous chars (Il1O0)? [Y/n]: ").strip().lower()

    pw = generate_password(
        length=length,
        use_upper=(ucase!="n"),
        use_digits=(digits!="n"),
        use_symbols=(syms!="n"),
        avoid_ambiguous=(amb!="n")
    )
    print("\nGenerated password:\n")
    print(C["b"] + pw + C["x"])
    # optionally copy to clipboard if termux-clipboard-set exists
    try:
        subprocess = __import__("subprocess")
        subprocess.run(["termux-clipboard-set", pw])
        print("\nPassword copied to clipboard (termux-clipboard-set).")
    except Exception:
        pass

if __name__=="__main__":
    main()
