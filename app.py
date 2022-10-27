import streamlit as st
import pandas as pd
import numpy as np
import requests
import json

def get_api_data(stock, days):
    # https://rapidapi.com/collection/list-of-free-apis

    # Load API key
    yahoo_api = open("yahoo_api.json")
    yahoo_api = json.load(yahoo_api)  # dictionary
    api_key = yahoo_api["api_key"]  # string

    # API Request Information
    url = "https://yahoo-finance97.p.rapidapi.com/price"

    # The user may specify the stock name and the amount of days.
    payload = "symbol="+ str(stock) + "&period=" + str(days) + "d"
    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "yahoo-finance97.p.rapidapi.com"
    }
    
    return requests.request("POST", url, data=payload, headers=headers).json()

st.title("CAP 4104 Project")
st.header("Yahoo API")

# Temporary method of storing/caching API Data into A json file. (This will reduce the amount of API calls needed.)
# with open("test.json", "w") as write_file:
#     json.dump(get_api_data("AMD", 7), write_file)

response_data = open("test.json")
response_data = json.load(response_data)
print(response_data["data"])

# Dates seem to use Epoch Unix Timestamp
data_table1 = pd.DataFrame(response_data["data"])
st.write(data_table1)