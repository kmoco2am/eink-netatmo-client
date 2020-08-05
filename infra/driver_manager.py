# display drivers - note: they are GPL licensed, unlike this file
import drivers.drivers_base as drivers_base
import drivers.drivers_partial as drivers_partial
import drivers.drivers_full as drivers_full
import drivers.drivers_color as drivers_color
import drivers.drivers_colordraw as drivers_colordraw
import drivers.driver_it8951 as driver_it8951
# for tidy driver list
from collections import OrderedDict


class DriverManager:

    def __init__(self) -> None:
        self.driverdict = {}
        driverlist = [drivers_partial.EPD1in54, drivers_partial.EPD2in13, drivers_partial.EPD2in13v2, drivers_partial.EPD2in9,
                      drivers_partial.EPD2in13d,
                      drivers_full.EPD2in7, drivers_full.EPD4in2, drivers_full.EPD7in5, drivers_full.EPD7in5v2,
                      drivers_color.EPD4in2b, drivers_color.EPD7in5b, drivers_color.EPD5in83, drivers_color.EPD5in83b,
                      drivers_colordraw.EPD1in54b, drivers_colordraw.EPD1in54c, drivers_colordraw.EPD2in13b,
                      drivers_colordraw.EPD2in7b, drivers_colordraw.EPD2in9b, driver_it8951.IT8951,
                      drivers_base.Dummy, drivers_base.Bitmap]
        for driver in driverlist:
            self.driverdict[driver.__name__] = {'desc': driver.__doc__, 'class': driver}

    def get_drivers(self):
        """Get the list of available drivers as a dict
        Format: { '<NAME>': { 'desc': '<DESCRIPTION>', 'class': <CLASS> }, ... }"""
        return self.driverdict

    def get_driver_list(self):
        """Get a neat printable driver list"""
        order = OrderedDict(sorted(self.get_drivers().items()))
        return '\n'.join(["{}{}".format(driver.ljust(15), order[driver]['desc']) for driver in order])

    def get_driver_by_name(self, driver):
        matched_drivers = [n for n in self.get_drivers() if n.lower() == driver.lower()]
        return matched_drivers
