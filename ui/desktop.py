import os

from datetime import datetime
from typing import Optional, Tuple

from PIL import Image, ImageDraw, ImageFont, ImageChops

from model.weather import WeatherModel, WeatherInsideModel, WeatherOutsideModel
from ui.render_result import RenderResult
from widget.alignments import Alignments
from widget.panel import PanelWidget
from widget.text import TextWidget
from widget.weather_icon_lookup import WeatherIconLookup


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


def convert_float(orig_value: str) -> str:
    try:
        return "{0:.1f}".format(float(orig_value))
    except:
        return orig_value


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

        # https://erikflowers.github.io/weather-icons/
        self.icon_lookup = WeatherIconLookup(
            os.path.join(resource_dir, 'weathericons.xml'))

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


    def render_modern(self, data: Optional[WeatherModel]) -> RenderResult:
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
            humidity_out: str = data.outside.humidity

            indoor_panel: PanelWidget = self.render_indoor(data.inside)
            indoor_panel.left = 0
            indoor_panel.top = 0
            main_panel.add_child(indoor_panel)

            outdoor_panel: PanelWidget = self.render_outdoor(data.outside)
            outdoor_panel.left = 400
            outdoor_panel.top = 300
            main_panel.add_child(outdoor_panel)

        # time
        today: datetime = datetime.today()

        clock_text: TextWidget = TextWidget(400, 140, font=self.font_huge)
        clock_text.left = 400
        clock_text.top = 50
        clock_text.text = today.strftime("%H:%M")
        main_panel.add_child(clock_text)

        date_text: TextWidget = TextWidget(400, 50, font=self.font_medium)
        date_text.left = 400
        date_text.top = 0
        date_text.horizontal_alignment = Alignments.CENTER
        date_text.text = today.strftime("%d %B %Y")
        main_panel.add_child(date_text)

        main_panel.is_children_draw_border(False)
        main_panel.draw(draw)

        result.add_bounding_box((0,0,400,300))
        result.add_bounding_box((0,300,400,600))
        result.add_bounding_box((400,0,800,300))
        result.add_bounding_box((400,300,800,600))

        return result

    def render_outdoor(self, outdoor_data: WeatherOutsideModel) -> PanelWidget:
        p: PanelWidget = PanelWidget(400, 300)

        temp_orig: str = outdoor_data.temperature
        temp_val: str = convert_float(temp_orig)

        temp_panel: PanelWidget = self.render_temp(temp_val)
        temp_panel.left = 50
        temp_panel.top = 80
        p.add_child(temp_panel)

        return p

    def render_indoor(self, indoor_data: WeatherInsideModel) -> PanelWidget:
        p: PanelWidget = PanelWidget(400, 300)

        temp_in_orig: str = indoor_data.temperature
        temp_in: str = convert_float(temp_in_orig)

        temp_panel: PanelWidget = self.render_temp(temp_in)
        temp_panel.left = 50
        temp_panel.top = 80

        humidity_in: str = indoor_data.humidity

        co2_in: str = indoor_data.co2

        t1: TextWidget = TextWidget(30,30, font=self.font_weather_medium)
        t1.text = self.icon_lookup.look_up_with_name('wi_barometer')
        t1.left = 50
        t1.top = temp_panel.top + temp_panel.height
        p.add_child(t1)

        t2: TextWidget = TextWidget(100,30, font=self.font_medium)
        t2.horizontal_alignment = Alignments.RIGHT
        t2.text = co2_in
        t2.left = t1.left + t1.width
        t2.top = temp_panel.top + temp_panel.height
        p.add_child(t2)

        t3: TextWidget = TextWidget(50,30, font=self.font_small)
        t3.horizontal_alignment = Alignments.LEFT
        t3.vertical_alignment = Alignments.BOTTOM
        t3.text = "ppm"
        t3.left = t2.left + t2.width + 10
        t3.top = temp_panel.top + temp_panel.height
        p.add_child(t3)

        p.add_child(temp_panel)
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

        temp_text: TextWidget = TextWidget(150, 130, font=self.font_huge)
        temp_text.left = 30
        temp_text.top = 0
        temp_text.horizontal_alignment = Alignments.RIGHT
        temp_text.vertical_alignment = Alignments.TOP
        temp_text.text = degree_val
        p.add_child(temp_text)

        temp2: TextWidget = TextWidget(90,70, font=self.font_large)
        temp2.left = 190
        temp2.top = 0
        temp2.horizontal_alignment = Alignments.LEFT
        temp2.vertical_alignment = Alignments.TOP
        temp2.text = "." + subdegree_val

        p.add_child(temp2)

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
        # self.window.draw(draw)
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
        temp_out_orig: str = data.outside.temperature
        temp_in_orig: str = data.inside.temperature

        tempOut: str = convert_float(temp_out_orig)
        temp_in: str = convert_float(temp_in_orig)

        humidity_out: str = data.outside.humidity
        humidity_in: str = data.inside.humidity

        co2_in: str = data.inside.co2

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

    def show_widget_border(self, show_border: bool):
        self.window.is_draw_border(show_border)
        self.window.is_children_draw_border(show_border)
