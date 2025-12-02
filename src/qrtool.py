#!/usr/bin/env python3
"""
qrtool.py — A tiny command-line QR code generator.

Usage:
    python src/qrtool.py "https://example.com" --out qr.png
"""

import argparse
import qrcode

def build_parser():
    parser = argparse.ArgumentParser(
        description="Generate QR codes in seconds."
    )
    parser.add_argument(
        "data",
        help="The text or URL to encode into the QR code."
    )
    parser.add_argument(
        "--out",
        default="qr.png",
        help="Output filename (default: qr.png)"
    )
    parser.add_argument(
        "--size",
        type=int,
        default=10,
        help="Box size for each module (default: 10)"
    )
    parser.add_argument(
        "--fill",
        default="black",
        help="Fill colour (default: black)"
    )
    parser.add_argument(
        "--bg",
        default="white",
        help="Background colour (default: white)"
    )
    return parser

def generate_qr(data, out, size, fill, bg):
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=size,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color=fill, back_color=bg)
    img.save(out)
    print(f"[OK] Saved QR code to {out}")

def main():
    parser = build_parser()
    args = parser.parse_args()

    generate_qr(
        data=args.data,
        out=args.out,
        size=args.size,
        fill=args.fill,
        bg=args.bg
    )

if __name__ == "__main__":
    main()
