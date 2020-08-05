#!/usr/bin/env bash
# Generate picture locally and upload to remote RPi

set -euo pipefail

DIR="$(cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd)"

pipenv run python "${DIR}/main.py" "${DIR}/output/local.bmp"

scp "${DIR}/output/local.bmp" pi:/home/pi
ssh pi "sudo /home/pi/eink/waveshare-IT8951/IT8951 0 0 /home/pi/local.bmp"
