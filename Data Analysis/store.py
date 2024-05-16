#working

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import matplotlib.pyplot as plt
import seaborn as sns

# Load and cache the data
@st.cache_data
def load_data():
    data = pd.read_csv("stores.csv")
    data = data.drop(columns=['Id', 'PostalCode', 'PhoneNumber'])
    data.dropna(subset=['Latitude', 'Longitude'], inplace=True)
    return data

data = load_data()

st.image("images/starbucks.png", width=500)
st.title("Welcome to Starbucks Store Analysis")
st.write("This app provides an in-depth analysis of Starbucks store locations worldwide.")

def display_global_map(data):
    """ Display a simple global map with default markers """
    m = folium.Map(location=[0, 0], zoom_start=2)
    for idx, row in data.iterrows():
        folium.Marker([row['Latitude'], row['Longitude']]).add_to(m)
    folium_static(m)

display_global_map(data)

st.image("images/starbucks.png", width=500)
st.title("Welcome to Starbucks Store Analysis")
st.write("This app provides an in-depth analysis of Starbucks store locations worldwide.")



country = st.selectbox('Select a Country', [''] + list(data['CountryCode'].unique()))

if country:
    filtered_data = data[data['CountryCode'] == country]
    city = st.selectbox('Select a City', [''] + list(filtered_data['City'].dropna().unique()))

    if city:
        city_data = filtered_data[filtered_data['City'] == city]
        st.write(f"Number of Starbucks stores in {city}, {country}: {len(city_data)}")
        st.dataframe(city_data[['Name', 'Street1']].rename(columns={'Name': 'Store Name', 'Street1': 'Address'}))

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

        display_city_map(city_data)  # Customized city map

        # Plotting number of stores by city within the selected country
        def plot_city_distribution(data):
            fig, ax = plt.subplots()
            city_counts = data['City'].value_counts().nlargest(10)  # You might adjust the number shown
            sns.barplot(x=city_counts.values, y=city_counts.index, ax=ax)
            ax.set_title('Top Cities by Number of Stores in ' + country)
            ax.set_xlabel('Number of Stores')
            ax.set_ylabel('City')
            st.pyplot(fig)

        plot_city_distribution(filtered_data)

        # Ownership type pie chart for the selected city
        def plot_ownership_type(data):
            ownership_counts = data['OwnershipType'].value_counts()
            fig, ax = plt.subplots()
            ax.pie(ownership_counts, labels=ownership_counts.index, autopct='%1.1f%%', startangle=90)
            ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
            plt.title('Ownership Types in ' + city)
            st.pyplot(fig)

        plot_ownership_type(city_data)

#--------------------------------------

#working
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import matplotlib.pyplot as plt
import seaborn as sns

# Define a function to load data
@st.cache_data
def load_data():
    data = pd.read_csv("stores.csv")
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
    ownership_counts = data['OwnershipType'].value_counts()
    fig, ax = plt.subplots()
    ax.pie(ownership_counts, labels=ownership_counts.index, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')
    plt.title('Ownership Types in ' + city)
    st.pyplot(fig)

# Setup navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Choose a page", ["Home", "Global Map", "City Analysis", "Opening Timeline"])

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

elif page == "Opening Timeline":
    st.title("Starbucks Locations Opening Timeline")
    # Assuming 'OpeningDate' has been converted to datetime
    min_year = int(data['OpeningDate'].dt.year.min())
    max_year = int(data['OpeningDate'].dt.year.max())
    year_selected = st.slider("Select Year", min_year, max_year, min_year)
    
    def display_openings_by_year(data, year):
        year_data = data[data['OpeningDate'].dt.year <= year]
        m = folium.Map(location=[0, 0], zoom_start=2)
        for idx, row in year_data.iterrows():
            folium.Marker(
                [row['Latitude'], row['Longitude']],
                popup=f"{row['Name']}<br>{row['Street1']}<br>Opened: {row['OpeningDate'].strftime('%Y-%m-%d')}",
                icon=folium.Icon(color='blue', icon='info-sign')
            ).add_to(m)
        folium_static(m)

    display_openings_by_year(data, year_selected)

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static

# st.set_theme('light')

logo_path = "images/starbucks.png"
st.image(logo_path, width=500)

# Load and cache the data
@st.cache_data  # Adjusted caching method
def load_data():
    data = pd.read_csv("stores.csv")
    # Keep only necessary columns for mapping and analysis
    data = data.drop(columns=['Id', 'PostalCode', 'PhoneNumber'])
    return data

data = load_data()

st.title("Welcome to Starbucks Store Analysis")
st.write("This app provides an in-depth analysis of Starbucks store locations worldwide.")

# Initialize placeholders
country_placeholder = st.empty()
city_placeholder = st.empty()
info_placeholder = st.empty()
table_placeholder = st.empty()
map_placeholder = st.empty()

# User input: Select a Country
country = country_placeholder.selectbox('Select a Country', [''] + list(data['CountryCode'].unique()))

if country:
    # Filter data based on the country selection
    filtered_data = data[data['CountryCode'] == country]

    # User input: Select a City
    city = city_placeholder.selectbox('Select a City', [''] + list(filtered_data['City'].dropna().unique()))

    if city:
        # Filter data based on the city selection
        city_data = filtered_data[filtered_data['City'] == city]

        # Display the number of Starbucks locations in the selected city
        info_placeholder.write(f"Number of Starbucks stores in {city}, {country}: {len(city_data)}")

        # Display Starbucks locations in the selected city using a data table
        table_placeholder.dataframe(city_data[['Name', 'Street1']].rename(columns={'Name': 'Store Name', 'Street1': 'Address'}), height=min(300, 25*len(city_data)))

        # Map display option
    show_map = st.checkbox('Show Map')
    if show_map:
        m = folium.Map(location=[city_data['Latitude'].mean(), city_data['Longitude'].mean()], zoom_start=12)
        for idx, row in city_data.iterrows():
            folium.CircleMarker(
                location=[row['Latitude'], row['Longitude']],
                radius=5,
                popup=f"{row['Name']}<br>{row['Street1']}",
                color='blue',
                fill=True,
                fill_color='blue'
            ).add_to(m)
        folium_static(m)  # Correct usage of folium_static





        #second codeimport streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import matplotlib.pyplot as plt

# Load and cache the data
@st.cache_data
def load_data():
    data = pd.read_csv("stores.csv")
    # Keep only necessary columns for mapping and analysis
    data = data.drop(columns=['Id', 'PostalCode', 'PhoneNumber'])
    return data

data = load_data()

st.title("Welcome to Starbucks Store Analysis")
st.write("This app provides an in-depth analysis of Starbucks store locations worldwide.")

# Function to plot the average number of stores per city
def plot_average_stores_per_city(filtered_data):
    average_stores = filtered_data.groupby('City').size().reset_index(name='Store Count')
    average_stores.sort_values(by='Store Count', ascending=False, inplace=True)
    fig, ax = plt.subplots()
    average_stores.head(10).plot(kind='bar', x='City', y='Store Count', ax=ax, legend=None)
    ax.set_xlabel('City')
    ax.set_ylabel('Average Number of Stores')
    ax.set_title('Average Number of Stores Per City')
    st.pyplot(fig)

# User input: Select a Country
country = st.selectbox('Select a Country', [''] + list(data['CountryCode'].unique()))

if country:
    # Filter data based on the country selection
    filtered_data = data[data['CountryCode'] == country]
    plot_average_stores_per_city(filtered_data)  # Call to plot function right after country selection

    # User input: Select a City
    city = st.selectbox('Select a City', [''] + list(filtered_data['City'].dropna().unique()))

    if city:
        # Filter data based on the city selection
        city_data = filtered_data[filtered_data['City'] == city]

        # Display the number of Starbucks locations in the selected city
        st.write(f"Number of Starbucks stores in {city}, {country}: {len(city_data)}")

        # Display Starbucks locations in the selected city using a data table
        st.dataframe(city_data[['Name', 'Street1']].rename(columns={'Name': 'Store Name', 'Street1': 'Address'}), height=min(300, 25*len(city_data)))

        # Map display option
        show_map = st.checkbox('Show Map')
        if show_map:
            m = folium.Map(location=[city_data['Latitude'].mean(), city_data['Longitude'].mean()], zoom_start=12)
            for idx, row in city_data.iterrows():
                folium.CircleMarker(
                    location=[row['Latitude'], row['Longitude']],
                    radius=5,
                    popup=f"{row['Name']}<br>{row['Street1']}",
                    color='blue',
                    fill=True,
                    fill_color='blue'
                ).add_to(m)
            folium_static(m)  # Display the map


# code 3

import streamlit as st
import pandas as pd
import pydeck as pdk
import matplotlib.pyplot as plt

logo_path = "images/starbucks.png"
st.image(logo_path, width=1000)

# Load and cache the data
@st.cache_data
def load_data():
    data = pd.read_csv("stores.csv")
    # Keep only necessary columns for mapping and analysis
    data = data.drop(columns=['Id', 'PostalCode', 'PhoneNumber'])
    return data

data = load_data()

def create_map(data, latitude, longitude, zoom=1):
    view_state = pdk.ViewState(latitude=latitude, longitude=longitude, zoom=zoom)
    layer = pdk.Layer(
        "HexagonLayer",
        data,
        get_position="[Longitude, Latitude]",
        radius=500,
        elevation_scale=500,
        elevation_range=[0, 1000],
        pickable=True,
        extruded=True,
    )
    map = pdk.Deck(
        map_style='mapbox://styles/mapbox/light-v9',
        initial_view_state=view_state,
        layers=[layer],
        tooltip={"text": "Store Count: {elevationValue}"}
    )
    return map

st.title("Welcome to Starbucks Store Analysis")
st.write("This app provides an in-depth analysis of Starbucks store locations worldwide.")

# Display the global map
st.pydeck_chart(create_map(data, 0, 0, zoom=1))

country = st.selectbox('Select a Country', [''] + list(data['CountryCode'].unique()))

if country:
    filtered_data = data[data['CountryCode'] == country]
    
    # Ownership type distribution as a pie chart
    ownership_counts = filtered_data['OwnershipType'].value_counts()
    fig, ax = plt.subplots()
    ax.pie(ownership_counts, labels=ownership_counts.index, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    ax.set_title('Ownership Type Distribution')
    st.pyplot(fig)

    city = st.selectbox('Select a City', [''] + list(filtered_data['City'].dropna().unique()))

    if city:
        city_data = filtered_data[filtered_data['City'] == city]
        st.write(f"Number of Starbucks stores in {city}, {country}: {len(city_data)}")
        st.dataframe(city_data[['Name', 'Street1']].rename(columns={'Name': 'Store Name', 'Street1': 'Address'}))

        # Display city map with detailed visualization
        if city_data.empty:
            st.write("No data available for this city.")
        else:
            st.pydeck_chart(create_map(city_data, city_data['Latitude'].mean(), city_data['Longitude'].mean(), zoom=12))


# 4th code
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import matplotlib.pyplot as plt
import seaborn as sns

# Load and cache the data
@st.cache_data
def load_data():
    data = pd.read_csv("stores.csv")
    data = data.drop(columns=['Id', 'PostalCode', 'PhoneNumber'])
    data.dropna(subset=['Latitude', 'Longitude'], inplace=True)
    return data

data = load_data()

st.image("images/starbucks.png", width=500)
st.title("Welcome to Starbucks Store Analysis")
st.write("This app provides an in-depth analysis of Starbucks store locations worldwide.")

def display_global_map(data):
    """ Display a simple global map with default markers """
    m = folium.Map(location=[0, 0], zoom_start=2)
    for idx, row in data.iterrows():
        folium.Marker([row['Latitude'], row['Longitude']]).add_to(m)
    folium_static(m)

display_global_map(data)  

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

# def plot_histogram_store_counts(data):
#     """ Histogram of Store Counts by Country """
#     fig, ax = plt.subplots(figsize=(10, 5))
#     sns.histplot(data['CountryCode'], kde=False, ax=ax, binwidth=1)
#     ax.set_title('Distribution of Stores by Country')
#     ax.set_xlabel('Country')
#     ax.set_ylabel('Number of Stores')
#     plt.xticks(rotation=90)  # Rotate the x-axis labels to prevent overlap
#     st.pyplot(fig)  # Use the figure object explicitly


# country = st.selectbox('Select a Country', [''] + list(data['CountryCode'].unique()))

# if country:
#     filtered_data = data[data['CountryCode'] == country]
#     city = st.selectbox('Select a City', [''] + list(filtered_data['City'].dropna().unique()))

#     if city:
#         city_data = filtered_data[filtered_data['City'] == city]
#         st.write(f"Number of Starbucks stores in {city}, {country}: {len(city_data)}")
#         st.dataframe(city_data[['Name', 'Street1']].rename(columns={'Name': 'Store Name', 'Street1': 'Address'}))
#         display_city_map(city_data)  # Customized city map

# plot_histogram_store_counts(data)  # Global histogram of store counts
