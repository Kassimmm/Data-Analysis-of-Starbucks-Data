import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import matplotlib.pyplot as plt
import seaborn as sns
import os

def generate_sample_data(data, file_name, num_rows=10000):
    if not os.path.exists(file_name):
        df = data.sample(n=num_rows, random_state=1)
        df.to_csv(file_name, index=False)

@st.cache_data
def load_data():
    data = pd.read_csv("stores.csv")
    generate_sample_data(data, 'sample_data.csv')
    data = pd.read_csv('sample_data.csv')
    data = data.drop(columns=['Id', 'PostalCode', 'PhoneNumber'])
    data.dropna(subset=['Latitude', 'Longitude'], inplace=True)
    return data

data = load_data()

def display_map(data, zoom_start=2):
    if data.empty:
        st.write("No data to display on the map for the selected year.")
        return
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

def plot_city_distribution(data, country):
    st.header(f'Top 10 Cities by Number of Stores in {country}')
    plt.figure(figsize=(10, 6))
    city_counts = data['City'].value_counts().nlargest(10)
    sns.barplot(y=city_counts.index, x=city_counts.values, palette='viridis')
    plt.title(f'Top 10 Cities by Number of Stores in {country}')
    plt.xlabel('Number of Stores')
    plt.ylabel('City')
    st.pyplot(plt.gcf())  # Pass the current figure to streamlit

def plot_ownership_type(data, city):
    st.header(f'Ownership Types in {city}')
    ownership_counts = data['OwnershipType'].value_counts()
    plt.figure(figsize=(8, 6))
    sns.set(style="whitegrid")
    colors = sns.color_palette('pastel')
    plt.pie(ownership_counts, labels=ownership_counts.index, autopct='%1.1f%%', startangle=90, colors=colors)
    plt.title(f'Ownership Types in {city}')
    st.pyplot(plt.gcf())

st.sidebar.title("Navigation")
page = st.sidebar.radio("Choose a page", ["Home", "Global Map", "City Analysis", "Global Map by Year"])

if page == "Home":
    st.image("images/starbucks.png", use_column_width=True)
    st.markdown("<h1 style='text-align: center;'>Welcome to Starbucks Store Analysis</h1>", unsafe_allow_html=True)

    st.markdown("<p style='text-align: center;'>Explore Starbucks store locations worldwide through various analytical perspectives.</p>", unsafe_allow_html=True)

    video_path = "images/starbucks.mp4"
    video_url = open(video_path, 'rb')

    #autoplay video
    st.video(video_path, format='video/mp4', start_time=0)
    
elif page == "Global Map":
    st.title("Global Starbucks Locations")
    display_map(data)

elif page == "City Analysis":
    country = st.selectbox('Select a Country', [''] + list(data['CountryCode'].unique()))
    if country:
        filtered_data = data[data['CountryCode'] == country]
        city = st.selectbox('Select a City', [''] + list(filtered_data['City'].dropna().unique()))
        if city:
            city_data = filtered_data[filtered_data['City'] == city]
            st.write(f"Number of Starbucks stores in {city}, {country}: {len(city_data)}")
            st.dataframe(city_data[['Name', 'Street1']].rename(columns={'Name': 'Store Name', 'Street1': 'Address'}))
            display_map(city_data, zoom_start=12)
            plot_city_distribution(filtered_data, country)
            plot_ownership_type(city_data, city)

elif page == "Global Map by Year":
    if 'FirstSeen' in data.columns:
        data['FirstSeen'] = pd.to_datetime(data['FirstSeen'], errors='coerce')
        valid_years = data['FirstSeen'].dt.year.dropna().unique()
        if valid_years.size > 0:
            year_min, year_max = int(valid_years.min()), int(valid_years.max())
            year = st.slider("Select a Year", min_value=year_min, max_value=year_max, value=year_min)
            filtered_data = data[data['FirstSeen'].dt.year == year]
            display_map(filtered_data, zoom_start=2)
        else:
            st.write("No valid years found in the data.")
    else:
        st.write("The 'FirstSeen' column is missing from the dataset.")