# E-ink Netatmo Client

Source links:
- aeriswather.com - sun and moon phases
- wdisseny.com/lluna - moon phases
- sunrise-sunset.org/api

Credits:
- https://erikflowers.github.io/weather-icons/
- https://github.com/joukos/PaperTTY

## Development

```
pipenv --rm
pipenv --python 3.8
pipenv sync
```

## Installation

```
sudo pip3 install pipenv
```

```
* * * * * /bin/bash -c /home/pi/workspace/eink-py/run.sh
# * * * * * /bin/bash -c /home/pi/workspace/eink-py/run.sh >>/home/pi/workspace/eink-py/cron.log 2>&1
```

## Python 3.8 on Raspberry Pi

```
sudo apt-get update
sudo apt-get install -y build-essential tk-dev libncurses5-dev libncursesw5-dev libreadline6-dev libdb5.3-dev \
    libgdbm-dev libsqlite3-dev libssl-dev libbz2-dev libexpat1-dev liblzma-dev zlib1g-dev libffi-dev

wget https://www.python.org/ftp/python/3.8.5/Python-3.8.5.tar.xz
tar xf Python-3.8.5.tar.xz
cd Python-3.8.5
./configure --prefix=/usr/local/opt/python-3.8.5
make -j 4

# Install
sudo make altinstall

# Change default
sudo update-alternatives --config python

```
