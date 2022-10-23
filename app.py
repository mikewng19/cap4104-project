import streamlit as st
import pandas as pd
import numpy as np
import requests
import json

st.title("CAP 4104 Project")
st.header("Yahoo API")

yahoo_api = open("yahoo_api.json")
yahoo_api = json.load(yahoo_api)  # dictionary
api_key = yahoo_api["api_key"]  # string

# API Request Information
url = "https://yahoo-finance97.p.rapidapi.com/price"

# The payload currently requests 1d of AMD's stock data.
payload = "symbol=AMD&period=1d"
headers = {
    "content-type": "application/x-www-form-urlencoded",
    "X-RapidAPI-Key": api_key,
    "X-RapidAPI-Host": "yahoo-finance97.p.rapidapi.com"
}

# response = requests.request("POST", url, data=payload, headers=headers).json()
response = requests.request("POST", url, data=payload, headers=headers)

# print(response)
print(response.json())

#reponse["close"]
data_table1 = pd.DataFrame(response.json())
st.write(data_table1)