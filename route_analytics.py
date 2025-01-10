import streamlit as st
import pandas as pd
import datetime
import base64
import folium
from streamlit_folium import st_folium

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

if 'route' not in st.session_state:
    st.session_state.route = []

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

    # Add a marker at the specified location
    folium.Circle([lat, lon],color="red",radius=5).add_to(m)

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
    # Create a base map
    m = folium.Map(location=[lat, lon], zoom_start=zoom_start)

    for pt in points:
        # Add a marker at the specified location
        folium.Circle([pt[0], pt[1]],color="red",radius=5).add_to(m)

    folium.PolyLine(points).add_to(m)

    # Display the map in Streamlit using st_folium
    st_map = st_folium(m, width=700, height=450)

# Set your .png file path here
background_img_path = 'weather-purple.jpg'  # Replace with the actual path to your .png file
set_png_as_page_bg(background_img_path)


col1, col2  = st.columns(2)

with col1:
    # User input for latitude and longitude
    lat = st.number_input('Enter Latitude', min_value=-90.0, max_value=90.0, value=0.0, step=0.01)

with col2:
    lon = st.number_input('Enter Longitude', min_value=-180.0, max_value=180.0, value=0.0, step=0.01)

if 'show_map' not in st.session_state:
    st.session_state.show_map = True

if st.session_state.show_map:
    show_map_in_streamlit(lat, lon)

col1, col2, col3, col4, col5, col6  = st.columns(6)

with col1:
    if st.button("add to route"):
        st.session_state.route.append((lat,lon))
with col2:
    if st.button("show route"):
        st.write(f"{st.session_state['route']}")
with col3:
    if st.button("remove from route"):
        st.session_state['route'] = st.session_state['route'][:-1]
with col4:
    if st.button("empty route"):
        st.session_state['route'] = []
with col5:
    if 'show_route' not in st.session_state:
        st.session_state.show_route = False
with col6:
    if st.button("Plot route"):
        st.session_state.show_route = True
    
if st.session_state.show_route:
        show_route_in_streamlit(st.session_state['route'])
    
    
