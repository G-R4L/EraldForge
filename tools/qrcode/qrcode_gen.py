#!/data/data/com.termux/files/usr/bin/env python3
"""
EraldForge - QR Code Generator
Requires: python qrcode pillow  (install via pip: pip install qrcode pillow)
Outputs:
 - ASCII preview in terminal
 - writes PNG file to current directory
"""
import os, sys
from pathlib import Path

try:
    import qrcode
except Exception:
    qrcode = None

def ascii_qr(matrix):
    # matrix: list of lists of booleans
    # use '██' for dark and '  ' for light for square shape
    out = []
    for row in matrix:
        line = "".join("██" if v else "  " for v in row)
        out.append(line)
    return "\n".join(out)

def main():
    print("EraldForge — QR Code Generator")
    data = input("Enter text or URL to encode: ").strip()
    if not data:
        print("No input given.")
        return
    filename = input("Output filename (without ext) [erald_qr]: ").strip() or "erald_qr"
    png_path = Path.cwd() / (filename + ".png")

    if qrcode is None:
        print("Library 'qrcode' not installed. Install with:\n  pip install qrcode pillow")
        # fallback: try creating simple ASCII with replacement (not a real QR)
        print("\nFallback: printing raw text (install qrcode to create real QR image):\n")
        print(data)
        return

    qr = qrcode.QRCode(border=2, box_size=1)
    qr.add_data(data)
    qr.make(fit=True)
    matrix = qr.get_matrix()  # list of lists True/False
    print("\nASCII preview:\n")
    print(ascii_qr(matrix))
    # generate PNG
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(str(png_path))
    print(f"\nSaved PNG: {png_path}")
    # try to copy path to clipboard
    try:
        import subprocess
        subprocess.run(["termux-clipboard-set", str(png_path)])
    except Exception:
        pass

if __name__=="__main__":
    main()
