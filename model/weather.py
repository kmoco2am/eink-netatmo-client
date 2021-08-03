import netatmo_client
import logging

class WeatherOutsideModel:
    def __init__(self, data) -> None:
        self._temperature = data['Temperature']
        self._humidity = data['Humidity']


class WeatherInsideModel:
    def __init__(self, data) -> None:
        self._temperature = data['Temperature']
        self._humidity = data['Humidity']
        self._co2 = data['CO2']


class WeatherModel:
    def __init__(self, data: dict) -> None:
        self._outside = WeatherOutsideModel(data['Outdoor'])
        self._inside = WeatherInsideModel(data['Indoor'])

    @property
    def outside(self) -> WeatherOutsideModel:
        return self._outside

    @property
    def inside(self) -> WeatherInsideModel:
        return self._inside


class NetatmoDataLoader:
    def __init__(self) -> None:
        logging.info("Netatmo authentication")
        self.auth = netatmo_client.ClientAuth()

    def get_last_data(self) -> dict:
        dev = netatmo_client.WeatherStationData(self.auth)
        return dev.lastData()

    def load_data(self) -> WeatherModel:
        data = self.get_last_data()
        return WeatherModel(data)
