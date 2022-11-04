# Contributors:
#   Michael Wong:
#       API requests, API response processing, Button, Table, Map, Bar Chart, Checkbox, Feedback/Info messages, Page layout
#       [Widgets: Date selector, Selector box, Multi selector box, Color picker, Radio Button]
#
#   Roberto Luna-Garcia:
#       Line chart, Button, Checkbox [Widgets: Color picker]
#
#   Jenniffer Hierro Cruz:
#       [Widget: Radio Button, Feedback/Info messages, Date selector]

import streamlit as st
import pandas as pd
import numpy as np
import requests
import json
import plotly.express as px
import jmespath
from datetime import datetime, timedelta

st.set_page_config(layout="wide", page_title="CAP 4104: Project #2")


def get_csse_data(state, location_type, date):
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
            querystring = {"iso": "USA"}

        response = requests.request(
            "GET", url, headers=headers, params=querystring)
    except:
        st.error("CSSE API Response: " + str(response.status_code), icon="🚨")
        error = True

    if not error:
        st.success("CSSE API Response: " + str(response.status_code), icon="✅")
        return response.json()


def get_vaccovid_data(country):
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
        st.error("VACCOVID API Response: " +
                 str(response.status_code), icon="🚨")

    if not error:
        st.success("VACCOVID API Response: " +
                   str(response.status_code), icon="✅")
        return response.json()


def process_csse_map_data(json, array, value):
    # Possbile paths for getting data if jmsepath is used.
    # country = jmespath.search("data[*].region." + str(value), json)
    # cities = jmespath.search("data[*].region.cities[*]." + str(value), json)
    try:
        for i in range(0, len(json['data'])):
            for j in range(0, len(json['data'][i]['region']['cities'])):
                if(json['data'][i]['region']['cities'][j][value] is not None):
                    array.append(
                        float(json['data'][i]['region']['cities'][j][value]))
    except:
        st.error('CSSE Map Data: Failed to process data.', icon="🚨")


def process_vaccovid_data(json, array, value):
    try:
        for obj in json:
            if(obj[value] is not None):
                array.append(int(obj[value]))
    except:
        st.error('Vaccovid Data: Failed to process data.', icon="🚨")


def main():
    # Date is two day behind to prevent any errors.
    search_date = datetime.today() - timedelta(days=2)
    search_date = search_date.strftime('%Y-%m-%d')

    # Streamlit
    st.title("CAP 4104 Project")
    st.header("Welcome to the COVID 19 Dashboard!")

    # Info tab
    with st.expander("More info", expanded=True):
        st.warning("Disclaimer: Data may be inaccurate.", icon="⚠️")

        #radio button
        option = st.radio( 
        'Have you been recently affected by COVID 19?',
        ('Yes', 'No', 'Already had COVID'))

     #Here's what to do if you been affected:
        if option == 'Yes':
            st.write("If you or anyone you know has been affected, please folllow CDC guidelines and measures below.")

        #Info box
            st.info('Click here to see the CDC website: https://www.cdc.gov/coronavirus/2019-ncov/if-you-are-sick/steps-when-sick.html', icon="ℹ️")

        else:
            st.info('Click here to see the CDC website: https://www.cdc.gov/coronavirus/2019-ncov/if-you-are-sick/steps-when-sick.html', icon="ℹ️")

        # Load list of all the states in the US. Even including Puerto Rico (US Territory).
        try:
            states = np.genfromtxt('states.csv', dtype='str', delimiter=',')
        except:
            st.error('Error: Failed to load states.txt', icon="🚨")

    table_tab, map_tab, charts_tab, credits_tab = st.tabs(
        ["Table", "Map", "Charts", "Credits"])

    # Table
    with table_tab:
        st.info(
            'The API refreshes at certian times: The starting date is set 2 days behind to prevent errors. The starting date may still be invalid.', icon="ℹ️")
        data_table1 = None

        d = st.date_input("Select a date: ",
                          datetime.today() - timedelta(days=2))
        option = st.selectbox("Select a State/Territory: ", states)
        city_data = get_csse_data(option, "state", d)

        try:
            st.header("Showing results for:  " +
                      str(city_data['data'][0]['region']['province']) + "'s Cities")
            data_table1 = pd.DataFrame(
                city_data['data'][0]['region']['cities'])
        except:
            st.error('Error: No data exists for this date.', icon="🚨")
        finally:
            # Prevents displaying a small "None" text if no data exists."
            if data_table1 is not None:
                st.table(data_table1)

    # Map
    with map_tab:
        # Getting longitude and latitue for the map
        csse_map_data = get_csse_data(None, "country", None)

        latitude, longitude = [], []
        process_csse_map_data(csse_map_data, latitude, 'lat')
        process_csse_map_data(csse_map_data, longitude, 'long')

        cords = np.column_stack((latitude, longitude))
        st.header(
            "Data Availability Map")
        df_map = pd.DataFrame(cords, columns=['latitude', 'longitude'])
        st.map(df_map)

    # Charts
    with charts_tab:
        # Getting the US's past (API only returns around 29 days instead of 6 months.) of covid data.
        total_cases, total_deaths = [], []

        vaccovid_usa_data = get_vaccovid_data("USA")

        process_vaccovid_data(vaccovid_usa_data, total_cases, 'total_cases')
        process_vaccovid_data(vaccovid_usa_data, total_deaths, 'total_deaths')

        vaccovid_usa_data = pd.DataFrame(vaccovid_usa_data)

        cases_column, death_columns = st.columns((2))

        with cases_column:
            st.header("Total Cases [USA]: " + str(max(total_cases)))
        with death_columns:
            st.header("Total Deaths [USA]: " + str(max(total_deaths)))

        st.warning(
            "Note: Vaccovid API may not be working as intended (Normal Response: Past 6 months of data).", icon="⚠️")

        # Line chart
        if st.checkbox("Show Area Chart", value=True):
            st.header("Line chart [USA]")

            line_chart_options = st.multiselect(
                'Select data to display on the area chart', ['new_cases', 'new_deaths'], default='new_cases')

            color_cases = st.color_picker(
                "Select a color for new_cases", '#FFFF00')
            color_deaths = st.color_picker(
                "Select a color for new_deaths", '#FF4B4B')

            fig = px.line(
                vaccovid_usa_data,
                x='date',
                y=line_chart_options,
                color_discrete_map={
                    'new_cases': color_cases,
                    'new_deaths': color_deaths

                }
            )
            st.plotly_chart(fig, use_container_width=True)
            if st.button("Open line chart in a new window"):

                fig.show()

        # Bar chart
        if st.checkbox("Show Bar Chart", value=True):
            st.header("Bar chart [USA]")

            bar_chart_options = st.radio('Select data to display on the bar chart',
                                         ['new_cases', 'new_deaths'])
            color_bar = st.color_picker(
                "Select a color for the bar chart", "#FF4B4B")

            fig_bar = px.bar(vaccovid_usa_data, x='date', y=bar_chart_options)
            fig_bar.update_traces(marker_color=color_bar)

            st.plotly_chart(fig_bar, use_container_width=True)

            if st.button("Open Bar chart in a new window"):
                fig_bar.show()

    # Credits
    with credits_tab:
        st.header("Team:")
        st.subheader(
            "Jenniffer Hierro Cruz: [Widget: Radio Button, Feedback/Info messages, Date selector]  \n")
        st.subheader(
            "Roberto Luna-Garcia: Line chart, Button, Checkbox [Widgets: Color picker]")
        st.subheader(
            "Michael Wong: API requests, API response processing, Button, Table, Map, Bar Chart, Checkbox, Feedback/Info messages, Page layout")
        st.subheader(
            "[Widgets: Date selector, Selector box, Multi selector box, Color picker, Radio Button]")

        st.header("API's Used:")
        st.subheader(
            "COVID-19 Statistics (CSSE) by Axisbits:  \nhttps://rapidapi.com/axisbits-axisbits-default/api/covid-19-statistics/")
        st.subheader("VACCOVID - coronavirus, vaccine and treatment tracker by vaccovidlive:  \nhttps://rapidapi.com/vaccovidlive-vaccovidlive-default/api/vaccovid-coronavirus-vaccine-and-treatment-tracker/")

        if st.button("Test API Status"):
            st.write("API Status Codes:  \nInformational responses (100 – 199)  \nSuccessful responses (200 – 299)  \nRedirection messages (300 – 399)  \nClient error responses (400 – 499)  \nServer error responses (500 – 599)")

            csse_test = get_csse_data(None, "country", None)
            vaccovid_test = get_vaccovid_data("USA")
            del csse_test, vaccovid_test


if __name__ == '__main__':
    main()