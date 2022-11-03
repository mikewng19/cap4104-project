# Author: Michael Wong
import streamlit as st
import pandas as pd
import numpy as np
import requests
import json
import jmespath
from datetime import datetime, timedelta


def get_csse_data(state, location_type, date):
    # Log: May implement an option to allow a user to specific a custom country.
    # API Used: https://rapidapi.com/axisbits-axisbits-default/api/covid-19-statistics/
    response = None
    error = False
    url = "https://covid-19-statistics.p.rapidapi.com/reports"

    try:
        # Load API key
        csse = open("csse_api.json")
        csse = json.load(csse)  # dictionary
        api_key = csse["api_key"]  # string

        headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": "covid-19-statistics.p.rapidapi.com"
        }
        if location_type == "state":
            querystring = {"date": str(
                date), "iso": "USA", "region_province": str(state)}
        elif location_type == "country":
            querystring = {"date": str(date), "iso": "USA"}
        response = requests.request(
            "GET", url, headers=headers, params=querystring)

    except:
        st.error('CSSE API Response: Failed', icon="🚨")
        error = True

    if not error:
        st.success('CSSE API Response: Successful', icon="✅")
        return response.json()


def get_vaccovid_data(country):
    # Log: May implement an option to allow a user to specific a custom country.
    # API Used: https://rapidapi.com/vaccovidlive-vaccovidlive-default/api/vaccovid-coronavirus-vaccine-and-treatment-tracker/
    # API only returns around 29 days instead of 6 months.
    response = None
    error = False

    url = "https://vaccovid-coronavirus-vaccine-and-treatment-tracker.p.rapidapi.com/api/covid-ovid-data/sixmonth/" + \
        str(country)

    try:
        # Load API key
        vaccovid = open("vaccovid_api.json")
        vaccovid = json.load(vaccovid)  # dictionary
        api_key = vaccovid["api_key"]  # string
        headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": "vaccovid-coronavirus-vaccine-and-treatment-tracker.p.rapidapi.com"
        }

        response = requests.request("GET", url, headers=headers)
    except:
        error = True
        st.error('VACCOVID API Response: Failed', icon="🚨")

    if not error:
        st.success('VACCOVID API Response: Successful', icon="✅")
        return response.json()


def process_csse_map(json, array, value):
    # Possbile paths for world data.
    # country = jmespath.search("data[*].region." + str(value), json)
    # cities = jmespath.search("data[*].region.cities[*]." + str(value), json)
    try:
        for i in range(0, len(json['data'])):
            for j in range(0, len(json['data'][i]['region']['cities'])):
                if(json['data'][i]['region']['cities'][j][value] is not None):
                    array.append(
                        float(json['data'][i]['region']['cities'][j][value]))
    except:
        st.error('CSSE Data Map: Failed', icon="🚨")


def process_vaccovid(json, array, value):
    if value == 'date':
        for obj in json:
            array.append(str(obj[value]))
    else:
        for obj in json:
            if(obj[value] is not None):
                array.append(int(obj[value]))


def main():
    # Date is one day behind to prevent any errors.
    search_date = datetime.today() - timedelta(days=1)
    search_date = search_date.strftime('%Y-%m-%d')

    # Call and store API response into a JSON file. (This will reduce the amount of API calls needed.)
    # with open("csse_data.json", "w") as write_file:
    #     json.dump(get_csse_data(None, "country", search_date), write_file)

    # with open("vaccovid_data.json", "w") as write_file:
    #     json.dump(get_vaccovid_data("USA"), write_file)

    # Load from Files
    try:
        csse_map_data = open("csse_data.json")
        csse_map_data = json.load(csse_map_data)
    except:
        st.error('Error: Failed to load CSSE API Response JSON', icon="🚨")

    try:
        vaccovid_usa_data = open("vaccovid_data.json")
        vaccovid_usa_data = json.load(vaccovid_usa_data)
    except:
        st.error('Error: Failed to load VACCOVID API Response JSON', icon="🚨")

    # Call and store API response in variables
    # csse_map_data = get_csse_data("USA", "", "country")
    # vaccovid_usa_data = get_vaccovid_data("USA")

    # Getting longitude and latitue for the map
    latitude, longitude = [], []

    process_csse_map(csse_map_data, latitude, 'lat')
    process_csse_map(csse_map_data, longitude, 'long')

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

    st.warning("Disclaimer: Data may be inaccurate.", icon="⚠️")
    st.info('Dates start one day behind to compensate for API update frequency.', icon="ℹ️")
    # Load list of all the states in the US. Even including Puerto Rico (US Territory).
    try:
        states = np.genfromtxt('states.csv', dtype='str', delimiter=',')
    except:
        st.error('Error: Failed to load states.txt', icon="🚨")

    # Button
    if st.button("Show API's Used"):
        st.write("COVID-19 Statistics by Axisbits:  \nhttps://rapidapi.com/axisbits-axisbits-default/api/covid-19-statistics/")
        st.write("VACCOVID - coronavirus, vaccine and treatment tracker by vaccovidlive:  \nhttps://rapidapi.com/vaccovidlive-vaccovidlive-default/api/vaccovid-coronavirus-vaccine-and-treatment-tracker/")

    # Table
    
    d = st.date_input("Select a date: ", datetime.today() - timedelta(days=1))
    option = st.selectbox ("Select a State/Territory: ", states)
    city_data = get_csse_data(option, "state", d)
    data_table1 = None

    # option = st.selectbox("Select a State", )

    try:
        st.header("COVID-19 Table:  " +
                  str(city_data['data'][0]['region']['province']))
        data_table1 = pd.DataFrame(city_data['data'][0]['region']['cities'])
    except:
        st.error('Error: No data exists for this date.', icon="🚨")
    finally:
        st.write(data_table1)

    # Map
    st.header(
        "Data Availability Map for Table [USA]")
    df_map = pd.DataFrame(cords, columns=['latitude', 'longitude'])
    st.map(df_map)

    # Charts
    st.header("New Cases [USA]")

    area_chart = pd.DataFrame(new_cases)
    st.area_chart(area_chart)

    st.header("New Deaths [USA]")
    bar_chart = pd.DataFrame(new_deaths)
    st.bar_chart(bar_chart)


if __name__ == '__main__':
    main()
