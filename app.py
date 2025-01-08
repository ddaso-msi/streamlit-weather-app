import streamlit as st
import pandas as pd
from retry_requests import retry
import datetime
# Setup the Open-Meteo API client with cache and retry on error


from weather_fetch import *
from utils import *
# Streamlit UI

cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)


st.title('Weather App - open-meteo')

# User input for latitude and longitude
lat = st.number_input('Enter Latitude', min_value=-90.0, max_value=90.0, value=0.0, step=0.01)
lon = st.number_input('Enter Longitude', min_value=-180.0, max_value=180.0, value=0.0, step=0.01)

metrics = {
    'temperature_2m': '°C',
    'rain': 'mm',
    'surface_pressure': 'hPa',
    'wind_speed_10m': 'm/s',
    'wind_direction_10m': '°',
    'wave_height': 'm',
    'wave_direction': '°',
    'wave_period': 's',
    'wind_wave_height': 'm',
    'wind_wave_direction': '°',
    'wind_wave_period': 's',
    'swell_wave_height': 'm',
    'swell_wave_direction': '°',
    'swell_wave_period': 's',
    'ocean_current_velocity': 'm/s',
    'ocean_current_direction': '°'
    }

if st.button('Get Latest Weather'):
    weather__forecast_data = featch_weather_forecast(lat, lon, 7)
    if 'Error' in weather__forecast_data:
        st.error(weather__forecast_data['Error'])
    else:
        weather_forecast_df = pd.DataFrame(featch_weather_forecast(lat, lon, 7))

    marine__forecast_data = fetch_marine_forecast(lat, lon)
    if 'Error' in marine__forecast_data:
        st.error(marine__forecast_data['Error'])
    else:
        marine__forecast_df = pd.DataFrame(fetch_marine_forecast(lat, lon))

    # Get the current timestamp
    latest_timestamp = datetime.now()
    latest_timestamp = round_datetime(latest_timestamp)

    latest_timestamp = pd.to_datetime(round_datetime(latest_timestamp)).tz_localize('UTC')

    print(weather_forecast_df.columns)
    print(marine__forecast_df.columns)

    forecastdatapoint = weather_forecast_df[weather_forecast_df['date'] == latest_timestamp].iloc[0]
    marinedatapoint = marine__forecast_df[marine__forecast_df['date'] == latest_timestamp].iloc[0]

    data = {
    'temperature_2m': round(forecastdatapoint['temperature_2m'], 2),
    'rain': round(forecastdatapoint['rain'], 2),
    'surface_pressure': round(forecastdatapoint['surface_pressure'], 2),
    'wind_speed_10m': round(forecastdatapoint['wind_speed_10m'], 2),
    'wind_direction_10m': round(forecastdatapoint['wind_direction_10m'], 2),
    'wave_height': round(marinedatapoint['wave_height'], 2),
    'wave_direction': round(marinedatapoint['wave_direction'], 2),
    'wave_period': round(marinedatapoint['wave_period'], 2),
    'wind_wave_height': round(marinedatapoint['wind_wave_height'], 2),
    'wind_wave_direction': round(marinedatapoint['wind_wave_direction'], 2),
    'wind_wave_period': round(marinedatapoint['wind_wave_period'], 2),
    'swell_wave_height': round(marinedatapoint['swell_wave_height'], 2),
    'swell_wave_direction': round(marinedatapoint['swell_wave_direction'], 2),
    'swell_wave_period': round(marinedatapoint['swell_wave_period'], 2),
    'ocean_current_velocity': round(marinedatapoint['ocean_current_velocity'], 2),
    'ocean_current_direction': round(marinedatapoint['ocean_current_direction'], 2)
    }

    
    # Displaying metrics in two columns for better visual organization
    col1, col2 = st.columns(2)

    for i, (metric, unit) in enumerate(metrics.items()):
        # Use column layout for better aesthetics
        if i < len(metrics) / 2:
            display_column = col1
        else:
            display_column = col2
        
        # Fetch the actual value from your data structure (replace 'data' with your actual data variable)
        value = data.get(metric, "N/A")
        
        # Display metric with unit and value in big, bold font
        display_column.markdown(f"**:blue[{metric.replace('_', ' ').title()}]**: {value} {unit}", unsafe_allow_html=True)
        
        # Add some spacing for better readability
        display_column.markdown("<br>", unsafe_allow_html=True)

    st.markdown("---")  # Horizontal line for separation

# Optional: Add some styling or additional information
st.markdown("""
**Note:** This app uses open-meteo API to fetch weather data. Make sure you have entered valid latitude and longitude coordinates.
""")