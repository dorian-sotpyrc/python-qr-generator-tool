
# Python QR Generator Tool

A tiny, fast, single-file QR code generator written in Python.

This repository is the **reference implementation** used in the PLEX article:

👉 **Building a custom QR generator tool with Python in less than 5 minutes**  
https://plexdata.online/?utm_source=github&utm_medium=repo&utm_campaign=python-qr-generator-tool#tool-qr  

The article walks you through **building the tool from scratch**, explaining every step of the implementation.  
If you want a ready-to-use module instead of writing the whole thing yourself, this repo contains the exact version demonstrated.

---

## ⚡ Want a QR code instantly?

Use the live PLEX QR Generator tool here:

👉 **https://plexdata.online/?utm_source=github&utm_medium=repo&utm_campaign=python-qr-generator-tool#tool-qr**

No install, no Python — just paste your URL or text and download a PNG.

---

## 🚀 Quick Start (Python CLI)

```bash
git clone git@github-dorian:dorian-sotpyrc/python-qr-generator-tool.git
cd python-qr-generator-tool
pip install -r requirements.txt
````

Generate your first QR code:

```bash
python src/qrtool.py "https://plexdata.online"
```

---

## ✨ Features

* **Single-file CLI** (`src/qrtool.py`)
* **Multiple data modes:** URL, phone, email, SMS, raw text
* **Modern rounded frame**
* **Centre logo support with a clean rounded container** (`--logo`)
* **PLEX-style auto colour extraction** (`--auto-style`)
* **Manual colour control** (`--fill`, `--bg`)
* **Adjustable QR module size** (`--size`)
* **High error correction when embedding a logo**

---

## 🧪 Usage Examples

### PLEX-styled QR with centre logo

```bash
python src/qrtool.py "plexdata.online" \
  --mode url \
  --logo examples/plex_logo.png \
  --auto-style \
  --out plex_qr.png
```

### Phone, email & SMS

```bash
python src/qrtool.py "+61412345678" --mode tel --out phone.png
python src/qrtool.py "you@example.com" --mode email --out email.png
python src/qrtool.py "+61412345678" --mode sms --out sms.png
```

### Custom colours

```bash
python src/qrtool.py "Hello" --fill "#EC793F" --bg "#F8F7FF"
```

### Disable modern frame

```bash
python src/qrtool.py "plexdata.online" --no-frame --out bare.png
```

---

## 🌈 Auto-Style Colours (PLEX Palette)

When `--auto-style` is used:

1. The logo is scanned
2. A dominant colour is extracted
3. The colour is snapped to the nearest shade in the official **PLEX palette**, including:

   * deep lilac
   * soft periwinkle
   * bright lavender
   * atomic tangerine
   * sandy brown
4. The QR modules adopt that colour
5. A subtle PLEX-style background and rounded frame are applied

This produces **designer-level QR codes** with zero manual tweaking.

---

## 🧱 How the Tool Works

Pipeline:

1. Input text
2. Normalisation (`https://`, `mailto:`, `tel:`, etc.)
3. QR code matrix generation
4. PIL rendering
5. Optional:

   * Logo container overlay
   * PLEX colour inference
   * Rounded outer frame
6. Output to PNG

---

## 🌐 Online version (no install needed)

If you prefer a simple UI instead of the Python CLI:

👉 **[Open the online QR generator](https://plexdata.online/?utm_source=github&utm_medium=repo&utm_campaign=python-qr-generator-tool-footer#tool-qr)**

* Upload a logo
* Paste a URL, phone, or email
* Download a styled PNG instantly
* Uses the same algorithms as this repo

---

## 📦 Project Structure

```
python-qr-generator-tool/
├── src/
│   └── qrtool.py
├── examples/
│   └── plex_logo.png
├── requirements.txt
└── README.md
```

---

## 🛠 Ideas to Extend

* SVG output
* Batch generator from CSV
* Poster sheet QR generator
* Brand presets / themes
* REST API wrapper

---

## 📄 License

MIT License — free to use, modify, embed, or integrate into your own automation workflows.

