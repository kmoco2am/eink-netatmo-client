import os
import socket
import time
import logging
from typing import Optional, Tuple

import netatmo_client
from model.weather import NetatmoDataLoader
from schedule import configure_signals, ProgramKilled
from schedule.job import Job
import click
import sys
from infra.driver_manager import DriverManager
from PIL import Image, ImageDraw, ImageFont

from ui.desktop import Desktop
from ui.render_result import RenderResult, BoundingBox

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
    args = {}

    def __init__(self, **kwargs):
        self.args = kwargs


@click.command(name='main')
@click.pass_obj
def main(settings):
    configure_signals()
    wcm: WeatherClientMain = WeatherClientMain(**settings.args)
    wcm.init_display()
    loader = NetatmoDataLoader()
    project_dir = os.path.dirname(os.path.realpath(__file__))
    resources_dir = os.path.join(project_dir, "resources")
    desktop = Desktop(resources_dir)

    updates: int = 0
    previous_image: Optional[Image] = None
    logging.info("Starting data loop")
    while True:
        try:
            try:
                last_data: Optional[dict] = loader.get_last_data()
                logging.debug("Data gathered")
            except socket.timeout:
                logging.warning("Netatmo Socket Timeout")
                last_data = None
            except netatmo_client.NoData:
                logging.warning("No Data")
                last_data = None
            rr: RenderResult = desktop.render(last_data)
            image = rr.image
            bbs = rr.bounding_boxes

            if updates == 0:
                # full redraw
                updates = (updates + 1) % 60
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
                    updates = (updates + 1) % 60

            previous_image = image.copy()
            time.sleep(10)
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
@click.pass_context
def cli(ctx, driver, nopartial, encoding):
    """CLI configuration"""
    manager = DriverManager()
    if not driver:
        WeatherClientMain.error(
            "You must choose a display driver. If your 'C' variant is not listed, use the 'B' driver.\n\n{}".format(
                manager.get_driver_list()))
    else:
        matched_drivers = manager.get_driver_by_name(driver)
        if not matched_drivers:
            WeatherClientMain.error('Invalid driver selection, choose from:\n{}'.format(manager.get_driver_list()))
        ctx.obj = Settings(driver=matched_drivers[0], partial=not nopartial, encoding=encoding)
    pass


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logging.info("Weather main is starting ...")
    # add all the CLI commands
    cli.add_command(print_bitmap)
    cli.add_command(list_drivers)
    cli.add_command(main)
    cli()

