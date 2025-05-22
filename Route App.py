import streamlit as st
import pandas as pd
import datetime
import base64
import folium
from streamlit_folium import st_folium
from folium.plugins import BoatMarker, MousePosition, Draw

import math 
import ast

from pyproj import Geod

# Setup the Open-Meteo API client with cache and retry on error

from simulation_vessel import * 
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

if 'route' not in st.session_state:
    st.session_state.route = []

st.title('Route Creator App')


def string_to_array_array(s):
    # Remove the outer brackets and split by '],[' to handle each coordinate pair
    s = s.strip('[]')
    pairs = s.split('],[')
    
    # Convert each string pair into a tuple of floats
    result = []
    for pair in pairs:
        # Replace '[' and ']' with '' for correct parsing
        pair = pair.replace('[', '').replace(']', '')
        coords = pair.split(',')
        # Convert string numbers to floats
        result.append([float(coord) for coord in coords])
    
    final_result = []
    for coord in result:
        final_result.append([coord[1],coord[0]])

    return final_result

def string_to_array_array_format2(s):
    # Remove the outer brackets and split by '],[' to handle each coordinate pair
    s = s.strip('[]')
    pairs = s.split('),(')
    
    # Convert each string pair into a tuple of floats
    result = []
    for pair in pairs:
        # Replace '[' and ']' with '' for correct parsing
        pair = pair.replace('[', '').replace(']', '')
        coords = pair.split(',')
        # Convert string numbers to floats
        result.append([float(coord) for coord in coords])
    
    final_result = []
    for coord in result:
        final_result.append([coord[1],coord[0]])

    return final_result

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

def show_map_in_streamlit(lat, lon, zoom_start=2):
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
    folium.plugins.Geocoder().add_to(m)
    Draw(export=True).add_to(m)
    # Add a marker at the specified location
    folium.Circle([lat, lon],color="red",radius=5).add_to(m)
    MousePosition().add_to(m)

    # Display the map in Streamlit using st_folium
    st_map = st_folium(m, width=700, height=450)

def show_route_in_streamlit(points, zoom_start=2):
    """
    Create and display a Folium map in Streamlit using st_folium.

    Parameters:
    - lat (float): Latitude of the map center.
    - lon (float): Longitude of the map center.
    - zoom_start (int): Initial zoom level for the map. Default is 13.

    Returns:
    None. Displays the map directly in Streamlit.
    """
    m = folium.Map()
    MousePosition().add_to(m)
    folium.plugins.BoatMarker(
        location=(points[0][0], points[0][1]), heading=45, wind_heading=150, wind_speed=45, color="#8f8"
    ).add_to(m)
    
    folium.plugins.Geocoder().add_to(m)

    for pt in points:
        # Add a marker at the specified location
        folium.Circle([pt[0], pt[1]],color="red",radius=7).add_to(m)

    folium.PolyLine(points).add_to(m)

    # Display the map in Streamlit using st_folium
    st_map = st_folium(m, width=700, height=450)

# Set your .png file path here
background_img_path = 'weather-purple.jpg'  # Replace with the actual path to your .png file
set_png_as_page_bg(background_img_path)

routestring = st.text_area("Enter List of Coordinates (eg [[38.793333, -75.03], [38.431783, -74.711166], [35.266516, -74.2892]] or [(38.793333, -75.03), (38.431783, -74.711166), (35.266516, -74.2892)] )")
route_format = st.checkbox("folium format")

col1, col2 = st.columns(2)

with col1: 
    granularity = st.number_input("Granularity (in Nautical Miles)", min_value=10)
with col2:
    if st.button("Enter"):
        if route_format : 
            route = string_to_array_array(routestring)
        else:
            route = string_to_array_array_format2(routestring)
        st.session_state['route'] = route
        st.write("Route Loaded..")
        #st.session_state.show_route = True

if 'show_map' not in st.session_state:
    st.session_state.show_map = True

start_lat, start_lon = 0,0
if st.session_state.show_map:
    show_map_in_streamlit(start_lat, start_lon)
        
col1, col2  = st.columns(2)
with col1:
    # User input for latitude and longitude
    lat = st.number_input('Enter Latitude', min_value=-90.0, max_value=90.0, value=0.0, step=0.01)
with col2:
    lon = st.number_input('Enter Longitude', min_value=-180.0, max_value=180.0, value=0.0, step=0.01)

import json 

col1, col2  = st.columns(2)
with col1:
    if st.button("Add to Route"):
        st.session_state.route.append((lat,lon))
    if st.button("Remove from Route"):
        st.session_state['route'] = st.session_state['route'][:-1]
    if st.button("Empty Route"):
        st.session_state['route'] = []
        st.session_state.show_route = False
with col2:
    if st.button("Show Route"):
        st.write(f"{st.session_state['route']}")
    if 'show_route' not in st.session_state:
        st.session_state.show_route = False
    if st.button("Plot Route"):
        if len(st.session_state['route'])>1:
            st.session_state.show_route = True
    if st.button("Finalize Route"):
        route_dict = {}
        route_dict['route'] = st.session_state['route']
        # File path for the JSON file
        file_path = "output.json"
        # Write the dictionary to a JSON file
        with open(file_path, "w") as json_file:
            json.dump(route_dict, json_file, indent=4)  # 'indent' makes the JSON pretty-printed
        st.write("Route Saved...")

if st.session_state.show_route:
        show_route_in_streamlit(expand_route_geodesic(st.session_state['route'], granularity))
    
if st.button("Calculate Route Metrics"):
    route_distance = calculate_route_distance(st.session_state['route'])
    legs = len(st.session_state['route'])-1
    st.write(f"There are {legs} legs to the voyage.")
    route_distance_m = route_distance
    route_distance_nm = route_distance_m/1852
    st.write(f"Total Distance : {round(route_distance_nm,2)} Nautical Miles")
    time1 = route_distance_nm / 5 # at 5 knots 
    time2 = route_distance_nm / 15 # at 15 knots
    st.write(f" Duration : ~ {math.floor(round(time2/24,2))} to {math.floor(round(time1/24,2))} days (if sailing at 5-15 knots speed)")

