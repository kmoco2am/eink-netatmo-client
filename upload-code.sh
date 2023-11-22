#!/usr/bin/env bash
# Install code into remote RPi

set -euo pipefail

rsync -avz \
  --exclude '.git' \
  --exclude '.vscode' \
  --exclude '.idea' \
  --exclude 'image.bmp' \
  --exclude 'output' \
  --exclude '__pycache__' \
  --exclude 'bitmap_frame_*.py' \
  . pi:/home/pi/workspace/eink-py
