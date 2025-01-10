import openmeteo_requests

import requests_cache
import pandas as pd
from retry_requests import retry

import requests


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

    try:
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

    except: 
        hourly_data = None

    return hourly_data

def fetch_aqi(lat, long):
    # The order of variables in hourly or daily is important to assign them correctly below
    url = "https://air-quality-api.open-meteo.com/v1/air-quality"
    params = {
        "latitude": lat,
        "longitude": long,
        "hourly": ["pm10", "pm2_5", "carbon_monoxide", "carbon_dioxide", "nitrogen_dioxide", "sulphur_dioxide", "ozone", "dust", "uv_index"]
    }
    responses = openmeteo.weather_api(url, params=params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]
    print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
    print(f"Elevation {response.Elevation()} m asl")
    print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
    print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

    # Process hourly data. The order of variables needs to be the same as requested.
    hourly = response.Hourly()
    hourly_pm10 = hourly.Variables(0).ValuesAsNumpy()
    hourly_pm2_5 = hourly.Variables(1).ValuesAsNumpy()
    hourly_carbon_monoxide = hourly.Variables(2).ValuesAsNumpy()
    hourly_carbon_dioxide = hourly.Variables(3).ValuesAsNumpy()
    hourly_nitrogen_dioxide = hourly.Variables(4).ValuesAsNumpy()
    hourly_sulphur_dioxide = hourly.Variables(5).ValuesAsNumpy()
    hourly_ozone = hourly.Variables(6).ValuesAsNumpy()
    hourly_dust = hourly.Variables(7).ValuesAsNumpy()
    hourly_uv_index = hourly.Variables(8).ValuesAsNumpy()

    hourly_data = {"date": pd.date_range(
        start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
        end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = hourly.Interval()),
        inclusive = "left"
    )}
    hourly_data["pm10"] = hourly_pm10
    hourly_data["pm2_5"] = hourly_pm2_5
    hourly_data["carbon_monoxide"] = hourly_carbon_monoxide
    hourly_data["carbon_dioxide"] = hourly_carbon_dioxide
    hourly_data["nitrogen_dioxide"] = hourly_nitrogen_dioxide
    hourly_data["sulphur_dioxide"] = hourly_sulphur_dioxide
    hourly_data["ozone"] = hourly_ozone
    hourly_data["dust"] = hourly_dust
    hourly_data["uv_index"] = hourly_uv_index

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



def fetch_elevation_data(latitude, longitude):
    """
    Fetch elevation data from the Open-Meteo API.

    Args:
    latitude (float): The latitude coordinate.
    longitude (float): The longitude coordinate.

    Returns:
    dict: A dictionary containing the elevation data or None if there's an error.

    Raises:
    requests.exceptions.RequestException: If there's an issue with the HTTP request.
    """
    # Construct the API URL
    url = f"https://api.open-meteo.com/v1/elevation?latitude={latitude}&longitude={longitude}"
    
    try:
        # Make the request to the API
        response = requests.get(url)
        response.raise_for_status()  # Will raise an exception for bad status codes
        
        # Parse JSON response
        data = response.json()
        
        # Check if the response contains elevation data
        if 'elevation' in data:
            return data
        else:
            print("Elevation data not found in response.")
            return None

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching data: {e}")
        return None
    

def fetch_geocoding(search_term, num_results):
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={search_term}&count={num_results}&language=en&format=json"

    try:
        # Make the request to the API
        response = requests.get(url)
        response.raise_for_status()  # Will raise an exception for bad status codes
        
        # Parse JSON response
        data = response.json()
        
        return data

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching data: {e}")
        return None
    
def fetch_river_discharge(lat, long):
    url = "https://flood-api.open-meteo.com/v1/flood"
    params = {
        "latitude": lat,
        "longitude": long,
        "daily": "river_discharge"
    }
    responses = openmeteo.weather_api(url, params=params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]
    # Process daily data. The order of variables needs to be the same as requested.
    daily = response.Daily()
    daily_river_discharge = daily.Variables(0).ValuesAsNumpy()

    daily_data = {"date": pd.date_range(
        start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
        end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = daily.Interval()),
        inclusive = "left"
    )}
    daily_data["river_discharge"] = daily_river_discharge

    return daily_data