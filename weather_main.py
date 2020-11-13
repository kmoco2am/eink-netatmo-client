import os
import socket
import time
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

WAIT_TIME_SECONDS = 5


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

    def init_display(self):
        """Initialize the display - call the driver's init method"""
        self.driver.init(partial=self.partial)
        self.initialized = True

    def ready(self):
        """Check that the driver is loaded and initialized"""
        return self.driver and self.initialized

    @staticmethod
    def error(msg, code=1):
        """Print error and exit"""
        print(msg)
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
    diff_bbox: Optional[Tuple[int, int, int, int]] = None
    while True:
        try:
            try:
                last_data: Optional[dict] = loader.get_last_data()
            except netatmo_client.NoData:
                last_data = None
            except socket.timeout:
                last_data = None
            image = desktop.render(last_data)

            if previous_image:
                diff_bbox = desktop.band(desktop.img_diff(image, previous_image))

            if diff_bbox:
                # increment update counter
                updates = (updates + 1) % 60
                changed_image_area = image.crop(diff_bbox)
                wcm.driver.draw(diff_bbox[0], diff_bbox[1], changed_image_area)
            else:
                if updates == 0:
                    updates = (updates + 1) % 60
                    wcm.driver.draw(0, 0, image)

            previous_image = image.copy()
            time.sleep(60)
        except ProgramKilled:
            print("Weather main killed")
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
    # add all the CLI commands
    cli.add_command(print_bitmap)
    cli.add_command(list_drivers)
    cli.add_command(main)
    cli()

