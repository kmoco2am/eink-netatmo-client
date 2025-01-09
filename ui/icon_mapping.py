import json
from typing import Optional


# https://gist.github.com/tbranyen/62d974681dea8ee0caa1
class IconMappingLookup:
    def __init__(self, value_path: str):
        self.map = None
        with open(value_path, 'r') as f:
            self.map = json.load(f)

    def lookup_icon(self, weather_code: int, is_day: bool) -> Optional[str]:
        icon_raw: str = self.map[str(weather_code)]['icon']

        # 7xx and 9xx do not get prefixed w/ day/night
        # If we are not in the ranges mentioned above, add a day/night prefix.
        if not(699 < weather_code < 800) and not(899 < weather_code < 1000):
            if is_day:
                icon = 'day_' + icon_raw
            else:
                icon = 'night_' + icon_raw
        else:
            icon = icon_raw

        # Finally tack on the prefix.
        return 'wi_' + icon
