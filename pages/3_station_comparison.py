import streamlit as st
import pandas as pd
import plotly.express as px

from dashboard_utils import (
    load_aqi_data,
    add_short_station_names,
    POLLUTANT_LABELS
)


st.title("📍 Monitoring Station Comparison")

st.markdown(
    """
    Compare air-quality patterns among Bengaluru
    monitoring stations while accounting for differences
    in data availability.
    """
)


df = load_aqi_data()
df = add_short_station_names(df)

df = df[
    df["hour_start"]
    .dt.year
    .isin([2024, 2025])
].copy()


# -------------------------------------------------
# FILTERS
# -------------------------------------------------

years = [2024, 2025]

selected_years = st.sidebar.multiselect(
    "Year",
    options=years,
    default=years
)


filtered = df[
    df["hour_start"]
    .dt.year
    .isin(selected_years)
].copy()


valid = filtered[
    filtered["aqi_eligible"]
].copy()


# -------------------------------------------------
# STATION SUMMARY
# -------------------------------------------------

station_summary = (
    filtered
    .groupby(
        "station_short",
        as_index=False
    )
    .agg(
        total_hours=(
            "aqi_eligible",
            "size"
        ),
        valid_hours=(
            "aqi_eligible",
            "sum"
        ),
        mean_aqi=(
            "aqi",
            "mean"
        ),
        median_aqi=(
            "aqi",
            "median"
        ),
        maximum_aqi=(
            "aqi",
            "max"
        )
    )
)


station_summary[
    "availability_pct"
] = (
    station_summary["valid_hours"]
    /
    station_summary["total_hours"]
    * 100
)


# -------------------------------------------------
# MEAN AQI
# -------------------------------------------------

st.subheader(
    "Average AQI by Monitoring Station"
)


fig = px.bar(
    station_summary.sort_values(
        "mean_aqi"
    ),
    x="mean_aqi",
    y="station_short",
    orientation="h",
    hover_data={
        "median_aqi": ":.1f",
        "maximum_aqi": ":.0f",
        "valid_hours": ":,",
        "availability_pct": ":.1f"
    },
    title="Mean AQI by Monitoring Station"
)

fig.update_layout(
    xaxis_title="Mean AQI",
    yaxis_title="Monitoring Station"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# -------------------------------------------------
# AVAILABILITY
# -------------------------------------------------

st.subheader(
    "AQI Data Availability"
)


fig = px.bar(
    station_summary.sort_values(
        "availability_pct"
    ),
    x="availability_pct",
    y="station_short",
    orientation="h",
    title=(
        "Percentage of Station-Hours "
        "with Valid AQI"
    )
)

fig.update_layout(
    xaxis_title="Valid AQI Station-Hours (%)",
    yaxis_title="Monitoring Station"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# -------------------------------------------------
# AQI DISTRIBUTIONS
# -------------------------------------------------

st.subheader(
    "Distribution of AQI by Station"
)


fig = px.box(
    valid,
    x="aqi",
    y="station_short",
    orientation="h",
    points=False,
    title=(
        "Distribution of Valid AQI "
        "Station-Hours"
    )
)

fig.update_layout(
    xaxis_title="AQI",
    yaxis_title="Monitoring Station"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# -------------------------------------------------
# DOMINANT POLLUTANT
# -------------------------------------------------

st.subheader(
    "AQI-Determining Pollutants by Station"
)


dominant_station = (
    valid
    .groupby(
        [
            "station_short",
            "dominant_pollutant"
        ]
    )
    .size()
    .reset_index(
        name="station_hours"
    )
)


dominant_station[
    "percentage"
] = (
    dominant_station[
        "station_hours"
    ]
    /
    dominant_station
    .groupby(
        "station_short"
    )[
        "station_hours"
    ]
    .transform("sum")
    * 100
)


dominant_station[
    "Pollutant"
] = (
    dominant_station[
        "dominant_pollutant"
    ]
    .map(POLLUTANT_LABELS)
)


fig = px.bar(
    dominant_station,
    x="percentage",
    y="station_short",
    color="Pollutant",
    orientation="h",
    title=(
        "Share of AQI-Determining "
        "Pollutants by Station"
    )
)

fig.update_layout(
    xaxis_title=(
        "Share of Valid AQI "
        "Station-Hours (%)"
    ),
    yaxis_title="Monitoring Station",
    barmode="stack"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


st.caption(
    """
    Differences between stations should be interpreted
    together with data availability. Monitoring stations
    do not have identical pollutant coverage.
    """
)