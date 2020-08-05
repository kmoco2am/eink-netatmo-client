#!/usr/bin/env bash
# Main script to run on RPi

set -euo pipefail

DIR="$(cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd)"

echo $(date)

cd ${DIR}

/usr/local/bin/pipenv run python ${DIR}/main.py ${DIR}/output/output.bmp

sudo /home/pi/eink/waveshare-IT8951/IT8951 0 0 ${DIR}/output/output.bmp

