import requests

class MarineForecastAPI:
    def __init__(self, lat=37.75, lon=-122.84):
        self.lat = lat
        self.lon = lon

    def get_forecast(self):
        url = (
            f"https://marine-api.open-meteo.com/v1/marine?"
            f"latitude={self.lat}&longitude={self.lon}"
            f"&hourly=wave_height,wave_direction,wave_period,"
            "swell_wave_height,swell_wave_direction,swell_wave_period"
            "&timezone=UTC"
        )
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        return None
