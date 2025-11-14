from ocean import OceanAPI
from forecast import MarineForecastAPI  # Updated import
from parser import OceanParse
import utils
from datetime import datetime, timezone, timedelta
import pandas as pd

class OceanApp:
    def __init__(self):
        self.buoy_id = None
        self.lat = None
        self.lon = None

    def run(self):
        # Prompt for inputs
        buoy_input = input("Enter NOAA Buoy ID (e.g., 46026) or press Enter for default: ").strip()
        self.buoy_id = int(buoy_input) if buoy_input else 46026

        coords = utils.get_buoy_coords(self.buoy_id)
        if coords:
            self.lat, self.lon = coords
            print(f"Using coords for Buoy {self.buoy_id}: {self.lat}, {self.lon}")
        else:
            lat_input = input(f"No coords found for Buoy {self.buoy_id}. Enter latitude (e.g., 37.75): ").strip()
            lon_input = input("Enter longitude (e.g., -122.84): ").strip()
            try:
                self.lat = float(lat_input)
                self.lon = float(lon_input)
            except ValueError:
                print("Invalid coords; using default 37.75, -122.84")
                self.lat, self.lon = 37.75, -122.84

        # Init APIs with inputs
        self.oceanAPI = OceanAPI(self.buoy_id)
        self.forecastAPI = MarineForecastAPI(lat=self.lat, lon=self.lon)

        now = datetime.now(timezone.utc)
        yesterday = now - timedelta(days=1)
        tomorrow = now + timedelta(days=1)
        day_after = now + timedelta(days=2)

        # Current/Past conditions
        response = self.oceanAPI.get_conditions()
        if response:
            parser = OceanParse(response)
            df_conditions = parser.to_dataframe()
            df_conditions_hourly = utils.group_hourly(df_conditions)

            # Split historical by day
            df_yesterday = df_conditions_hourly[df_conditions_hourly.index.to_series().dt.date == yesterday.date()]
            df_today = df_conditions_hourly[df_conditions_hourly.index.to_series().dt.date == now.date()]

            # Print sections if not empty
            if not df_yesterday.empty:
                utils.print_colored_df(df_yesterday, "Yesterday's Surf Conditions (NOAA Buoy 46026)")
                utils.ascii_bar_chart(df_yesterday, title="Yesterday's Wave Height Chart")

            if not df_today.empty:
                utils.print_colored_df(df_today, "Today's Surf Conditions So Far (NOAA Buoy 46026)")
                utils.ascii_bar_chart(df_today, title="Today's Wave Height Chart (Historical)")

        else:
            print("Failed to fetch conditions data.")

        # Forecast (extend to 48h)
        forecast_data = self.forecastAPI.get_forecast()
        if forecast_data:
            hourly = forecast_data['hourly']
            df_forecast = pd.DataFrame({
                'datetime': [datetime.fromisoformat(t).replace(tzinfo=timezone.utc) for t in hourly['time']],
                'wave_height': hourly['wave_height'],
                'wave_direction': hourly['wave_direction'],
                'wave_period': hourly['wave_period'],
                'swell_height': hourly['swell_wave_height'],
                'swell_direction': hourly['swell_wave_direction'],
                'swell_period': hourly['swell_wave_period']
            })
            df_forecast = df_forecast[df_forecast['datetime'] >= now]  # Future and current
            df_forecast = df_forecast.head(48)  # Up to 48 hours (2 days out)
            df_forecast.set_index('datetime', inplace=True)
            df_forecast_hourly = utils.group_hourly(df_forecast, is_forecast=True)  # Already hourly, but consistent

            # Split forecast by day
            df_rest_today = df_forecast_hourly[df_forecast_hourly.index.to_series().dt.date == now.date()]
            df_tomorrow = df_forecast_hourly[df_forecast_hourly.index.to_series().dt.date == tomorrow.date()]
            df_day_after = df_forecast_hourly[df_forecast_hourly.index.to_series().dt.date == day_after.date()]
            # Print sections if not empty
            if not df_rest_today.empty:
                utils.print_colored_df(df_rest_today, "Forecast for Rest of Today (Open-Meteo Model)")
                utils.ascii_bar_chart(df_rest_today, title="Rest of Today's Wave Height Forecast")

            if not df_tomorrow.empty:
                utils.print_colored_df(df_tomorrow, "Tomorrow's Wave Forecast (Open-Meteo Model)")
                utils.ascii_bar_chart(df_tomorrow, title="Tomorrow's Wave Height Forecast")

            if not df_day_after.empty:  # Only if data extends (depending on API)
                utils.print_colored_df(df_day_after, "Day After Tomorrow's Wave Forecast (Open-Meteo Model)")
                utils.ascii_bar_chart(df_day_after, title="Day After Tomorrow's Wave Height Forecast")

        else:
            print("Failed to fetch forecast data.")