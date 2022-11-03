# Author: Michael Wong
import streamlit as st
import pandas as pd
import numpy as np
import requests
import json
import plotly.express as px


def get_csse_data(user_choice):
    # Log: May implement an option to allow a user to specific a custom country.
    # API Used: https://rapidapi.com/axisbits-axisbits-default/api/covid-19-statistics/
    response = None
    successful = None
    url = "https://covid-19-statistics.p.rapidapi.com/reports"

    if(user_choice == "country"):
        querystring = {"region_name": "US", "iso": "USA"}
    else:
        querystring = {"q": "US " +
                       str(user_choice), "region_name": "US", "iso": "USA"}
    try:
        # Load API key
        csse = open("csse_api.json")
        csse = json.load(csse)  # dictionary
        api_key = csse["api_key"]  # string

        headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": "covid-19-statistics.p.rapidapi.com"
        }
        response = requests.request(
            "GET", url, headers=headers, params=querystring)
    except:
        st.error('CSSE API Response: Failed', icon="🚨")
        successful = False

    if successful is not False:
        st.success('CSSE API Response: Successful', icon="✅")
        return response.json()


def get_vaccovid_data():
    # Log: May implement an option to allow a user to specific a custom country.
    # API Used: https://rapidapi.com/vaccovidlive-vaccovidlive-default/api/vaccovid-coronavirus-vaccine-and-treatment-tracker/
    # API only returns around 29 days instead of 6 months.
    response = None
    successful = None

    url = "https://vaccovid-coronavirus-vaccine-and-treatment-tracker.p.rapidapi.com/api/covid-ovid-data/sixmonth/USA"

    try:
        # Load API key
        vaccovid = open("vaccovid_api.json")
        csse = json.load(vaccovid)  # dictionary
        api_key = csse["api_key"]  # string
        headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": "vaccovid-coronavirus-vaccine-and-treatment-tracker.p.rapidapi.com"
        }

        response = requests.request("GET", url, headers=headers)
    except:
        successful = False
        st.error('VACCOVID API Response: Failed', icon="🚨")

    if successful is not False:
        st.success('VACCOVID API Response: Successful', icon="✅")
        return response.json()


def process_csse(json, array, value, user_choice):
    # Log: May implement an option to allow a user to specific a custom country.
    if(user_choice == "city"):
        for obj in json['data'][0]['region']['cities']:
            if(obj[value] is not None):
                array.append(float(obj[value]))
    elif(user_choice == "country"):
        for i in range(0, len(json['data'][0]['region']['cities'])):
            for j in range(0, len(json['data'][i]['region']['cities'])):
                if(json['data'][i]['region']['cities'][j][value] is not None):
                    array.append(
                        float(json['data'][i]['region']['cities'][j][value]))


def process_vaccovid(json, array, value):
    if value == 'date':
        for obj in json:
            array.append(str(obj[value]))
    else:
        for obj in json:
            if(obj[value] is not None):
                array.append(int(obj[value]))


def main():

    # Temporary method of storing/caching API Data into A json file. (This will reduce the amount of API calls needed.)
    # Uncomment these lines you want to store data.

    # with open("csse_data.json", "w") as write_file:
    #     json.dump(get_csse_data("country"), write_file)

    # with open("vaccovid_data.json", "w") as write_file:
    #     json.dump(get_vaccovid_data(), write_file)

    # Load json data
    # try:
    #     csse_map_data = open("csse_data.json")
    #     csse_map_data = json.load(csse_data)
    # except:
    #     st.error('Error: Failed to load CSSE API Response JSON', icon="🚨")

    # try:
    #     vaccovid_usa_data = open("vaccovid_data.json")
    #     vaccovid_usa_data = json.load(vaccovid_data)
    # except:
    #     st.error('Error: Failed to load VACCOVID API Response JSON', icon="🚨")

    # Store API Response in variables 
    csse_map_data = get_csse_data("country")
    vaccovid_usa_data = get_vaccovid_data()

    # Getting longitude and latitue for the map
    longitude, latitude = [], []

    process_csse(csse_map_data, longitude, 'long', "country")
    process_csse(csse_map_data, latitude, 'lat', "country")
    cords = np.column_stack((latitude, longitude))

    # Getting the US's past (API only returns around 29 days instead of 6 months.) of covid data.
    total_cases, total_deaths = [], []
    new_cases, new_deaths = [], []
    date = []

    process_vaccovid(vaccovid_usa_data, total_cases, 'total_cases')
    process_vaccovid(vaccovid_usa_data, total_deaths, 'total_deaths')
    process_vaccovid(vaccovid_usa_data, new_cases, 'new_cases')
    process_vaccovid(vaccovid_usa_data, new_deaths, 'new_deaths')
    process_vaccovid(vaccovid_usa_data, date, 'date')

    ###################### Streamlit ######################

    st.title("CAP 4104 Project")
    st.header("Welcome to the COVID 19 Dashboard!")

    if 1==1:
        st.warning("Note: Data may not be accurate.", icon="⚠️")

        # Table
        city_data = get_csse_data("Florida")
        st.header("COVID-19 Table:  " +
                  str(city_data['data'][0]['region']['province']))

        data_table1 = pd.DataFrame(city_data['data'][0]['region']['cities'])

        st.write(data_table1)
        st.empty()

        # Map
        st.header(
            "Data Availability Map for Table [USA]")
        df_map = pd.DataFrame(cords, columns=['latitude', 'longitude'])
        st.map(df_map)

        # Charts
        st.header("New Cases [USA]")
        
        line_chart = pd.DataFrame(new_cases)
        st.line_chart(line_chart)

        color = st.color_picker("Pick a color","#00f900")
        fig = px.line(
            line_chart,
            x = date,
            y = new_cases
        )
        fig.update_traces(line_color=color)
        st.plotly_chart(fig,use_container_width=True)
        

        st.header("New Deaths [USA]")
        bar_chart = pd.DataFrame(new_deaths)
        st.bar_chart(bar_chart)

        
        bar_chart = px.bar(bar_chart, x=date, y=new_deaths)
        if st.checkbox("Go to Bar Graph"):
            bar_chart.show()

if __name__ == '__main__':
    main()
