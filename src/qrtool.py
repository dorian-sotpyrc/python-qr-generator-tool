#!/usr/bin/env python3
"""
qrtool.py — A tiny command-line QR code generator.

Examples:
    # Simple URL (auto mode)
    python src/qrtool.py "https://plexdata.online"

    # URL with centre logo and auto-styled PLEX colours
    python src/qrtool.py "plexdata.online" --mode url --logo examples/plex_logo.png --auto-style --out plex_styled.png

    # Phone number with tel: scheme
    python src/qrtool.py "+61412345678" --mode tel --out phone.png

    # Email address
    python src/qrtool.py "you@example.com" --mode email --out email.png
"""

import argparse
from pathlib import Path
from typing import Tuple

import qrcode
from PIL import Image, ImageDraw


# PLEX palette (subset needed for auto styling)
PLEX_PALETTE = {
    "lavender": (0xE3, 0xE3, 0xED),
    "atomic_tangerine": (0xEC, 0x79, 0x3F),
    "sandy_brown": (0xF2, 0xA0, 0x66),
    "sunlit_clay": (0xEA, 0xB4, 0x67),
    "soft_periwinkle": (0xA6, 0x90, 0xF9),
    "bright_lavender": (0xBA, 0x80, 0xE2),
    "deep_lilac": (0x6F, 0x45, 0xBC),
    "bg_main": (0xF4, 0xF4, 0xFB),
    "bg_elevated": (0xF8, 0xF7, 0xFF),
}


def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    return "#{:02X}{:02X}{:02X}".format(*rgb)


def nearest_palette_colour(rgb: Tuple[int, int, int]) -> Tuple[str, Tuple[int, int, int]]:
    """Return (name, rgb) of the closest PLEX palette colour to the given rgb."""
    r, g, b = rgb
    best_name = "deep_lilac"
    best_rgb = PLEX_PALETTE[best_name]
    best_dist = float("inf")

    for name, (pr, pg, pb) in PLEX_PALETTE.items():
        if name.startswith("bg_"):
            # skip backgrounds as primary fill candidates
            continue
        dr = r - pr
        dg = g - pg
        db = b - pb
        dist = dr * dr + dg * dg + db * db
        if dist < best_dist:
            best_dist = dist
            best_name = name
            best_rgb = (pr, pg, pb)

    return best_name, best_rgb


def infer_qr_colours_from_logo(logo_path: Path) -> Tuple[str, str]:
    """
    Infer (fill_hex, bg_hex) from the logo:
    - average logo colour snapped to nearest PLEX palette for fill
    - PLEX bg-main for background
    """
    try:
        img = Image.open(logo_path).convert("RGBA")
    except Exception as exc:  # noqa: BLE001
        print(f"[WARN] Could not open logo for colour inference: {exc}")
        # Fallback to classic black/white
        return "#000000", "#FFFFFF"

    # Downscale to keep things cheap and smooth
    img = img.resize((64, 64), Image.LANCZOS)
    pixels = img.getdata()

    total_r = total_g = total_b = count = 0
    for r, g, b, a in pixels:
        if a < 32:
            continue  # skip near-transparent
        # skip very bright whites
        if r > 245 and g > 245 and b > 245:
            continue
        total_r += r
        total_g += g
        total_b += b
        count += 1

    if count == 0:
        # If logo is basically all white/transparent, pick a nice default
        fill_rgb = PLEX_PALETTE["deep_lilac"]
    else:
        avg_rgb = (total_r // count, total_g // count, total_b // count)
        _, fill_rgb = nearest_palette_colour(avg_rgb)

    fill_hex = rgb_to_hex(fill_rgb)
    bg_rgb = PLEX_PALETTE["bg_main"]
    bg_hex = rgb_to_hex(bg_rgb)
    return fill_hex, bg_hex


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate QR codes in seconds (with optional centre logo and PLEX-style auto colours)."
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
        default=None,
        help="Fill colour (hex or name). When --auto-style is set, this is ignored."
    )
    parser.add_argument(
        "--bg",
        default=None,
        help="Background colour (hex or name). When --auto-style is set, this is ignored."
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
        help="Optional path to a logo image to overlay in a neat central container."
    )
    parser.add_argument(
        "--no-frame",
        action="store_true",
        help="Disable the rounded outer frame (classic QR look)."
    )
    parser.add_argument(
        "--auto-style",
        action="store_true",
        help="Infer QR colours from the logo using the PLEX palette (overrides --fill and --bg)."
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


def overlay_logo_with_container(qr_image: Image.Image, logo_path: Path) -> Image.Image:
    """
    Overlay a logo in a rounded white container at the centre of the QR.

    The container is about ~26% of the QR width with a slim border,
    so the logo feels tightly integrated.
    """
    if not logo_path.is_file():
        print(f"[WARN] Logo path does not exist: {logo_path}")
        return qr_image

    qr_image = qr_image.convert("RGBA")
    qr_w, qr_h = qr_image.size

    # Central rounded container, slightly smaller to reduce white moat
    container_size = int(qr_w * 0.26)
    container = Image.new("RGBA", (container_size, container_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(container)
    radius = int(container_size * 0.16)
    draw.rounded_rectangle(
        (0, 0, container_size, container_size),
        radius=radius,
        fill=(255, 255, 255, 255),
    )

    c_x = (qr_w - container_size) // 2
    c_y = (qr_h - container_size) // 2
    qr_image.alpha_composite(container, (c_x, c_y))

    # Logo inside container with very small margin (tight look)
    logo = Image.open(logo_path).convert("RGBA")

    margin = int(container_size * 0.06)  # smaller margin → minimal white gap
    max_logo_w = container_size - 2 * margin
    max_logo_h = container_size - 2 * margin
    logo.thumbnail((max_logo_w, max_logo_h), Image.LANCZOS)

    logo_w, logo_h = logo.size
    l_x = c_x + (container_size - logo_w) // 2
    l_y = c_y + (container_size - logo_h) // 2

    qr_image.alpha_composite(logo, (l_x, l_y))
    return qr_image


def add_modern_frame(qr_image: Image.Image, bg: str) -> Image.Image:
    """
    Place the QR on a slightly larger canvas with rounded corners
    to give it a modern, 'card-like' appearance with tight padding.
    """
    qr_image = qr_image.convert("RGBA")
    qr_w, qr_h = qr_image.size

    # Tighter outer whitespace
    padding = int(qr_w * 0.03)
    frame_w = qr_w + 2 * padding
    frame_h = qr_h + 2 * padding

    canvas = Image.new("RGBA", (frame_w, frame_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)

    radius = int(min(frame_w, frame_h) * 0.1)
    draw.rounded_rectangle(
        (0, 0, frame_w, frame_h),
        radius=radius,
        fill=bg,
    )

    canvas.alpha_composite(qr_image, (padding, padding))
    return canvas


def generate_qr(data: str,
                out: str,
                size: int,
                fill: str | None,
                bg: str | None,
                mode: str,
                logo: str | None,
                no_frame: bool,
                auto_style: bool) -> None:
    encoded = prepare_data(data, mode)

    logo_path = Path(logo) if logo else None

    if auto_style and logo_path is not None:
        fill, bg = infer_qr_colours_from_logo(logo_path)
        print(f"[INFO] Auto-styled colours: fill={fill}, bg={bg}")
    else:
        if fill is None:
            fill = "black"
        if bg is None:
            bg = "white"

    # Higher error correction when we have a logo in the middle
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

    img = qr.make_image(fill_color=fill, back_color=bg).convert("RGBA")

    if logo_path is not None:
        img = overlay_logo_with_container(img, logo_path)

    if not no_frame:
        img = add_modern_frame(img, bg=bg)

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
        no_frame=args.no_frame,
        auto_style=args.auto_style,
    )


if __name__ == "__main__":
    main()
