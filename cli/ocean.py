import requests # Used to make API calls



class OceanAPI:
    def __init__(self, buoy):
        self.buoy = buoy

    def get_conditions(self):
        url = "https://www.ndbc.noaa.gov/data/realtime2/" + str(self.buoy) + ".txt"
        response = requests.get(url)
        # Get string if response successful (status 200)
        if response.status_code == 200:
            data = response.text
            return data
        else:
            return None      