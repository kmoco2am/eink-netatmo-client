#!/usr/bin/python
# -*- coding:utf-8 -*-

import os
import sys

import netatmo_client
from PIL import Image, ImageDraw, ImageFont

from datetime import datetime

from widget.weather_icon_lookup import WeatherIconLookup

project_dir = os.path.dirname(os.path.realpath(__file__))

# Access to the sensors
auth = netatmo_client.ClientAuth()
dev = netatmo_client.WeatherStationData(auth)

lastData: dict = dev.lastData()


def read_val(data: dict, section: str, value: str, default: str) -> str:
    if section in data:
        if value in data[section]:
            return data[section][value]
        else:
            return default
    else:
        return default


def convert_float(orig_value: str) -> str:
    try:
        return "{0:.1f}".format(float(orig_value))
    except:
        return orig_value


data_indoor: dict = dev.lastData()['Indoor']

tempOutOrig: str = read_val(lastData, 'Outdoor', 'Temperature', '--.-')
tempInOrig: str = read_val(lastData, 'Indoor', 'Temperature', '--.-')

tempOut: str = convert_float(tempOutOrig)
tempIn: str = convert_float(tempInOrig)

humidityOut: str = read_val(lastData, 'Outdoor', 'Humidity', '--')
humidityIn: str = read_val(lastData, 'Indoor', 'Humidity', '--')


co2In: str = read_val(lastData, 'Indoor', 'CO2', '---')

print("Drawing")
# Drawing on the Horizontal image
Himage = Image.new('L', (800, 600), 255)  # 255: clear the frame
draw = ImageDraw.Draw(Himage)


def get_font(size: int):
    return ImageFont.truetype(os.path.join(project_dir, "resources", 'Inconsolata-Regular.ttf'), size=size)

font_small = get_font(20)
font_medium = get_font(34)
font_large = get_font(74)

font_weather_large = ImageFont.truetype(
    os.path.join(project_dir, 'resources', 'weathericons-regular-webfont.ttf'),
    size=47)
font_weather_medium = ImageFont.truetype(
    os.path.join(project_dir, 'resources', 'weathericons-regular-webfont.ttf'),
    size=30)

draw.line((20, 200, 780, 200), fill=0, width=3)

draw.line((400, 210, 400, 390), fill=0, width=3)

draw.line((20, 400, 780, 400), fill=0, width=3)

draw.line((400, 410, 400, 580), fill=0, width=3)
draw.line((200, 410, 200, 580), fill=0, width=3)
draw.line((600, 410, 600, 580), fill=0, width=3)

today = datetime.today()
today_date_str = today.strftime("%A, %d %B %Y")
draw.text((50, 20), today_date_str, font=font_medium, fill=0)
today_time_str = today.strftime("%H:%M")
draw.text((550, 50), today_time_str, font=font_large, fill=0)

# https://erikflowers.github.io/weather-icons/
icon_lookup = WeatherIconLookup(os.path.join(project_dir, 'resources', 'weathericons.xml'))

draw.text((100, 150), icon_lookup.look_up_with_name('wi_sunrise'), font=font_weather_medium, fill=0)
draw.text((350, 150), icon_lookup.look_up_with_name('wi_sunset'), font=font_weather_medium, fill=0)

# indoor

draw.text((100, 240), icon_lookup.look_up_with_name('wi_thermometer'), font=font_weather_large, fill=0)
draw.text((150, 230), tempIn, font=font_large, fill=0)
draw.text((320, 230), icon_lookup.look_up_with_name('wi_celsius'), font=font_weather_large, fill=0)

draw.text((120, 310), icon_lookup.look_up_with_name('wi_humidity'), font=font_weather_medium, fill=0)
draw.text((150, 312), "%s%%" % humidityIn, font=font_medium, fill=0)

draw.text((230, 310), icon_lookup.look_up_with_name('wi_barometer'), font=font_weather_medium, fill=0)
draw.text((260, 312), "%s" % co2In, font=font_medium, fill=0)
draw.text((330, 314), "ppm", font=font_small, fill=0)

# outdoor

draw.text((460, 240), icon_lookup.look_up_with_name('wi_thermometer'), font=font_weather_large, fill=0)
draw.text((510, 230), tempOut, font=font_large, fill=0)
draw.text((680, 230), icon_lookup.look_up_with_name('wi_celsius'), font=font_weather_large, fill=0)

draw.text((480, 310), icon_lookup.look_up_with_name('wi_humidity'), font=font_weather_medium, fill=0)
draw.text((510, 312), "%s%%" % humidityOut, font=font_medium, fill=0)

output_filename = sys.argv[1]

print("Saving into: {0:s}".format(output_filename))
Himage.save(output_filename)
