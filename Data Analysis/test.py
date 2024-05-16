import os
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

# Define all necessary functions upfront
def display_city_map(data):
    """ Display an enhanced map with custom markers for the city """
    m = folium.Map(location=[data['Latitude'].mean(), data['Longitude'].mean()], zoom_start=12)
    for idx, row in data.iterrows():
        folium.Marker(
            [row['Latitude'], row['Longitude']],
            popup=f"{row['Name']}<br>{row['Street1']}",
            icon=folium.Icon(color='red', icon='glyphicon-star')
        ).add_to(m)
    folium_static(m)

def plot_city_distribution(data, country):
    fig, ax = plt.subplots()
    city_counts = data['City'].value_counts().nlargest(10)
    sns.barplot(x=city_counts.values, y=city_counts.index, ax=ax)
    ax.set_title('Top Cities by Number of Stores in ' + country)
    ax.set_xlabel('Number of Stores')
    ax.set_ylabel('City')
    st.pyplot(fig)


def plot_ownership_type(data, city):
    ownership_counts = data['OwnershipType'].replace({
        'CO': 'Company Operated',
        'LS': 'Licensed Store',
        'JV': 'Joint Venture',
        'Franchised': 'Franchised'
    }).value_counts()

    fig, ax = plt.subplots()
    ax.pie(ownership_counts, labels=ownership_counts.index, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')
    plt.title('Ownership Types in ' + city)
    st.pyplot(fig)


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
    display_city_map(data)  # Assuming global map uses the same structure

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
            display_city_map(city_data)  # Customized city map
            plot_city_distribution(filtered_data, country)
            plot_ownership_type(city_data, city)

elif page == "Global Map by Year":
    st.title("Global Starbucks Locations by Year")
    
    # Convert FirstSeen column to datetime
    data['FirstSeen'] = pd.to_datetime(data['FirstSeen'])

    # Exclude NaN values when calculating min and max
    valid_years = data['FirstSeen'].dt.year[~data['FirstSeen'].isnull()]
    if not valid_years.empty:
        year_min = int(valid_years.min())
        year_max = int(valid_years.max())

        year = st.slider("Select a Year", min_value=year_min, max_value=year_max)
        filtered_data = data[data['FirstSeen'].dt.year == year]
        display_city_map(filtered_data)  # Assuming global map uses the same structure
    else:
        st.write("No valid years found in the data.")
