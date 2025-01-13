import streamlit as st
import pandas as pd
import datetime
import base64
import folium
from streamlit_folium import st_folium
from folium.plugins import BoatMarker, MousePosition, Draw

# Setup the Open-Meteo API client with cache and retry on error
from weather_fetch import *
from utils import *
# Streamlit UI

st.set_page_config(
    page_title="Weather App - Open-Meteo",
    page_icon="🌦️",
    initial_sidebar_state="expanded"
)
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
openmeteo = openmeteo_requests.Client(session = cache_session)

st.session_state['data'] = False

def pipeline_fetch_weather_marine_data(lat, lon):
    import streamlit as st
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

    return weather_forecast_df, marine__forecast_df

# Function to get the base64 string for the image
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Set the background image using the function above
def set_png_as_page_bg(png_file):
    bin_str = get_base64_of_bin_file(png_file)
    page_bg_img = '''
    <style>
    .stApp {
        background-image: url("data:image/png;base64,%s");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: scroll; /* You can change this to 'fixed' if you want the image to not scroll */
    }
    </style>
    ''' % bin_str
    st.markdown(page_bg_img, unsafe_allow_html=True)

def show_map_in_streamlit(lat, lon, zoom_start=5):
    """
    Create and display a Folium map in Streamlit using st_folium.

    Parameters:
    - lat (float): Latitude of the map center.
    - lon (float): Longitude of the map center.
    - zoom_start (int): Initial zoom level for the map. Default is 13.

    Returns:
    None. Displays the map directly in Streamlit.
    """
    # Create a base map
    m = folium.Map(location=[lat, lon], zoom_start=zoom_start)
    MousePosition().add_to(m)
    Draw(export=True).add_to(m)
    # Add a marker at the specified location
    folium.plugins.BoatMarker(
        location=(lat, lon), heading=45, wind_heading=150, wind_speed=45, color="#8f8"
    ).add_to(m)

    folium.plugins.Geocoder().add_to(m)
    folium.Circle([lat, lon],color="red",radius=15).add_to(m)

    # Display the map in Streamlit using st_folium
    st_map = st_folium(m, width=700, height=450)

# Set your .png file path here
background_img_path = 'weather-purple.jpg'  # Replace with the actual path to your .png file
set_png_as_page_bg(background_img_path)

start_lat, start_lon = 0,0
st.session_state['lat'] = start_lat 
st.session_state['lon'] = start_lon 

st.title('Weather App - Open-Meteo')

if 'show_map' not in st.session_state:
    st.session_state.show_map = True

col1, col2  = st.columns(2)
with col1:
    # User input for latitude and longitude
    lat = st.number_input('Enter Latitude', min_value=-90.0, max_value=90.0, value=0.0, step=0.01)
    start_date = st.date_input("Date")
with col2:
    lon = st.number_input('Enter Longitude', min_value=-180.0, max_value=180.0, value=0.0, step=0.01)
    start_time = st.time_input("Time")

if st.session_state.show_map:
    show_map_in_streamlit(lat, lon)

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

historical_metrics = {
    'temperature_2m': '°C',
    'rain': 'mm',
    'surface_pressure': 'hPa',
    'wind_speed_10m': 'm/s',
    'wind_direction_10m': '°',
}

aqi_metrics = {
    'pm10': '',
    'pm2_5': '',
    'carbon_monoxide': '',
    'carbon_dioxide': '',
    'nitrogen_dioxide': '',
    'sulphur_dioxide': '',
    'ozone': '',
    'dust': '',
    'uv_index': ''
    }

elevation_metrics = {'elevation':'m'}

col1, col2, col3 = st.columns(3)
# Place buttons in columns
with col1:
    if st.button('Get Future Weather Data'):
    # Convert to datetime
        date_object = datetime.strptime(f"{start_date} {start_time}", '%Y-%m-%d %H:%M:%S')
        date_object= pd.to_datetime(round_datetime(date_object)).tz_localize('UTC')
        weather_forecast_df, marine__forecast_df = pipeline_fetch_weather_marine_data(lat, lon)
        try:
            forecastdatapoint = weather_forecast_df[weather_forecast_df['date'] == date_object].iloc[0]
            data_forecast = {
            'temperature_2m': round(forecastdatapoint['temperature_2m'], 2),
            'rain': round(forecastdatapoint['rain'], 2),
            'surface_pressure': round(forecastdatapoint['surface_pressure'], 2),
            'wind_speed_10m': round(forecastdatapoint['wind_speed_10m'], 2),
            'wind_direction_10m': round(forecastdatapoint['wind_direction_10m'], 2)
            }
        
        except:
            data_forecast = {
            'temperature_2m': None,
            'rain': None,
            'surface_pressure': None,
            'wind_speed_10m': None,
            'wind_direction_10m': None
            }

        try: 
            marinedatapoint = marine__forecast_df[marine__forecast_df['date'] == date_object].iloc[0]
            data_marine = {
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

        except:
            data_marine = {
            'wave_height': None,
            'wave_direction': None,
            'wave_period': None,
            'wind_wave_height': None,
            'wind_wave_direction': None,
            'wind_wave_period': None,
            'swell_wave_height': None,
            'swell_wave_direction': None,
            'swell_wave_period': None,
            'ocean_current_velocity': None,
            'ocean_current_direction': None
            }

        data =  {**data_forecast, **data_marine}

        st.session_state['data'] = {
            'data': data,
            'timestamp': date_object,
            'type':'forecast'
        }

    if st.button('Get Historical Weather'):
        date_object = datetime.strptime(f"{start_date} {start_time}", '%Y-%m-%d %H:%M:%S')
        date_object= pd.to_datetime(round_datetime(date_object)).tz_localize('UTC')

        historical_data = pd.DataFrame(fetch_historical_data(lat, lon, start_date, start_date))
        
        try: 
            historical_data = historical_data[historical_data['date']==date_object].iloc[0]
            
            data = {
            'temperature_2m': round(historical_data['temperature_2m'], 2),
            'rain': round(historical_data['rain'], 2),
            'relative_humidity_2m': round(historical_data['relative_humidity_2m'], 2),
            'surface_pressure': round(historical_data['surface_pressure'], 2),
            'wind_speed_10m': round(historical_data['wind_speed_10m'], 2),
            'wind_direction_10m': round(historical_data['wind_direction_10m'], 2),
            'wind_direction_10m': round(historical_data['wind_direction_10m'], 2),
            }

        except:
            data = {
            'temperature_2m': None,
            'rain': None,
            'relative_humidity_2m': None,
            'surface_pressure': None,
            'wind_speed_10m': None,
            'wind_direction_10m': None,
            'wind_direction_10m': None,
            }

        # Get the current timestamp
        latest_timestamp = datetime.now()
        latest_timestamp = round_datetime(latest_timestamp)

        latest_timestamp = pd.to_datetime(round_datetime(latest_timestamp)).tz_localize('UTC')
        
        st.session_state['data'] = {
            'data': data,
            'timestamp': latest_timestamp,
            'type':'historical'
        }   

with col2:
    if st.button('Get Latest Weather'):
        weather_forecast_df, marine__forecast_df = pipeline_fetch_weather_marine_data(lat, lon)

        # Get the current timestamp
        latest_timestamp = datetime.now()
        latest_timestamp = round_datetime(latest_timestamp)

        latest_timestamp = pd.to_datetime(round_datetime(latest_timestamp)).tz_localize('UTC')

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

        st.session_state['data'] = {
            'data': data,
            'timestamp': latest_timestamp,
            'type':'forecast'
        }

    if st.button('Get Current AQI'):
        aquidata = pd.DataFrame(fetch_aqi(lat,lon))

        latest_timestamp = datetime.now()
        latest_timestamp = round_datetime(latest_timestamp)

        latest_timestamp = pd.to_datetime(round_datetime(latest_timestamp)).tz_localize('UTC')
        aquidata = aquidata[aquidata['date']==latest_timestamp].iloc[0]

        data = {
        'pm10': round(aquidata['pm10'], 2),
        'pm2_5': round(aquidata['pm2_5'], 2),
        'carbon_monoxide': round(aquidata['carbon_monoxide'], 2),
        'carbon_dioxide': round(aquidata['carbon_dioxide'], 2),
        'nitrogen_dioxide': round(aquidata['nitrogen_dioxide'], 2),
        'sulphur_dioxide': round(aquidata['sulphur_dioxide'], 2),
        'ozone': round(aquidata['ozone'], 2),
        'dust': round(aquidata['dust'], 2),
        'uv_index': round(aquidata['uv_index'], 2)
        }
        
        st.session_state['data'] = {
            'data': data,
            'timestamp': latest_timestamp,
            'type':'aqi'
        }

with col3:
    if st.button('Get Elevation'):
        elevation = fetch_elevation_data(10, 1)['elevation'][0]
        st.session_state['data'] = {
            'data': elevation,
            'type':'elevation'
        }
        
    if st.button("Get River Discharge"):
        data = fetch_river_discharge(lat,lon)

        st.session_state['data'] = {
            'data': data,
            'type':'discharge'
        }


if st.session_state['data']:
    data = st.session_state['data']['data']
    type = st.session_state['data']['type']

    if type == "forecast":
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

    elif (type == "historical"):
        for i, (metric, unit) in enumerate(historical_metrics.items()):
            # Use column layout for better aesthetics
            if i < len(historical_metrics) / 2:
                display_column = col1
            else:
                display_column = col2
            
            # Fetch the actual value from your data structure (replace 'data' with your actual data variable)
            value = data.get(metric, "N/A")
            
            # Display metric with unit and value in big, bold font
            display_column.markdown(f"**:blue[{metric.replace('_', ' ').title()}]**: {value} {unit}", unsafe_allow_html=True)
            
            # Add some spacing for better readability
            display_column.markdown("<br>", unsafe_allow_html=True)

    elif (type == "aqi"):
        for i, (metric, unit) in enumerate(aqi_metrics.items()):
            # Use column layout for better aesthetics
            if i < len(aqi_metrics) / 2:
                display_column = col1
            else:
                display_column = col2
            
            # Fetch the actual value from your data structure (replace 'data' with your actual data variable)
            value = data.get(metric, "N/A")
            
            # Display metric with unit and value in big, bold font
            display_column.markdown(f"**:blue[{metric.replace('_', ' ').title()}]**: {value} {unit}", unsafe_allow_html=True)
            
            # Add some spacing for better readability
            display_column.markdown("<br>", unsafe_allow_html=True)

    elif (type == "elevation"):
        for i, (metric, unit) in enumerate(elevation_metrics.items()):
            # Use column layout for better aesthetics
            if i < len(elevation_metrics) / 2:
                display_column = col1
            else:
                display_column = col2
            
            # Fetch the actual value from your data structure (replace 'data' with your actual data variable)
            value = data
            
            # Display metric with unit and value in big, bold font
            display_column.markdown(f"**:blue[{metric.replace('_', ' ').title()}]**: {value} {unit}", unsafe_allow_html=True)
            
            # Add some spacing for better readability
            display_column.markdown("<br>", unsafe_allow_html=True)

    elif (type == "discharge"): 
        datadf = pd.DataFrame(data)
        st.write(f"Showing next {len(datadf)} days discharge forecast")
        st.write(datadf)

    else:
        print("Waiting for input ,1")

else:
    print(f"cache cleared")

st.markdown("==== Geocoding ====")  # Horizontal line for separation
st.markdown("Search locations globally")

user_input = st.text_input("Search")
#country_input = st.text_input("Country")
num_results = int(st.number_input("Num Results (how many rows you want returned)", min_value=10, max_value=100,))

if st.button("Show Result"):
    result = pd.DataFrame(fetch_geocoding(user_input,num_results)['results'])
    #result = result[result['country']==country_input]
    st.write(result)

st.markdown("---")  # Horizontal line for separation

# Optional: Add some styling or additional information
st.markdown("""
**Note:** This app uses open-meteo API to fetch weather data. Make sure you have entered valid latitude and longitude coordinates.
""")

st.markdown('Website : <a href="https://open-meteo.com/" target="_blank">https://open-meteo.com/</a>', unsafe_allow_html=True)
