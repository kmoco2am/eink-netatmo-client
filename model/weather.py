from dataclasses import dataclass
from typing import Optional, TypeVar

import lnetatmo
import logging

T = TypeVar("T")


def sanitize_val(d: dict, value_name: str, default_value: Optional[T]) -> Optional[T]:
    if d is None:
        return default_value
    elif value_name in d:
        return d[value_name]
    else:
        return default_value


DEFAULT_NONE_TEMPERATURE = '--.-'
DEFAULT_NONE_HUMIDITY = '--'
DEFAULT_NONE_CO2 = '---'


@dataclass
class WeatherOutsideModel:
    temperature: Optional[float]
    humidity: Optional[int]

    def __init__(self, temperature: Optional[float], humidity: Optional[int]):
        self.temperature = temperature
        self.humidity = humidity


@dataclass
class WeatherInsideModel:
    temperature: Optional[float]
    humidity: Optional[int]
    co2: Optional[int]

    def __init__(self, temperature: Optional[float], humidity: Optional[int], co2: Optional[int]):
        self.temperature = temperature
        self.humidity = humidity
        self.co2 = co2


@dataclass
class WeatherModel:
    outside: WeatherOutsideModel
    inside: WeatherInsideModel

    def __init__(self, outside: WeatherOutsideModel, inside: WeatherInsideModel):
        self.outside = outside
        self.inside = inside


class NetatmoDataLoader:

    auth: lnetatmo.ClientAuth

    def __init__(self) -> None:
        logging.info("Netatmo authentication")
        self.auth = lnetatmo.ClientAuth()

    def load_data(self) -> Optional[WeatherModel]:
        client = lnetatmo.WeatherStationData(self.auth)
        data = client.lastData()
        if data:
            outdoor_data = sanitize_val(data, 'Outdoor', None)
            indoor_data = sanitize_val(data, 'Indoor', None)
            outside_model = WeatherOutsideModel(
                sanitize_val(outdoor_data, 'Temperature', DEFAULT_NONE_TEMPERATURE),
                sanitize_val(outdoor_data, 'Humidity', DEFAULT_NONE_HUMIDITY)
            )
            inside_model = WeatherInsideModel(
                sanitize_val(indoor_data, 'Temperature', DEFAULT_NONE_TEMPERATURE),
                sanitize_val(indoor_data, 'Humidity', DEFAULT_NONE_HUMIDITY),
                sanitize_val(indoor_data, 'CO2', DEFAULT_NONE_CO2)
            )
            return WeatherModel(outside_model, inside_model)
        else:
            return None
