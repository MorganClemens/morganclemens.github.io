# utils.py
import numpy as np
import pandas as pd
pd.set_option('future.no_silent_downcasting', True) # remove downcasting warning

def ascii_bar_chart(df, key='wave_height', title='Wave Height Chart', max_height=10):
    if df.empty:
        print("No data to display.")
        return
    df = df[df[key].notna()]
    if df.empty:
        print(f"No valid {key} data to display.")
        return
    values = df[key].tolist()
    times = df.index.strftime('%H:%M').tolist()  # Hourly, so %H:00 works fine
    max_val = max(values)
    scale = max_height / max_val if max_val > 0 else 1
    
    # ANSI color codes
    RESET = '\033[0m'
    BOLD = '\033[1m'
    GREEN = '\033[32m' # More compatible green
    YELLOW = '\033[93m'
    RED = '\033[91m'
    
    print(f"\n{BOLD}{title}:{RESET}")
    for time, val in zip(times, values):
        if val < 1:
            color = RED
        elif val < 2:
            color = YELLOW
        else:
            color = GREEN
        bar = color + '|' * int(val * scale) + RESET
        print(f"{time}: {bar} ({val:.1f}m)")

def print_colored_df(df, title):
    print(f"\n\033[1m{title}\033[0m\n")  # Bold title
    # Custom string format: color directions blue, heights green, etc.
    print(df.to_string(float_format='%.1f', index=True))  # Example: 1 decimal, keep as-is or enhance

def vector_mean_dir(degrees):
    degrees = degrees.dropna()  # Drop NaNs
    if len(degrees) == 0:
        return np.nan
    radians = np.deg2rad(degrees)
    return (np.rad2deg(np.arctan2(np.mean(np.sin(radians)), np.mean(np.cos(radians)))) + 360) % 360

def group_hourly(df, is_forecast=False):
    if df.empty:
        return df
    
    # Ensure index is datetime
    df.index = pd.to_datetime(df.index, utc=True)
    
    # Define aggregation dict based on DataFrame type
    if not is_forecast:
        # Historical aggs
        agg_dict = {
            'wind_direction': vector_mean_dir,
            'wind_speed': 'mean',
            'wave_height': 'mean',
            'dominant_wave_period': 'mean',
            'average_wave_period': 'mean',
            'wave_direction': vector_mean_dir,
            'water_temp': 'mean',
            'tide': 'mean'
        }
    else:
        # Forecast aggs
        agg_dict = {
            'wave_height': 'mean',
            'wave_direction': vector_mean_dir,
            'wave_period': 'mean',
            'swell_height': 'mean',
            'swell_direction': vector_mean_dir,
            'swell_period': 'mean'
        }
    
    # Resample to hourly (aligns to hour start, 12:00-13:00)
    hourly_df = df.resample('h').agg(agg_dict)
    
    # Optional: Forward-fill small gaps (e.g., if an hour has no data)
    hourly_df = hourly_df.ffill(limit=1)  # Limit to 1 hour to avoid over-filling
    
    # Drop any fully NaN rows
    hourly_df.dropna(how='all', inplace=True)
    
    return hourly_df

# Move this to a more formal location in future
BUOY_COORDS = {
    46026: (37.75, -122.84),
    46005: (46.13, -131.09),
    46011: (34.96, -120.99),
    46012: (37.36, -122.98),
    # Add more here
}

def get_buoy_coords(buoy_id):
    return BUOY_COORDS.get(buoy_id, None)