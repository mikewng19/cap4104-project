import streamlit as st
import pandas as pd
import numpy as np
import requests
import json
import datetime


def get_api_data(stock, days):
    # https://rapidapi.com/collection/list-of-free-apis

    # Load API key
    yahoo_api = open("yahoo_api.json")
    yahoo_api = json.load(yahoo_api)  # dictionary
    api_key = yahoo_api["api_key"]  # string

    # API Request Information
    url = "https://yahoo-finance97.p.rapidapi.com/price"

    # The user may specify the stock name and the amount of days.
    payload = "symbol=" + str(stock) + "&period=" + str(days) + "d"
    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "yahoo-finance97.p.rapidapi.com"
    }

    return requests.request("POST", url, data=payload, headers=headers).json()


def process_data(json, array, value):
    # Currently unused
    # response_length = (len(response_data['data'][0]) - 1)
    # print("JSON Length: ", response_length)

    # Example of getting data
    # for close in response_data['data']:
    #     close_values.append(float(close['Close']))

    # Converting Epoch to Datetime is not working.
    # Seems like the int 'epoch' isn't being passed before the datetime function is being called
    # causing OSError: [Errno 22] Invalid argument
    # Possible fix: pandas has a way to convert epoch to datetime. Haven't tried it out yet.

    # if value == 'Date':
    #     for i in json['data']:
    #         epoch = int(i[value])
    #         date = datetime.datetime.fromtimestamp(epoch).strftime('%Y-%m-%d')
    #         array.append(date)
    # else:
    for i in json['data']:
        array.append(float(i[value]))


def main():
    # U.S. markets, regular trading sessions run from 9:30 a.m. to 4:00 p.m. Eastern
    # Temporary method of storing/caching API Data into A json file. (This will reduce the amount of API calls needed.)
    # with open("test.json", "w") as write_file:
    #     json.dump(get_api_data("AMD", 7), write_file)

    response_data = open("test.json")
    response_data = json.load(response_data)

    # Example of accessing data:
    # response_data['data'][0]['Close']
    # Storing response data in arrays.
    close_values, open_values = [], []
    high_values, low_values = [], []
    date_values = []

    process_data(response_data, close_values, 'Close')
    process_data(response_data, open_values, 'Open')
    process_data(response_data, high_values, 'High')
    process_data(response_data, low_values, 'Low')
    process_data(response_data, date_values, 'Date')

    print(date_values)

    # Streamlit
    st.title("CAP 4104 Project")
    st.header("Yahoo API")

    # Dates seem to use Epoch Unix Timestamp
    data_table1 = pd.DataFrame(response_data['data'])
    st.write(data_table1)

    # st.line_chart()


if __name__ == '__main__':
    main()
