import json
from dataclasses import dataclass
from os.path import expanduser
from typing import Optional

from pyowm import OWM
from pyowm.weatherapi25.forecast import Forecast
from pyowm.weatherapi25.observation import Observation
from pyowm.weatherapi25.weather import Weather
import datetime
import pytz
from pyowm.weatherapi25.weather_manager import WeatherManager


@dataclass
class WeatherGenericData:
    sunrise: datetime
    sunset: datetime
    weather_code: int

    def __init__(self,
                 sunrise: datetime,
                 sunset: datetime,
                 weather_code: int,
                 forecast_code_1: int,
                 forecast_datetime_1: datetime,
                 forecast_code_2: int,
                 forecast_datetime_2: datetime,
                 forecast_code_3:int,
                 forecast_datetime_3: datetime):
        self.sunset = sunset
        self.sunrise = sunrise
        self.weather_code = weather_code
        self.forecast_code_1 = forecast_code_1
        self.forecast_datetime_1 = forecast_datetime_1
        self.forecast_code_2 = forecast_code_2
        self.forecast_datetime_2 = forecast_datetime_2
        self.forecast_code_3 = forecast_code_3
        self.forecast_datetime_3 = forecast_datetime_3


class OpenWeatherDataLoader:

    def __init__(self):
        self._credentialFile = expanduser("~/.owm.credentials")
        with open(self._credentialFile, "r", encoding="utf-8") as f:
            cred = {k.upper():v for k,v in json.loads(f.read()).items()}
        self._token = cred["TOKEN"]

    def load_data(self) -> Optional[WeatherGenericData]:
        owm:OWM = OWM(self._token)

        mgr: WeatherManager = owm.weather_manager()

        obs: Optional[Observation] = mgr.weather_at_place("Prague")
        weather: Weather = obs.weather
        code = weather.weather_code
        sunset_datetime: datetime = weather.sunset_time(timeformat="date")
        sunrise_datetime: datetime = weather.sunrise_time(timeformat="date")

        forecast_3h: Forecast = mgr.forecast_at_place('Prague', '3h').forecast

        forecast_weathers = forecast_3h.weathers
        return WeatherGenericData(
            sunrise_datetime,
            sunset_datetime,
            code,
            forecast_weathers[2].weather_code,
            forecast_weathers[2].reference_time(timeformat="date"),
            forecast_weathers[5].weather_code,
            forecast_weathers[5].reference_time(timeformat="date"),
            forecast_weathers[8].weather_code,
            forecast_weathers[8].reference_time(timeformat="date")
        )

