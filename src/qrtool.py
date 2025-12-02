#!/usr/bin/env python3
"""
qrtool.py — A tiny command-line QR code generator.

Examples:
    # Simple URL (auto mode)
    python src/qrtool.py "https://plexdata.online"

    # Phone number with tel: scheme
    python src/qrtool.py "+61412345678" --mode tel --out phone.png

    # Email address
    python src/qrtool.py "you@example.com" --mode email --out email.png

    # URL with a centre logo
    python src/qrtool.py "plexdata.online" --mode url --logo static/logo.png --out plex.png
"""

import argparse
from pathlib import Path

import qrcode
from PIL import Image


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate QR codes in seconds (with optional centre logo)."
    )
    parser.add_argument(
        "data",
        help="The text, URL, phone number, or email to encode."
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
    parser.add_argument(
        "--mode",
        choices=["auto", "url", "tel", "email", "sms"],
        default="auto",
        help=(
            "How to interpret the data: "
            "auto (as-is), url, tel, email, sms. Default: auto."
        ),
    )
    parser.add_argument(
        "--logo",
        help="Optional path to a logo image to overlay in the centre of the QR."
    )
    return parser


def prepare_data(raw: str, mode: str) -> str:
    raw = raw.strip()
    if mode == "url":
        if not raw.startswith(("http://", "https://")):
            return "https://" + raw
        return raw
    if mode == "tel":
        return f"tel:{raw}"
    if mode == "email":
        return f"mailto:{raw}"
    if mode == "sms":
        return f"sms:{raw}"
    # auto
    return raw


def overlay_logo(qr_image: Image.Image, logo_path: Path) -> Image.Image:
    """
    Overlay a logo at the centre of the QR code.

    The logo is scaled to at most ~25% of the QR width to keep it scannable.
    """
    if not logo_path.is_file():
        print(f"[WARN] Logo path does not exist: {logo_path}")
        return qr_image

    logo = Image.open(logo_path).convert("RGBA")
    qr_image = qr_image.convert("RGBA")

    qr_w, qr_h = qr_image.size
    max_logo_width = int(qr_w * 0.25)
    max_logo_height = int(qr_h * 0.25)
    logo.thumbnail((max_logo_width, max_logo_height), Image.LANCZOS)

    logo_w, logo_h = logo.size
    pos = ((qr_w - logo_w) // 2, (qr_h - logo_h) // 2)

    qr_image.paste(logo, pos, mask=logo)
    return qr_image


def generate_qr(data: str,
                out: str,
                size: int,
                fill: str,
                bg: str,
                mode: str,
                logo: str | None) -> None:
    encoded = prepare_data(data, mode)

    # Use higher error correction when we have a logo in the middle
    error_level = (
        qrcode.constants.ERROR_CORRECT_H if logo else qrcode.constants.ERROR_CORRECT_M
    )

    qr = qrcode.QRCode(
        version=None,
        error_correction=error_level,
        box_size=size,
        border=4,
    )
    qr.add_data(encoded)
    qr.make(fit=True)

    img = qr.make_image(fill_color=fill, back_color=bg)

    if logo:
        img = overlay_logo(img, Path(logo))

    img.save(out)
    print(f"[OK] Saved QR code to {out}")


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    generate_qr(
        data=args.data,
        out=args.out,
        size=args.size,
        fill=args.fill,
        bg=args.bg,
        mode=args.mode,
        logo=args.logo,
    )


if __name__ == "__main__":
    main()
