# E-ink Netatmo Client

Source links:
- aeriswather.com - sun and moon phases
- wdisseny.com/lluna - moon phases
- sunrise-sunset.org/api

Credits:
- https://erikflowers.github.io/weather-icons/
- https://github.com/joukos/PaperTTY
- https://github.com/philippelt/netatmo-api-python

## Development

```
pipenv --rm
pipenv --python 3.8
pipenv sync
```

## Python 3.8 on Raspberry Pi

```
sudo apt-get update
sudo apt-get install -y build-essential tk-dev libncurses5-dev libncursesw5-dev libreadline6-dev libdb5.3-dev \
    libgdbm-dev libsqlite3-dev libssl-dev libbz2-dev libexpat1-dev liblzma-dev zlib1g-dev libffi-dev

wget https://www.python.org/ftp/python/3.8.5/Python-3.8.5.tar.xz
tar xf Python-3.8.5.tar.xz
cd Python-3.8.5
./configure --prefix=/usr/local/opt/python-3.8.5 --enable-optimizations
make -j 4

# Install
sudo make altinstall
```

## Installation by Systemd

```
sudo cp weather_main.service /etc/systemd/system/weather_main.service
sudo systemctl start weather_main.service

sudo systemctl status weather_main.service

sudo systemctl stop weather_main.service

sudo systemctl enable weather_main.service
```

## Run it manually

```
sudo 

sudo \
    /usr/local/bin/pipenv run python \
    ./weather_main.py \ 
    --driver=IT8951 \
    bitmap \
    --file=/home/pi/workspace/waveshare-it8951/18.bmp
```
