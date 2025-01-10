import openmeteo_requests

import requests_cache
import pandas as pd
from retry_requests import retry


cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

def fetch_marine_forecast(lat, long):
    url = "https://marine-api.open-meteo.com/v1/marine"
    params = {
        "latitude": lat ,
        "longitude": long ,
        "hourly": ["wave_height", "wave_direction", "wave_period", "wind_wave_height", "wind_wave_direction", "wind_wave_period", "swell_wave_height", "swell_wave_direction", "swell_wave_period", "ocean_current_velocity", "ocean_current_direction"]
    }

    responses = openmeteo.weather_api(url, params=params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]
    # Process hourly data. The order of variables needs to be the same as requested.
    hourly = response.Hourly()
    hourly_wave_height = hourly.Variables(0).ValuesAsNumpy()
    hourly_wave_direction = hourly.Variables(1).ValuesAsNumpy()
    hourly_wave_period = hourly.Variables(2).ValuesAsNumpy()
    hourly_wind_wave_height = hourly.Variables(3).ValuesAsNumpy()
    hourly_wind_wave_direction = hourly.Variables(4).ValuesAsNumpy()
    hourly_wind_wave_period = hourly.Variables(5).ValuesAsNumpy()
    hourly_swell_wave_height = hourly.Variables(6).ValuesAsNumpy()
    hourly_swell_wave_direction = hourly.Variables(7).ValuesAsNumpy()
    hourly_swell_wave_period = hourly.Variables(8).ValuesAsNumpy()
    hourly_ocean_current_velocity = hourly.Variables(9).ValuesAsNumpy()
    hourly_ocean_current_direction = hourly.Variables(10).ValuesAsNumpy()

    hourly_data = {"date": pd.date_range(
        start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
        end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = hourly.Interval()),
        inclusive = "left"
    )}
    hourly_data["wave_height"] = hourly_wave_height
    hourly_data["wave_direction"] = hourly_wave_direction
    hourly_data["wave_period"] = hourly_wave_period
    hourly_data["wind_wave_height"] = hourly_wind_wave_height
    hourly_data["wind_wave_direction"] = hourly_wind_wave_direction
    hourly_data["wind_wave_period"] = hourly_wind_wave_period
    hourly_data["swell_wave_height"] = hourly_swell_wave_height
    hourly_data["swell_wave_direction"] = hourly_swell_wave_direction
    hourly_data["swell_wave_period"] = hourly_swell_wave_period
    hourly_data["ocean_current_velocity"] = hourly_ocean_current_velocity
    hourly_data["ocean_current_direction"] = hourly_ocean_current_direction

    return hourly_data

def featch_weather_forecast(lat,long,forecast_days=16):
    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat ,
        "longitude": long ,
        "hourly": ["temperature_2m", "rain", "surface_pressure", "wind_speed_10m", "wind_direction_10m"],
        "forecast_days": forecast_days 
    }

    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]
    # Process hourly data. The order of variables needs to be the same as requested.
    hourly = response.Hourly()
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
    hourly_rain = hourly.Variables(1).ValuesAsNumpy()
    hourly_surface_pressure = hourly.Variables(2).ValuesAsNumpy()
    hourly_wind_speed_10m = hourly.Variables(3).ValuesAsNumpy()
    hourly_wind_direction_10m = hourly.Variables(4).ValuesAsNumpy()

    hourly_data = {"date": pd.date_range(
        start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
        end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = hourly.Interval()),
        inclusive = "left"
    )}
    hourly_data["temperature_2m"] = hourly_temperature_2m
    hourly_data["rain"] = hourly_rain
    hourly_data["surface_pressure"] = hourly_surface_pressure
    hourly_data["wind_speed_10m"] = hourly_wind_speed_10m
    hourly_data["wind_direction_10m"] = hourly_wind_direction_10m    

    return hourly_data

def fetch_historical_data(lat, long, start, end):
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": long,
        "start_date": start,
        "end_date": end,
        "hourly": ["temperature_2m", "relative_humidity_2m", "rain", "surface_pressure", "wind_speed_10m", "wind_direction_10m"]
    }
    responses = openmeteo.weather_api(url, params=params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]
    # Process hourly data. The order of variables needs to be the same as requested.
    hourly = response.Hourly()
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
    hourly_relative_humidity_2m = hourly.Variables(1).ValuesAsNumpy()
    hourly_rain = hourly.Variables(2).ValuesAsNumpy()
    hourly_surface_pressure = hourly.Variables(3).ValuesAsNumpy()
    hourly_wind_speed_10m = hourly.Variables(4).ValuesAsNumpy()
    hourly_wind_direction_10m = hourly.Variables(5).ValuesAsNumpy()

    hourly_data = {"date": pd.date_range(
        start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
        end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = hourly.Interval()),
        inclusive = "left"
    )}
    hourly_data["temperature_2m"] = hourly_temperature_2m
    hourly_data["relative_humidity_2m"] = hourly_relative_humidity_2m
    hourly_data["rain"] = hourly_rain
    hourly_data["surface_pressure"] = hourly_surface_pressure
    hourly_data["wind_speed_10m"] = hourly_wind_speed_10m
    hourly_data["wind_direction_10m"] = hourly_wind_direction_10m

    return hourly_data

# Iterate through granular route and exctract all weather data and keep appending it together 

def fetch_weather_data_along_route(granular_coordinates):
    forecastdata = pd.DataFrame(columns=['date', 'temperature_2m', 'rain', 'surface_pressure', 'wind_speed_10m',
        'wind_direction_10m', 'coordinate'])

    for waypoint in granular_coordinates:
        response = featch_weather_forecast(waypoint[0],waypoint[1],16)
        responsedf = pd.DataFrame(response)
        responsedf['coordinate'] = str((waypoint[0],waypoint[1]))
        forecastdata = pd.concat([forecastdata, responsedf], ignore_index=True)

    return forecastdata

