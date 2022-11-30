# Contributors:
#   Michael Wong:
#       API requests, API response processing, Button, Table, Map, Bar Chart, Checkbox, Feedback/Info messages, Page layout
#       [Widgets: Date selector, Selector box, Multi selector box, Color picker, Radio Button]
#
#   Roberto Luna-Garcia:
#       Line chart [Widgets: Color picker]
#
#   Jenniffer Hierro Cruz:
#       Feedback/Info messages [Widget: Radio Button]

import streamlit as st
import pandas as pd
import numpy as np
import requests
import json
import plotly.express as px
import jmespath
from datetime import datetime, timedelta

st.set_page_config(layout="wide", page_title="CAP 4104: Project #2")

@st.cache(suppress_st_warning=True)
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
        try:
            error = True
            st.error("CSSE API Response: " +
                     str(response.status_code), icon="🚨")
        except:
            error = True
            st.error(
                "CSSE API Response: API may be down or unresponsive.", icon="🚨")

    if not error:
        st.info("CSSE API Response: " + str(response.status_code), icon="ℹ️")
        return response.json()

@st.cache(suppress_st_warning=True)
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
        try:
            error = True
            st.error("VACCOVID API Response: " +
                     str(response.status_code), icon="🚨")
        except:
            error = True
            st.error(
                "VACCOVID API Response: API may be down or unresponsive.", icon="🚨")

    if not error:
        st.info("VACCOVID API Response: " +
                str(response.status_code), icon="ℹ️")
        return response.json()

def process_csse_map_data(json, array, value):
    # Possbile paths for getting data if jmsepath is used.
    # country = jmespath.search("data[*].region." + str(value), json)
    # cities = jmespath.search("data[*].region.cities[*]." + str(value), json)
    try:
        for i in range(0, len(json["data"])):
            for j in range(0, len(json["data"][i]["region"]["cities"])):
                if(json["data"][i]["region"]["cities"][j][value] is not None):
                    array.append(
                        float(json["data"][i]["region"]["cities"][j][value]))
    except:
        st.error("CSSE Map Data: Failed to process data.", icon="🚨")

def process_vaccovid_data(json, array, value):
    try:
        for obj in json:
            if(obj[value] is not None):
                array.append(int(obj[value]))
    except:
        st.error("Vaccovid Data: Failed to process data.", icon="🚨")

def display_info_tab():
    # Info tab
    with st.expander("More info", expanded=True):
        st.warning("Disclaimer: Data may be inaccurate.", icon="⚠️")

        # Radio button
        if st.radio(
            "Have you been recently affected by COVID 19?",
                ("Yes", "No"), index=(1)) == "Yes":
            st.write(
                "If you or anyone you know has been affected, please folllow CDC guidelines and measures below.")
            # Info box
            st.info("Click here to see the CDC website: https://www.cdc.gov/coronavirus/2019-ncov/if-you-are-sick/steps-when-sick.html", icon="ℹ️")

def display_table():
    data_table1 = None

    # Load list of all the states in the US. Even including Puerto Rico (US Territory).
    try:
        states = np.genfromtxt("states.csv", dtype="str", delimiter=",")
    except:
        st.error("Error: Failed to load states.txt", icon="🚨")

    with st.expander("Show Selection Options", expanded=True):
        st.info(
            "The API refreshes at certian times: The starting date is set 2 days behind to prevent errors. The starting date may still be invalid.", icon="ℹ️")
        date = st.date_input("Select a date: ",
                                datetime.today() - timedelta(days=2))

        state_option = st.selectbox("Select a State/Territory: ", states)

    city_data = get_csse_data(state_option, "state", date)

    try:
        st.info(
            "Table data source: COVID-19 Statistics (CSSE) by Axisbits", icon="ℹ️")
        st.header("Showing results for:  " +
                    str(city_data["data"][0]["region"]["province"]) + "'s Cities")

        data_table1 = pd.DataFrame(
            city_data["data"][0]["region"]["cities"])
    except:
        st.error("Error: No data exists for this date.", icon="🚨")
    finally:
        # Prevents displaying a small "None" text if no data exists."
        if data_table1 is not None:
            st.table(data_table1)  

def display_map():
    try:
        # Getting longitude and latitue for the map
        csse_map_data = get_csse_data(None, "country", None)

        latitude, longitude = [], []
        process_csse_map_data(csse_map_data, latitude, "lat")
        process_csse_map_data(csse_map_data, longitude, "long")
        cords = np.column_stack((latitude, longitude))

        st.header("Data Availability Map")

        with st.expander("Show Map Source and Info", expanded=True):
            st.info(
                "Map data source: COVID-19 Statistics (CSSE) by Axisbits", icon="ℹ️")
            st.info(
                "This map displays the data availability for the table.", icon="ℹ️")

        df_map = pd.DataFrame(cords, columns=["latitude", "longitude"])
        st.map(df_map)
    except:
        st.error("Error: Failed to process and display data. CSSE API may be experiencing issues.", icon="🚨")

def display_charts():
    # Getting the US"s past (API only returns around 29 days instead of 6 months.) of covid data.
    try:
        total_cases, total_deaths = [], []

        vaccovid_usa_data = get_vaccovid_data("USA")

        process_vaccovid_data(
            vaccovid_usa_data, total_cases, "total_cases")
        process_vaccovid_data(
            vaccovid_usa_data, total_deaths, "total_deaths")

        vaccovid_usa_data = pd.DataFrame(vaccovid_usa_data)

        with st.expander("Show Chart Source and Info", expanded=True):
            st.info(
                "Chart data source: VACCOVID - coronavirus, vaccine and treatment tracker by vaccovidlive", icon="ℹ️")
            st.warning(
                "Note: Vaccovid API may not be working as intended (Normal Response: Past 6 months of data).", icon="⚠️")

        cases_column, death_columns = st.columns((2))
        with cases_column:
            st.header("Total Cases [USA]: " + str(max(total_cases)))
        with death_columns:
            st.header("Total Deaths [USA]: " + str(max(total_deaths)))

        # Line chart
        # Using checkbox to show/hide chart instead of expanders due to issues stated below.
        if st.checkbox("Show Line Chart", value=True):
            st.header("Line chart [USA]")

            # Using expander instead of checkbox here due to checkboxes requiring variables to be initialized outside the if statement,
            # causing graphs not to show properly.
            with st.expander("Show Selection Options", expanded=True):
                line_chart_options = st.multiselect(
                    "Select data to display on the area chart", ["new_cases", "new_deaths"], default="new_cases")

                color_cases = st.color_picker(
                    "Select a color for new_cases", "#FFFF00")
                color_deaths = st.color_picker(
                    "Select a color for new_deaths", "#FF4B4B")

            fig = px.line(
                vaccovid_usa_data,
                x="date",
                y=line_chart_options,
                color_discrete_map={
                    "new_cases": color_cases,
                    "new_deaths": color_deaths
                }
            )
            st.plotly_chart(fig, use_container_width=True)

            # Allows a user to open chart in a new window
            if st.button("Open line chart in a new window"):
                fig.show()

        # Bar chart
        # Using checkbox to show/hide chart instead of expanders due to issues stated below.
        if st.checkbox("Show Bar Chart", value=True):
            st.header("Bar chart [USA]")

            # Using expander instead of checkbox here due to checkboxes requiring variables to be initialized outside the if statement,
            # causing graphs not to show properly.
            with st.expander("Show Selection Options", expanded=True):
                bar_chart_options = st.radio("Select data to display on the bar chart",
                                                ["new_cases", "new_deaths"], horizontal=True)
                color_bar = st.color_picker(
                    "Select a color for the bar chart", "#FF4B4B")

            fig_bar = px.bar(vaccovid_usa_data, x="date",
                                y=bar_chart_options)
            fig_bar.update_traces(marker_color=color_bar)

            st.plotly_chart(fig_bar, use_container_width=True)

            # Allows a user to open chart in a new window
            if st.button("Open bar chart in a new window"):
                fig_bar.show()
    except:
        st.error(
            "Error: Failed to process and display data. VACCOVID API may be experiencing issues.", icon="🚨")

def display_credits():
    with st.expander("Show Team", expanded=True):
        st.header("Team:")
        st.subheader(
            "Jenniffer Hierro Cruz: Feedback/Info messages [Widget: Radio Button]")
        st.subheader(
            "Roberto Luna-Garcia: Line chart [Widgets: Color picker]")
        st.subheader(
            "Michael Wong: API requests, API response processing, Button, Table, Map, Bar Chart, Checkbox, Feedback/Info messages, Page layout")
        st.subheader(
            "[Widgets: Date selector, Selector box, Multi selector box, Color picker, Radio Button]")
    with st.expander("Show API Credits", expanded=True):
        st.header("API's Used:")
        st.subheader(
            "[Table and Map]:  \nCOVID-19 Statistics (CSSE) by Axisbits:  \nhttps://rapidapi.com/axisbits-axisbits-default/api/covid-19-statistics/")
        st.subheader("[Charts]:  \nVACCOVID - coronavirus, vaccine and treatment tracker by vaccovidlive:  \nhttps://rapidapi.com/vaccovidlive-vaccovidlive-default/api/vaccovid-coronavirus-vaccine-and-treatment-tracker/")

        if st.button("Test API Status"):
            st.write("API Status Codes:  \nInformational responses (100 – 199)  \nSuccessful responses (200 – 299)  \nRedirection messages (300 – 399)  \nClient error responses (400 – 499)  \nServer error responses (500 – 599)")

            csse_test = get_csse_data(None, "country", None)
            vaccovid_test = get_vaccovid_data("USA")
            del csse_test, vaccovid_test

def main():
    # Streamlit
    st.title("CAP 4104 Project #2")
    st.header("Welcome to the COVID-19 Dashboard!")

    #Info tab shows in every Organization tab.
    display_info_tab()

    # Organization tabs
    table_tab, map_tab, charts_tab, credits_tab = st.tabs(
        ["Table", "Map", "Charts", "Credits"])

    # Table
    with table_tab:
        display_table()

    # Map
    with map_tab:
        display_map()

    # Charts
    with charts_tab:
       display_charts()

    # Credits
    with credits_tab:
        display_credits()

if __name__ == "__main__":
    main()
