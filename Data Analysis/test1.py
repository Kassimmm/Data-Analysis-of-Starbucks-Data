import os
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import matplotlib.pyplot as plt
import seaborn as sns

def generate_sample_data(data, file_name, num_rows=10000):
    if not os.path.exists(file_name):
        df = data.sample(n=num_rows, random_state=1)
        df.to_csv(file_name, index=False)

# Define a function to load data
@st.cache_data
def load_data():
    load_data = pd.read_csv("stores.csv")
    generate_sample_data(load_data, 'sample_data.csv')
    data = pd.read_csv('sample_data.csv')
    data = data.drop(columns=['Id', 'PostalCode', 'PhoneNumber'])
    data.dropna(subset=['Latitude', 'Longitude'], inplace=True)
    return data

data = load_data()

# Define the map display function
def display_map(data, zoom_start=2):
    """Display a map with markers for given data."""
    if data.empty:
        st.write("No data to display on the map for the selected year.")
        return

    # Determine center of the map for better focus
    latitude_center = data['Latitude'].mean()
    longitude_center = data['Longitude'].mean()

    m = folium.Map(location=[latitude_center, longitude_center], zoom_start=zoom_start)
    for idx, row in data.iterrows():
        folium.Marker(
            [row['Latitude'], row['Longitude']],
            popup=f"{row['Name']}<br>{row['Street1']}",
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(m)
    folium_static(m)

# Setup navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Choose a page", ["Home", "Global Map", "City Analysis", "Global Map by Year"])

if page == "Home":
    st.image("images/starbucks.png", width=500)
    st.title("Welcome to Starbucks Store Analysis")
    st.write("Explore Starbucks store locations worldwide through various analytical perspectives.")

elif page == "Global Map":
    st.title("Global Starbucks Locations")
    st.write("Visual representation of all Starbucks locations across the globe.")
    display_map(data)  # Display the map using the generalized function

elif page == "City Analysis":
    st.title("City-specific Starbucks Analysis")
    country = st.selectbox('Select a Country', [''] + list(data['CountryCode'].unique()))
    if country:
        filtered_data = data[data['CountryCode'] == country]
        city = st.selectbox('Select a City', [''] + list(filtered_data['City'].dropna().unique()))
        if city:
            city_data = filtered_data[filtered_data['City'] == city]
            st.write(f"Number of Starbucks stores in {city}, {country}: {len(city_data)}")
            st.dataframe(city_data[['Name', 'Street1']].rename(columns={'Name': 'Store Name', 'Street1': 'Address'}))
            display_map(city_data, zoom_start=12)  # Use the new map display function

elif page == "Global Map by Year":
    st.title("Global Starbucks Locations by Year")
    if 'FirstSeen' in data.columns:
        data['FirstSeen'] = pd.to_datetime(data['FirstSeen'], errors='coerce')
        valid_years = data['FirstSeen'].dt.year.dropna().unique()
        if valid_years.size > 0:
            year_min, year_max = int(valid_years.min()), int(valid_years.max())
            year = st.slider("Select a Year", min_value=year_min, max_value=year_max, value=year_min)
            filtered_data = data[data['FirstSeen'].dt.year == year]
            display_map(filtered_data, zoom_start=2)  # Using the new map function for year-specific display
        else:
            st.write("No valid years found in the data.")
