import streamlit as st
import pandas as pd
import numpy as np
import requests
import json

def get_api_data(day):
    # Load API key
    yahoo_api = open("yahoo_api.json")
    yahoo_api = json.load(yahoo_api)  # dictionary
    api_key = yahoo_api["api_key"]  # string

    # https://rapidapi.com/collection/list-of-free-apis
    # API Request Information
    url = "https://yahoo-finance97.p.rapidapi.com/price"

    # The payload currently requests 1d of AMD's stock data.
    payload = "symbol=AMD&period=" + str(day) + "d"
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
#     json.dump(get_api_data(7), write_file)

response_data = open("test.json")
response_data = json.load(response_data)
print(response_data["data"])

# data_table1 = pd.DataFrame(close)
# st.write(data_table1)