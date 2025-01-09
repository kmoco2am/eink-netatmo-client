# E-ink Netatmo Client

Source links:
- aeriswather.com - sun and moon phases
- wdisseny.com/lluna - moon phases
- sunrise-sunset.org/api

Credits:
- https://erikflowers.github.io/weather-icons/
- https://github.com/joukos/PaperTTY
- https://github.com/philippelt/netatmo-api-python
- Official Waveshare examples and drivers: https://github.com/waveshareteam/e-Paper/

## Development

```bash
brew install python@3.9

pipenv --rm
pipenv --python 3.9
pipenv sync
```

### Generate Demo Pictures
```bash
pipenv run python ./weather_main.py --driver=IT8951 --debug demo
```

```bash
pipenv run python ./weather_main.py --driver=IT8951 --debug demo --modern
```


### Generate Real Picture
```bash
pipenv run python ./weather_main.py --driver=Bitmap --debug main
```

## Installation by Systemd

```bash
sudo cp weather_main.service /etc/systemd/system/weather_main.service
sudo systemctl start weather_main.service

sudo systemctl status weather_main.service

sudo systemctl stop weather_main.service

sudo systemctl enable weather_main.service

sudo systemctl restart weather_main.service
```

## Run it manually

```bash
sudo 

sudo \
    /usr/local/bin/pipenv run python \
    ./weather_main.py \ 
    --driver=IT8951 \
    bitmap \
    --file=/home/pi/workspace/waveshare-it8951/18.bmp
```

## Checking status

```bash
sudo journalctl -u weather_main.service -f -n 100
```

## Netatmo Credentials

Developer portal: https://dev.netatmo.com/

`~/.netatmo.credentials`:
```json
{
 "CLIENT_ID": "xxx",
 "CLIENT_SECRET": "xxx",
 "REFRESH_TOKEN": "xxx"
}
```

Regenerating refresh token may help to fix authentication issues (e.g. wrong grant).
