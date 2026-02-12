#!/usr/bin/env bash
# Quick start script per Linux/Mac (reference)
# Per Windows, usare build_exe.ps1 o build_exe.bat

set -e

echo "=== EthoRenamer Quick Start ==="

# 1. Create venv
python3 -m venv .venv
source .venv/bin/activate

# 2. Install
pip install -U pip
pip install -r requirements.txt

echo ""
echo "✓ Setup complete!"
echo ""
echo "Run: python app.py"
echo ""
echo "Note: Ensure ffmpeg/ffprobe is in PATH"
echo "      or copy ffprobe to ./bin/"
