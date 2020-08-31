import os

from datetime import datetime

from PIL import Image, ImageDraw, ImageFont

from widget.panel import PanelWidget
from widget.weather_icon_lookup import WeatherIconLookup


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


class Desktop:
    def __init__(self, resource_dir: str):
        self.font_large = ImageFont.truetype(
            os.path.join(resource_dir, 'Inconsolata-Regular.ttf'), size=74)
        self.font_medium = ImageFont.truetype(
            os.path.join(resource_dir, 'Inconsolata-Regular.ttf'), size=34)
        self.font_small = ImageFont.truetype(
            os.path.join(resource_dir, 'Inconsolata-Regular.ttf'), size=20)
        self.font_weather_large = ImageFont.truetype(
            os.path.join(resource_dir, 'weathericons-regular-webfont.ttf'),
            size=47)
        self.font_weather_medium = ImageFont.truetype(
            os.path.join(resource_dir, 'weathericons-regular-webfont.ttf'),
            size=30)
        self.font_weather_small = ImageFont.truetype(
            os.path.join(resource_dir, 'weathericons-regular-webfont.ttf'),
            size=27)

        # https://erikflowers.github.io/weather-icons/
        self.icon_lookup = WeatherIconLookup(
            os.path.join(resource_dir, 'weathericons.xml'))

        #self.window = PanelWidget(800, 600)

    def render(self, data: dict):
        # image = Image.new('L', (self.window.height, self.window.width), 255)
        image = Image.new('L', (800, 600), 255)
        draw = ImageDraw.Draw(image)
        # self.window.draw(draw)
        self.old_render(draw, data)
        return image

    def old_render(self, draw, data: dict):
        temp_out_orig: str = read_val(data, 'Outdoor', 'Temperature', '--.-')
        temp_in_orig: str = read_val(data, 'Indoor', 'Temperature', '--.-')

        tempOut: str = convert_float(temp_out_orig)
        temp_in: str = convert_float(temp_in_orig)

        humidity_out: str = read_val(data, 'Outdoor', 'Humidity', '--')
        humidity_in: str = read_val(data, 'Indoor', 'Humidity', '--')

        co2_in: str = read_val(data, 'Indoor', 'CO2', '---')

        draw.line((20, 200, 780, 200), fill=0, width=3)
        draw.line((400, 210, 400, 390), fill=0, width=3)
        draw.line((20, 400, 780, 400), fill=0, width=3)
        draw.line((400, 410, 400, 580), fill=0, width=3)
        draw.line((200, 410, 200, 580), fill=0, width=3)
        draw.line((600, 410, 600, 580), fill=0, width=3)

        today = datetime.today()
        today_date_str = today.strftime("%A, %d %B %Y")
        draw.text((50, 20), today_date_str, font=self.font_medium, fill=0)
        today_time_str = today.strftime("%H:%M")
        draw.text((550, 50), today_time_str, font=self.font_large, fill=0)

        draw.text((100, 150), self.icon_lookup.look_up_with_name('wi_sunrise'), font=self.font_weather_medium, fill=0)
        draw.text((350, 150), self.icon_lookup.look_up_with_name('wi_sunset'), font=self.font_weather_medium, fill=0)

        # indoor
        draw.text((100, 240), self.icon_lookup.look_up_with_name('wi_thermometer'), font=self.font_weather_large, fill=0)
        draw.text((150, 230), temp_in, font=self.font_large, fill=0)
        draw.text((320, 230), self.icon_lookup.look_up_with_name('wi_celsius'), font=self.font_weather_large, fill=0)

        draw.text((120, 310), self.icon_lookup.look_up_with_name('wi_humidity'), font=self.font_weather_medium, fill=0)
        draw.text((150, 312), "%s%%" % humidity_in, font=self.font_medium, fill=0)

        draw.text((230, 310), self.icon_lookup.look_up_with_name('wi_barometer'), font=self.font_weather_medium, fill=0)
        draw.text((260, 312), "%s" % co2_in, font=self.font_medium, fill=0)
        draw.text((330, 314), "ppm", font=self.font_small, fill=0)

        # outdoor
        draw.text((460, 240), self.icon_lookup.look_up_with_name('wi_thermometer'), font=self.font_weather_large, fill=0)
        draw.text((510, 230), tempOut, font=self.font_large, fill=0)
        draw.text((680, 230), self.icon_lookup.look_up_with_name('wi_celsius'), font=self.font_weather_large, fill=0)

        draw.text((480, 310), self.icon_lookup.look_up_with_name('wi_humidity'), font=self.font_weather_medium, fill=0)
        draw.text((510, 312), "%s%%" % humidity_out, font=self.font_medium, fill=0)


    def show_widget_border(self, show_border: bool):
        self.window.is_draw_border(show_border)
        self.window.is_children_draw_border(show_border)
