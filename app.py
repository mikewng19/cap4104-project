# Contributors:
#   Michael Wong:
#       API requests, API response processing, Button, Table, Map, Bar Chart, Checkbox, Feedback/Info messages, Page layout")
#       [Widgets: Date selector, Selector box, Multi selector box, Color picker, Radio Button]")
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


def process_csse_map(json, array, value):
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
    # Date is two day behind to prevent any errors.
    search_date = datetime.today() - timedelta(days=2)
    search_date = search_date.strftime('%Y-%m-%d')

    # Streamlit
    st.title("CAP 4104 Project")
    st.header("Welcome to the COVID 19 Dashboard!")

    with st.expander("More info", expanded=True):
        st.warning("Disclaimer: Data may be inaccurate.", icon="⚠️")

        if st.button("View API credits and Test API Status"):
            st.write(
                "COVID-19 Statistics (CSSE) by Axisbits:  \nhttps://rapidapi.com/axisbits-axisbits-default/api/covid-19-statistics/")
            st.write("VACCOVID - coronavirus, vaccine and treatment tracker by vaccovidlive:  \nhttps://rapidapi.com/vaccovidlive-vaccovidlive-default/api/vaccovid-coronavirus-vaccine-and-treatment-tracker/")
            st.write("API Status Codes:  \nInformational responses (100 – 199)  \nSuccessful responses (200 – 299)  \nRedirection messages (300 – 399)  \nClient error responses (400 – 499)  \nServer error responses (500 – 599)")

            csse_test = get_csse_data(None, "country", None)
            vaccovid_test = get_vaccovid_data("USA")
            del csse_test, vaccovid_test

        # Load list of all the states in the US. Even including Puerto Rico (US Territory).
        try:
            states = np.genfromtxt('states.csv', dtype='str', delimiter=',')
        except:
            st.error('Error: Failed to load states.txt', icon="🚨")

    tab1, tab2, tab3, tab4 = st.tabs(["Table", "Map", "Charts", "Credits"])

    # Table
    with tab1:
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
    with tab2:
        # Getting longitude and latitue for the map
        csse_map_data = get_csse_data(None, "country", None)

        latitude, longitude = [], []
        process_csse_map(csse_map_data, latitude, 'lat')
        process_csse_map(csse_map_data, longitude, 'long')

        cords = np.column_stack((latitude, longitude))
        st.header(
            "Data Availability Map")
        df_map = pd.DataFrame(cords, columns=['latitude', 'longitude'])
        st.map(df_map)

    # Charts
    with tab3:
        # Getting the US's past (API only returns around 29 days instead of 6 months.) of covid data.
        total_cases, total_deaths = [], []

        vaccovid_usa_data = get_vaccovid_data("USA")

        process_vaccovid(vaccovid_usa_data, total_cases, 'total_cases')
        process_vaccovid(vaccovid_usa_data, total_deaths, 'total_deaths')

        vaccovid_usa_data = pd.DataFrame(vaccovid_usa_data)

        row_1, row_2 = st.columns((2))

        with row_1:
            st.header(" Total Cases [USA]: " + str(max(total_cases)))
        with row_2:
            st.header(" Total Deaths [USA]: " + str(max(total_deaths)))

        st.warning(
            "Note: Vaccovid API is currently returning 28 days of data instead of 6 months of data!", icon="⚠️")

        # Line chart
        if st.checkbox("Show Area Chart", value=True):
            st.header("Line chart [USA]")

            line_chart_options = st.multiselect(
                'Select data to display on the area chart', ['new_cases', 'new_deaths'])

            color_cases = st.color_picker(
                "Select color for new cases", '#FFFF00')
            color_deaths = st.color_picker(
                "Select color for new deaths", '#FF4B4B')

            fig = px.line(
                vaccovid_usa_data,
                x='date',
                y=line_chart_options,
                color_discrete_map={
                    'new_cases': color_deaths,
                    'new_deaths': color_cases

                }
            )
            st.plotly_chart(fig, use_container_width=True)
            if st.button("Open line chart in a new window"):

                fig.show()

        # Bar chart
        if st.checkbox("Show Bar Chart", value=True):
            st.header("Bar chart [USA]")

            bar_chart_options = st.radio('Select data to display on the bar chart',
                                         ['new_deaths', 'new_cases'])
            color_bar = st.color_picker("Pick a color", "#FF4B4B")

            fig_bar = px.bar(vaccovid_usa_data, x='date', y=bar_chart_options)
            fig_bar.update_traces(marker_color=color_bar)
            st.plotly_chart(fig_bar, use_container_width=True)

            if st.button("Open Bar chart in a new window"):
                fig_bar.show()
    # Credits
    with tab4:
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


if __name__ == '__main__':
    main()