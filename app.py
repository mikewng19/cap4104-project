# Author: Michael Wong
import streamlit as st
import pandas as pd
import numpy as np
import requests
import json


def get_csse_data(user_choice):
    # Log: May implement an option to allow a user to specific a custom country.
    # API Used: https://rapidapi.com/axisbits-axisbits-default/api/covid-19-statistics/

    # Load API key
    csse = open("csse_api.json")
    csse = json.load(csse)  # dictionary
    api_key = csse["api_key"]  # string

    url = "https://covid-19-statistics.p.rapidapi.com/reports"

    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "covid-19-statistics.p.rapidapi.com"
    }

    if(user_choice == "country"):
        querystring = {"region_name": "US", "iso": "USA"}
    else:
        try:
            querystring = {"q": "US " + str(user_choice), "region_name": "US", "iso": "USA"}
        except ValueError:
            print("Oops!  State does not exist.")

    return requests.request("GET", url, headers=headers, params=querystring).json()


def get_vaccovid_data():
    # Log: May implement an option to allow a user to specific a custom country.
    # API Used: https://rapidapi.com/vaccovidlive-vaccovidlive-default/api/vaccovid-coronavirus-vaccine-and-treatment-tracker/
    vaccovid = open("vaccovid_api.json")
    csse = json.load(vaccovid)  # dictionary
    api_key = csse["api_key"]  # string
    # API only returns around 29 days instead of 6 months.
    url = "https://vaccovid-coronavirus-vaccine-and-treatment-tracker.p.rapidapi.com/api/covid-ovid-data/sixmonth/USA"

    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "vaccovid-coronavirus-vaccine-and-treatment-tracker.p.rapidapi.com"
    }

    return requests.request("GET", url, headers=headers).json()


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
    # with open("csse_data.json", "w") as write_file:
    #     json.dump(get_csse_data("country"), write_file)

    # with open("vaccovid_data.json", "w") as write_file:
    #     json.dump(get_vaccovid_data(), write_file)

    # Load json data
    csse_data = open("csse_data.json")
    csse_data = json.load(csse_data)

    vaccovid_data = open("vaccovid_data.json")
    vaccovid_data = json.load(vaccovid_data)

    # Getting longitude and latitue for the map
    longitude, latitude = [], []

    process_csse(csse_data, longitude, 'long', "country")
    process_csse(csse_data, latitude, 'lat', "country")
    cords = np.column_stack((latitude, longitude))

    # Getting the US's past (API only returns around 29 days instead of 6 months.) of covid data.
    total_cases, total_deaths = [], []
    new_cases, new_deaths = [], []
    date = []

    process_vaccovid(vaccovid_data, total_cases, 'total_cases')
    process_vaccovid(vaccovid_data, total_deaths, 'total_deaths')
    process_vaccovid(vaccovid_data, new_cases, 'new_cases')
    process_vaccovid(vaccovid_data, date, 'date')

    ###################### Streamlit ######################
    st.title("CAP 4104 Project")
    st.header("COVID-19 Dashboard")

    # Table
    
    # City data test
    city_data = get_csse_data("Florida")
    st.header("COVID-19 Table:  " +
              str(city_data['data'][0]['region']['province']))

    # data_table1 = pd.DataFrame(csse_data['data'])

    data_table1 = pd.DataFrame(city_data['data'][0]['region']['cities'])
    st.write(data_table1)

    # Map
    st.header(
        "Data Availability Map for Table [USA]")
    df_map = pd.DataFrame(cords, columns=['latitude', 'longitude'])
    st.map(df_map)

    # Charts
    st.header("New Cases [USA]")

    df_chart1 = pd.DataFrame(new_cases)
    st.line_chart(df_chart1)


if __name__ == '__main__':
    main()
