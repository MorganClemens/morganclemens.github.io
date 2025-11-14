from datetime import datetime, timedelta, timezone
import pandas as pd # To build dataframe
pd.set_option('future.no_silent_downcasting', True) # remove downcasting warning

class OceanParse:
    def __init__(self, response):
        self.response = response

    def parse_conditions(self):
        '''Extracts and structures ocean condition data.
        Returns a dictionary keyed by timestamps (datetime objects),
        each pointing to a dictionary of measurements.'''
        # Define time cutoff for filtering
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(hours=24)

        # Split to rows
        response_by_line = self.response.split('\n')
        data_by_time = {}

        for line in response_by_line:
            if line.startswith('#') or not line.strip():
                continue # skip headers, comments, and empty lines
            row = line.split()
            if len(row) < 19:
                continue  # Skip incomplete lines

            try:
                timestamp = datetime(
                    int(row[0]),  # year
                    int(row[1]),  # month
                    int(row[2]),  # day
                    int(row[3]),  # hour
                    int(row[4]),  # minute
                    tzinfo=timezone.utc # make object timezone aware
                )

                if timestamp < cutoff:
                    continue  # Skip old data

                data_by_time[timestamp] = {
                    "wind_direction": self.clean(row[5]),
                    "wind_speed": self.clean(row[6]),
                    "wave_height": self.clean(row[8]), # significant wave height
                    "dominant_wave_period": self.clean(row[9]),
                    "average_wave_period": self.clean(row[10]),
                    "wave_direction": self.clean(row[11]),
                    "water_temp": self.clean(row[14]),
                    "tide": self.clean(row[18])
                }

            except (IndexError, ValueError):
                continue  # Skip malformed or incomplete rows

        # Store list and return list of tuples sorted by time
        self.data_by_time = sorted(data_by_time.items())
        return self.data_by_time
    
    def to_dataframe(self):
        '''Converts parsed data into a Pandas DataFrame'''
        if not hasattr(self, 'data_by_time'):
            self.parse_conditions()

        timestamps = [ts for ts, _ in self.data_by_time]
        values = [v for _, v in self.data_by_time]

        df = pd.DataFrame(values, index=timestamps)
        df.index.name = "datetime"
        return df

    def clean(self, value):
        '''Converts missing values to None and attempts float conversion.'''
        if value == "MM":
            return None
        try:
            return float(value)
        except ValueError:
            return value  # fallback
