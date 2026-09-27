import pandas as pd
import streamlit as st
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = (
    BASE_DIR
    / "processed_data"
)

# @st.cache_data
# def load_aqi_data():

#     df = pd.read_parquet(
#         DATA_DIR /
#         "aqi_hourly_dashboard.parquet"
#     )

#     df["hour_start"] = pd.to_datetime(
#         df["hour_start"]
#     )

#     return df

@st.cache_data
def load_aqi_data():

    df = pd.read_parquet(
        DATA_DIR /
        "aqi_hourly_dashboard.parquet"
    )

    df["hour_start"] = pd.to_datetime(
        df["hour_start"]
    )

    df = df[
        df["hour_start"]
        .dt.year
        .isin([2024, 2025])
    ].copy()

    return df


# def short_station_name(name):

#     name = name.replace(
#         ", Bengaluru - KSPCB",
#         ""
#     )

#     name = name.replace(
#         ", Bengaluru - CPCB",
#         ""
#     )

#     return name

def short_station_name(name):

    if pd.isna(name):
        return name

    name = str(name)

    name = name.replace(
        ", Bengaluru - KSPCB",
        ""
    )

    name = name.replace(
        ", Bengaluru - CPCB",
        ""
    )

    return name


def add_short_station_names(df):

    df = df.copy()

    df["station_short"] = (
        df["Station Name"]
        .apply(short_station_name)
    )

    return df


AQI_CATEGORY_ORDER = [
    "Good",
    "Satisfactory",
    "Moderately Polluted",
    "Poor",
    "Very Poor",
    "Severe"
]


POLLUTANT_LABELS = {

    "pm25": "PM2.5",
    "pm10": "PM10",
    "no2": "NO₂",
    "so2": "SO₂",
    "co": "CO",
    "o3": "O₃",
    "nh3": "NH₃"
}