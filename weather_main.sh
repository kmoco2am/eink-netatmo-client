#!/usr/bin/env bash

set -euo pipefail

DIR="$(cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd)"

cd ${DIR}

/usr/local/bin/pipenv run python ${DIR}/weather_main.py --driver=IT8951 main
