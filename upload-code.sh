#!/usr/bin/env bash
# Install code into remote RPi

set -euo pipefail

rsync -avz \
  --exclude '.git' \
  --exclude '.vscode' \
  --exclude '.idea' \
  --exclude 'image.bmp' \
  --exclude 'output' \
  . pi:/home/pi/workspace/eink-py
