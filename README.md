# Python QR Generator Tool

A tiny, fast, single-file QR code generator CLI written in Python.
Create QR codes for URLs, Wi-Fi credentials, contact info, or plain text in seconds.

## Installation

```bash
git clone git@github-dorian:dorian-sotpyrc/python-qr-generator-tool.git
cd python-qr-generator-tool
pip install -r requirements.txt
````

## Usage

Generate a default QR code:

```bash
python src/qrtool.py "https://plexdata.online"
```

Custom output filename:

```bash
python src/qrtool.py "Hello world" --out hello.png
```

Custom colours:

```bash
python src/qrtool.py "WiFi:MyNetwork" --fill "#EC793F" --bg "white"
```

Adjust QR module size:

```bash
python src/qrtool.py "Some text" --size 14
```

## How it works

Input text → QRCode object → PIL image → PNG file.

The script uses:

* qrcode.QRCode for generation
* Medium error correction (ERROR_CORRECT_M)
* A configurable box size and colour scheme.

## Ideas to extend

* Add logo overlay
* Generate SVG output
* Batch-generate QR codes from a CSV file
  RDEOF

echo "Created $REPO_DIR with src/qrtool.py, requirements.txt, and README.md"
