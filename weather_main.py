import datetime
import locale
import os
import socket
import time
import logging
from typing import Optional

from model.open import OpenWeatherDataLoader, WeatherGenericData
from model.weather import NetatmoDataLoader, WeatherModel, WeatherOutsideModel, WeatherInsideModel
from schedule import configure_signals, ProgramKilled
import click
import sys
from infra.driver_manager import DriverManager
from PIL import Image

from ui.desktop import Desktop
from ui.render_result import RenderResult, BoundingBox

REDRAW_INTERVAL_SECONDS:int = 30
REDRAW_PARTIAL_NUMBER:int = 5

locale.setlocale(locale.LC_ALL, 'cs_CZ.UTF-8')

class WeatherClientMain:
    """The main class for Netatmo Weather Station client"""
    driver = None
    partial = None
    initialized = None
    white = None
    black = None
    encoding = None

    def __init__(self, driver, partial=None, encoding='utf-8'):
        """Create a PaperTTY with the chosen driver and settings"""
        manager = DriverManager()
        self.driver = manager.get_drivers()[driver]['class']()
        self.partial = partial
        self.white = self.driver.white
        self.black = self.driver.black
        self.encoding = encoding
        logging.info("Drivers loaded")

    def init_display(self):
        """Initialize the display - call the driver's init method"""
        self.driver.init(partial=self.partial)
        self.initialized = True
        logging.info("Display initialized")

    def ready(self):
        """Check that the driver is loaded and initialized"""
        return self.driver and self.initialized

    @staticmethod
    def error(msg, code=1):
        """Print error and exit"""
        logging.error(msg)
        sys.exit(code)


class Settings:
    """A class to store CLI settings so they can be referenced in the subcommands"""
    args: dict = {}

    project_dir: str
    output_dir: str
    settings_dir: str
    resources_dir: str

    def __init__(self, **kwargs):
        self.args = kwargs


@click.command(name='demo')
@click.option('--modern/--no-modern', default=False)
@click.pass_obj
def draw_demo(settings: Settings, modern: bool):
    desktop = Desktop(settings.resources_dir)
    data1: Optional[WeatherModel] = None
    gen_data1 = None
    rr1: RenderResult = desktop.render_modern(data1, gen_data1) if modern else desktop.render(data1)
    save_demo_file(rr1, desktop, settings.output_dir, "demo_nodata")
    data2: WeatherModel = WeatherModel(
        WeatherOutsideModel(None, None),
        WeatherInsideModel(None, None, None)
    )
    today = datetime.datetime.today()
    gen_data2: WeatherGenericData = WeatherGenericData(
        today,
        today + datetime.timedelta(hours=12),
        803,
        802,
        today + datetime.timedelta(hours=3),
        801,
        today + datetime.timedelta(hours=6),
        615,
        today + datetime.timedelta(hours=9),
    )
    rr2: RenderResult = desktop.render_modern(data2, gen_data2) if modern else desktop.render(data2)
    save_demo_file(rr2, desktop, settings.output_dir, "demo_empty")
    data3: WeatherModel = WeatherModel(
        WeatherOutsideModel(-28.1, 56),
        WeatherInsideModel(24.3, 65, 1223)
    )
    rr3: RenderResult = desktop.render_modern(data3, gen_data2) if modern else desktop.render(data3)
    save_demo_file(rr3, desktop, settings.output_dir, "demo_data3")
    logging.info("Demo pictures printed. Exiting.")


def save_demo_file(rr: RenderResult, desktop: Desktop, output_dir: str, filename: str):
    image = rr.image
    full_filename = os.path.join(output_dir, filename) + ".png"
    image.save(full_filename, "PNG")
    logging.info("Demo image generated: " + full_filename)


@click.command(name='main')
@click.pass_obj
def main(settings: Settings):
    configure_signals()
    wcm: WeatherClientMain = WeatherClientMain(**settings.args)
    wcm.init_display()
    loader = NetatmoDataLoader()
    owm_loader = OpenWeatherDataLoader()
    desktop = Desktop(settings.resources_dir)

    updates: int = 0
    previous_image: Optional[Image] = None
    logging.info("Starting data loop")
    while True:
        try:
            data: Optional[WeatherModel]
            try:
                data = loader.load_data()
                logging.debug("Data gathered")
            except socket.timeout:
                logging.warning("Netatmo Socket Timeout")
                data = None
            gen_data: Optional[WeatherGenericData]
            try:
                gen_data = owm_loader.load_data()
                logging.debug("OWM Data Loaded")
            except Exception:
                logging.warning("OWM loading failed")
                gen_data = None

            rr: RenderResult = desktop.render_modern(data, gen_data)
            image = rr.image
            bbs = rr.bounding_boxes

            if updates == 0:
                # full redraw
                updates = (updates + 1) % REDRAW_PARTIAL_NUMBER
                logging.debug("Full redraw")
                wcm.driver.draw(0, 0, image)
            else:
                change_detected = False
                logging.debug("Partial redraw")
                for bb in bbs:
                    banded_bb = desktop.band(bb)
                    cropped_image = image.crop(banded_bb)
                    cropped_previous_image = previous_image.crop(banded_bb)

                    img_diff: BoundingBox = desktop.img_diff(cropped_image, cropped_previous_image)

                    if img_diff:
                        # there is some difference
                        change_detected = True

                        diff_bbox: BoundingBox = desktop.band(img_diff)
                        changed_image_area = cropped_image.crop(diff_bbox)
                        x = banded_bb[0] + diff_bbox[0]
                        y = banded_bb[1] + diff_bbox[1]
                        wcm.driver.draw(x, y, changed_image_area)

                if change_detected:
                    # increment update counter
                    updates = (updates + 1) % REDRAW_PARTIAL_NUMBER

            previous_image = image.copy()
            logging.debug("Iteration finished")
            time.sleep(REDRAW_INTERVAL_SECONDS)
        except ProgramKilled:
            logging.info("Weather main killed")
            break


@click.command(name='bitmap')
@click.option('--file', default=None, help='Full path to a BMP file to load')
@click.pass_obj
def print_bitmap(settings, file):
    """Print bitmap from file"""
    wcm = WeatherClientMain(**settings.args)
    wcm.init_display()
    image = Image.open(file)
    wcm.driver.draw(0,0,image)
    WeatherClientMain.error(file, code=0)


@click.command(name='list')
def list_drivers():
    """List available display drivers"""
    manager = DriverManager()
    WeatherClientMain.error(manager.get_driver_list(), code=0)


@click.group()
@click.option('--driver', default=None, help='Select display driver')
@click.option('--nopartial', is_flag=True, default=False, help="Don't use partial updates even if display supports it")
@click.option('--encoding', default='utf-8', help='Encoding to use for the buffer', show_default=True)
@click.option('--debug', is_flag=True, default=False, help="Enable debug logging")
@click.pass_context
def cli(ctx, driver, nopartial, encoding, debug):
    """CLI configuration"""
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
    manager = DriverManager()
    if not driver:
        WeatherClientMain.error(
            "You must choose a display driver. If your 'C' variant is not listed, use the 'B' driver.\n\n{}".format(
                manager.get_driver_list()))
    else:
        matched_drivers = manager.get_driver_by_name(driver)
        if not matched_drivers:
            WeatherClientMain.error('Invalid driver selection, choose from:\n{}'.format(manager.get_driver_list()))

    project_dir = os.path.dirname(os.path.realpath(__file__))

    s = Settings(driver=matched_drivers[0],
                   partial=not nopartial,
                   encoding=encoding)
    s.project_dir=project_dir
    s.output_dir=os.path.join(project_dir, "output")
    s.resources_dir=os.path.join(project_dir, "resources")
    ctx.obj = s
    pass


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logging.info("Weather main is starting ...")
    # add all the CLI commands
    cli.add_command(print_bitmap)
    cli.add_command(list_drivers)
    cli.add_command(main)
    cli.add_command(draw_demo)
    cli()

