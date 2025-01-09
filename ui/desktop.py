import os

from datetime import datetime
from typing import Optional, Tuple

import pytz
from PIL import Image, ImageDraw, ImageFont, ImageChops

from model.open import WeatherGenericData
from model.weather import WeatherModel, WeatherInsideModel, WeatherOutsideModel, DEFAULT_NONE_TEMPERATURE
from ui.icon_mapping import IconMappingLookup
from ui.render_result import RenderResult
from widget.alignments import Alignments
from widget.panel import PanelWidget
from widget.text import TextWidget
from ui.weather_icon_lookup import WeatherIconLookup


def read_val(data: dict, section: str, value: str, default: str) -> str:
    if section in data:
        return sanitize_val(data[section], value, default)
    else:
        return default


def sanitize_val(d: dict, value_name: str, default_value: str) -> str:
    if value_name in d:
        return d[value_name]
    else:
        return default_value


def convert_float(orig_value: Optional[float], default_value: str = "") -> str:
    if orig_value is None:
        return default_value
    else:
        return "{0:.1f}".format(float(orig_value))

class Desktop:
    def __init__(self, resource_dir: str):
        default_font: str = os.path.join(resource_dir, 'RobotoCondensed-Regular.ttf')
        self.font_large = ImageFont.truetype(default_font, size=70)
        self.font_medium = ImageFont.truetype(default_font, size=40)
        self.font_small = ImageFont.truetype(default_font, size=20)
        self.font_huge = ImageFont.truetype(default_font, size=140)

        icons_font: str = os.path.join(resource_dir, 'weathericons-regular-webfont.ttf')
        self.font_weather_large = ImageFont.truetype(icons_font, size=47)
        self.font_weather_medium = ImageFont.truetype(icons_font, size=30)
        self.font_weather_small = ImageFont.truetype(icons_font, size=27)
        self.font_weather_huge = ImageFont.truetype(icons_font, size=140)

        # https://erikflowers.github.io/weather-icons/
        self.icon_lookup = WeatherIconLookup(
            os.path.join(resource_dir, 'weathericons.xml'))

        # https://gist.github.com/tbranyen/62d974681dea8ee0caa1
        self.icon_mapping = IconMappingLookup(os.path.join(resource_dir, 'icons-mapping.json'))

        # self.window = PanelWidget(800, 600)

    @staticmethod
    def band(bb: Tuple[int, int, int, int]) -> Tuple[int, int, int, int]:
        """Stretch a bounding box's X coordinates to be divisible by 8,
           otherwise weird artifacts occur as some bits are skipped."""
        return (int(bb[0] / 8) * 8, bb[1], int((bb[2] + 7) / 8) * 8, bb[3]) if bb else None

    @staticmethod
    def img_diff(img1: Image, img2: Image) -> Optional[Tuple[int, int, int, int]]:
        """Return the bounding box of differences between two images"""
        return ImageChops.difference(img1, img2).getbbox()


    def render_modern(self, data: Optional[WeatherModel], gen_data: Optional[WeatherGenericData]) -> RenderResult:
        image = Image.new('L', (800, 600), 255)
        draw = ImageDraw.Draw(image)
        result = RenderResult(image)

        # ------
        draw.line((20, 300, 780, 300), fill=0, width=3)
        # |
        draw.line((400, 20, 400, 290), fill=0, width=3)
        # |
        draw.line((400, 310, 400, 580), fill=0, width=3)

        main_panel: PanelWidget = PanelWidget(800,600)

        if data is None:
            pass
        else:
            indoor_panel: PanelWidget = self.render_indoor(data.inside)
            indoor_panel.left = 0
            indoor_panel.top = 0
            main_panel.add_child(indoor_panel)

            outdoor_panel: PanelWidget = self.render_outdoor(data.outside)
            outdoor_panel.left = 400
            outdoor_panel.top = 300
            main_panel.add_child(outdoor_panel)

        if gen_data:
            gen_data_panel: PanelWidget = self.render_generic_data(gen_data)
            gen_data_panel.left = 0
            gen_data_panel.top = 300
            main_panel.add_child(gen_data_panel)

        # time
        today: datetime = datetime.today()

        clock_text: TextWidget = TextWidget(400, 150, font=self.font_huge)
        clock_text.left = 400
        clock_text.top = 80
        clock_text.text = today.strftime("%k:%M")
        main_panel.add_child(clock_text)

        date_text: TextWidget = TextWidget(400, 50, font=self.font_medium)
        date_text.left = 400
        date_text.top = 40
        date_text.horizontal_alignment = Alignments.CENTER
        date_text.text = today.strftime("%-d %B %Y")
        main_panel.add_child(date_text)

        weekday_text: TextWidget = TextWidget(400, 50, font=self.font_medium)
        weekday_text.left = 400
        weekday_text.top = 220
        weekday_text.horizontal_alignment = Alignments.CENTER
        weekday_text.text = today.strftime("%A")
        main_panel.add_child(weekday_text)

        main_panel.is_children_draw_border(False)
        main_panel.draw(draw)

        result.add_bounding_box((0,0,400,300))
        result.add_bounding_box((0,300,400,600))
        result.add_bounding_box((400,0,800,300))
        result.add_bounding_box((400,300,800,600))

        return result

    def render_outdoor(self, outdoor_data: WeatherOutsideModel) -> PanelWidget:
        p: PanelWidget = PanelWidget(400, 300)

        temp_orig: float = outdoor_data.temperature
        temp_val: str = convert_float(temp_orig, DEFAULT_NONE_TEMPERATURE)

        temp_panel: PanelWidget = self.render_temp(temp_val)
        temp_panel.left = 80
        temp_panel.top = 100
        p.add_child(temp_panel)

        humidity_panel: PanelWidget = self.render_humidity(str(outdoor_data.humidity))
        humidity_panel.top = 40
        humidity_panel.left = 190
        p.add_child(humidity_panel)

        return p

    def render_indoor(self, indoor_data: WeatherInsideModel) -> PanelWidget:
        p: PanelWidget = PanelWidget(400, 300)

        temp_in: str = convert_float(indoor_data.temperature, DEFAULT_NONE_TEMPERATURE)

        temp_panel: PanelWidget = self.render_temp(temp_in)
        temp_panel.left = 80
        temp_panel.top = 100
        p.add_child(temp_panel)

        co2_panel: PanelWidget = self.render_co2(str(indoor_data.co2))
        co2_panel.top = temp_panel.top + temp_panel.height + 10
        co2_panel.left = 60
        p.add_child(co2_panel)

        humidity_panel: PanelWidget = self.render_humidity(str(indoor_data.humidity))
        humidity_panel.top = 40
        humidity_panel.left = 190
        p.add_child(humidity_panel)

        return p

    def render_humidity(self, value: str) -> PanelWidget:
        p: PanelWidget = PanelWidget(150, 40)

        t5: TextWidget = TextWidget(40,40, font=self.font_weather_medium)
        t5.text = self.icon_lookup.look_up_with_name('wi_humidity')
        t5.horizontal_alignment = Alignments.RIGHT
        t5.left = 0
        t5.top = 0
        p.add_child(t5)

        t4: TextWidget = TextWidget(90,40, font=self.font_medium)
        t4.horizontal_alignment = Alignments.RIGHT
        t4.text = "%s%%" % value
        t4.left = t5.left + t5.width
        t4.top = 0
        p.add_child(t4)


        return p

    def render_co2(self, value: str) -> PanelWidget:
        p: PanelWidget = PanelWidget(200, 40)

        t1: TextWidget = TextWidget(30,30, font=self.font_weather_medium)
        t1.text = self.icon_lookup.look_up_with_name('wi_barometer')
        t1.left = 0
        t1.top = 0
        p.add_child(t1)

        t2: TextWidget = TextWidget(100,30, font=self.font_medium)
        t2.horizontal_alignment = Alignments.RIGHT
        t2.text = value
        t2.left = t1.left + t1.width
        t2.top = 0
        p.add_child(t2)

        t3: TextWidget = TextWidget(50,30, font=self.font_small)
        t3.horizontal_alignment = Alignments.LEFT
        t3.vertical_alignment = Alignments.BOTTOM
        t3.text = "ppm"
        t3.left = t2.left + t2.width + 5
        t3.top = 0
        p.add_child(t3)
        return p

    def render_generic_data(self, gen_data):
        p: PanelWidget = PanelWidget(400, 300)

        today: datetime = datetime.today()
        is_day: bool = gen_data.sunrise.astimezone(pytz.utc) < today.astimezone(pytz.utc) < gen_data.sunset.astimezone(pytz.utc)
        icon: str = self.icon_mapping.lookup_icon(gen_data.weather_code, is_day)

        m: TextWidget = TextWidget(240,240, self.font_weather_huge)
        m.left = 10
        m.top = 50
        m.horizontal_alignment = Alignments.CENTER
        m.vertical_alignment = Alignments.CENTER
        m.text = self.icon_lookup.look_up_with_name(icon)
        p.add_child(m)

        f1_icon: str = self.icon_mapping.lookup_icon(gen_data.forecast_code_1, is_day)
        f1: TextWidget = TextWidget(70,70, self.font_weather_large)
        f1.left = 120
        f1.top = 20
        f1.horizontal_alignment = Alignments.CENTER
        f1.vertical_alignment = Alignments.CENTER
        f1.text = self.icon_lookup.look_up_with_name(f1_icon)
        p.add_child(f1)

        f2_icon: str = self.icon_mapping.lookup_icon(gen_data.forecast_code_2, is_day)
        f2: TextWidget = TextWidget(70,70, self.font_weather_large)
        f2.left = 190
        f2.top = 20
        f2.horizontal_alignment = Alignments.CENTER
        f2.vertical_alignment = Alignments.CENTER
        f2.text = self.icon_lookup.look_up_with_name(f2_icon)
        p.add_child(f2)

        f3_icon: str = self.icon_mapping.lookup_icon(gen_data.forecast_code_3, is_day)
        f3: TextWidget = TextWidget(70,70, self.font_weather_large)
        f3.left = 260
        f3.top = 20
        f3.horizontal_alignment = Alignments.CENTER
        f3.vertical_alignment = Alignments.CENTER
        f3.text = self.icon_lookup.look_up_with_name(f3_icon)
        p.add_child(f3)

        return p

    def render_temp(self, value: str) -> PanelWidget:
        p: PanelWidget = PanelWidget(280, 130)

        split = value.split(".")
        degree_val = split[0]
        subdegree_val = split[1]

        m: TextWidget = TextWidget(50,80, self.font_weather_large)
        m.left = 0
        m.top = 0
        m.horizontal_alignment = Alignments.LEFT
        m.vertical_alignment = Alignments.TOP
        m.text = self.icon_lookup.look_up_with_name('wi_thermometer')
        p.add_child(m)

        temp2: TextWidget = TextWidget(90,70, font=self.font_large)
        temp2.left = 190
        temp2.top = 5
        temp2.horizontal_alignment = Alignments.LEFT
        temp2.vertical_alignment = Alignments.TOP
        temp2.text = "." + subdegree_val
        p.add_child(temp2)

        temp_text: TextWidget = TextWidget(190, 120, font=self.font_huge)
        temp_text.left = 0
        temp_text.top = 5
        temp_text.horizontal_alignment = Alignments.RIGHT
        temp_text.vertical_alignment = Alignments.TOP
        temp_text.text = degree_val
        p.add_child(temp_text)

        degree_char: TextWidget = TextWidget(90, 40, font=self.font_weather_large)
        degree_char.left = 190
        degree_char.top = 70
        degree_char.horizontal_alignment = Alignments.LEFT
        degree_char.vertical_alignment = Alignments.BOTTOM
        degree_char.text = self.icon_lookup.look_up_with_name('wi_celsius')

        p.add_child(degree_char)
        return p


    def render(self, data: Optional[WeatherModel]) -> RenderResult:
        # image = Image.new('L', (self.window.height, self.window.width), 255)
        image = Image.new('L', (800, 600), 255)
        draw = ImageDraw.Draw(image)
        result = RenderResult(image)
        if data is None:
            self.render_warning(draw)
            result.add_bounding_box((0,0,800,600))
        else:
            self.old_render(draw, data)
            # bb for date and time
            result.add_bounding_box((0,0,800,200))
            # bb for indoor
            result.add_bounding_box((0,200,400,400))
            # bb for outdoor
            result.add_bounding_box((400,200,800,400))
            # bb for the rest
            result.add_bounding_box((0,400,800,600))

        self.render_time(draw)

        return result

    def render_warning(self, draw) -> None:
        draw.text((50, 250), "No data available!", font=self.font_large, fill=0)

    def render_time(self, draw) -> None:
        today = datetime.today()
        today_date_str = today.strftime("%A, %d %B %Y")
        draw.text((50, 20), today_date_str, font=self.font_medium, fill=0)
        today_time_str = today.strftime("%H:%M")
        draw.text((550, 50), today_time_str, font=self.font_large, fill=0)

    def old_render(self, draw, data: WeatherModel) -> None:
        temp_out_orig: float = data.outside.temperature
        temp_in_orig: float = data.inside.temperature

        tempOut: str = convert_float(temp_out_orig, DEFAULT_NONE_TEMPERATURE)
        temp_in: str = convert_float(temp_in_orig, DEFAULT_NONE_TEMPERATURE)

        humidity_out: str = str(data.outside.humidity)
        humidity_in: str = str(data.inside.humidity)

        co2_in: str = str(data.inside.co2)

        draw.line((20, 200, 780, 200), fill=0, width=3)
        draw.line((400, 210, 400, 390), fill=0, width=3)
        draw.line((20, 400, 780, 400), fill=0, width=3)
        draw.line((400, 410, 400, 580), fill=0, width=3)
        draw.line((200, 410, 200, 580), fill=0, width=3)
        draw.line((600, 410, 600, 580), fill=0, width=3)

        draw.text((100, 150), self.icon_lookup.look_up_with_name('wi_sunrise'), font=self.font_weather_medium, fill=0)
        draw.text((350, 150), self.icon_lookup.look_up_with_name('wi_sunset'), font=self.font_weather_medium, fill=0)

        # indoor
        draw.text((100, 240), self.icon_lookup.look_up_with_name('wi_thermometer'), font=self.font_weather_large,
                  fill=0)
        draw.text((150, 230), temp_in, font=self.font_large, fill=0)
        draw.text((320, 230), self.icon_lookup.look_up_with_name('wi_celsius'), font=self.font_weather_large, fill=0)

        draw.text((120, 310), self.icon_lookup.look_up_with_name('wi_humidity'), font=self.font_weather_medium, fill=0)
        draw.text((150, 312), "%s%%" % humidity_in, font=self.font_medium, fill=0)

        draw.text((230, 310), self.icon_lookup.look_up_with_name('wi_barometer'), font=self.font_weather_medium, fill=0)
        draw.text((260, 312), "%s" % co2_in, font=self.font_medium, fill=0)
        draw.text((330, 314), "ppm", font=self.font_small, fill=0)

        # outdoor
        draw.text((460, 240), self.icon_lookup.look_up_with_name('wi_thermometer'), font=self.font_weather_large,
                  fill=0)
        draw.text((510, 230), tempOut, font=self.font_large, fill=0)
        draw.text((680, 230), self.icon_lookup.look_up_with_name('wi_celsius'), font=self.font_weather_large, fill=0)

        draw.text((480, 310), self.icon_lookup.look_up_with_name('wi_humidity'), font=self.font_weather_medium, fill=0)
        draw.text((510, 312), "%s%%" % humidity_out, font=self.font_medium, fill=0)
