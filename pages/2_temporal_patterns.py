import streamlit as st
import pandas as pd
import plotly.express as px

from dashboard_utils import (
    load_aqi_data,
    add_short_station_names
)


st.title("📅 Temporal Patterns")

st.markdown(
    """
    This page examines how calculated AQI varies across
    years, months, days of the week and hours of the day.
    """
)


# -------------------------------------------------
# LOAD DATA
# -------------------------------------------------

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

st.sidebar.header("Temporal Filters")

stations = sorted(
    df["station_short"]
    .dropna()
    .unique()
)

selected_stations = st.sidebar.multiselect(
    "Monitoring Stations",
    options=stations,
    default=stations
)

years = [2024, 2025]

selected_years = st.sidebar.multiselect(
    "Year",
    options=years,
    default=years
)


filtered = df[
    df["station_short"].isin(
        selected_stations
    )
    &
    df["hour_start"]
    .dt.year
    .isin(selected_years)
].copy()


valid = filtered[
    filtered["aqi_eligible"]
].copy()


if valid.empty:
    st.warning(
        "No valid AQI observations are available "
        "for the selected filters."
    )
    st.stop()


# -------------------------------------------------
# TEMPORAL VARIABLES
# -------------------------------------------------

valid["year"] = (
    valid["hour_start"]
    .dt.year
)

valid["month"] = (
    valid["hour_start"]
    .dt.month
)

valid["month_name"] = (
    valid["hour_start"]
    .dt.month_name()
)

valid["hour"] = (
    valid["hour_start"]
    .dt.hour
)

valid["weekday"] = (
    valid["hour_start"]
    .dt.day_name()
)


MONTH_ORDER = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December"
]


WEEKDAY_ORDER = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday"
]


# -------------------------------------------------
# YEAR × MONTH
# -------------------------------------------------

st.subheader(
    "Monthly AQI: 2024 vs 2025"
)


monthly_year = (
    valid
    .groupby(
        [
            "year",
            "month",
            "month_name"
        ],
        as_index=False
    )
    .agg(
        mean_aqi=("aqi", "mean"),
        median_aqi=("aqi", "median"),
        valid_hours=("aqi", "size")
    )
    .sort_values(
        ["year", "month"]
    )
)


fig = px.line(
    monthly_year,
    x="month_name",
    y="mean_aqi",
    color="year",
    markers=True,
    hover_data={
        "median_aqi": ":.1f",
        "valid_hours": ":,"
    },
    category_orders={
        "month_name": MONTH_ORDER
    },
    title=(
        "Monthly Mean of Hourly Running AQI "
        "by Year"
    )
)

fig.update_layout(
    xaxis_title="Month",
    yaxis_title="Mean AQI",
    legend_title="Year"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


st.caption(
    """
    Values represent station-hour observations pooled
    across the selected monitoring stations. They should
    not be interpreted as a single city-wide AQI.
    """
)


# -------------------------------------------------
# HOURLY PATTERN
# -------------------------------------------------

st.subheader(
    "Typical Hour-of-Day Pattern"
)


hourly_pattern = (
    valid
    .groupby(
        "hour",
        as_index=False
    )
    .agg(
        mean_aqi=("aqi", "mean"),
        median_aqi=("aqi", "median"),
        valid_hours=("aqi", "size")
    )
)


fig = px.line(
    hourly_pattern,
    x="hour",
    y="mean_aqi",
    markers=True,
    hover_data=[
        "median_aqi",
        "valid_hours"
    ],
    title=(
        "Mean AQI by Hour of Day "
        "(Indian Standard Time)"
    )
)

fig.update_layout(
    xaxis_title="Hour of Day (IST)",
    yaxis_title="Mean AQI"
)

fig.update_xaxes(
    dtick=1
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# -------------------------------------------------
# WEEKDAY PATTERN
# -------------------------------------------------

st.subheader(
    "Day-of-Week Pattern"
)


weekday = (
    valid
    .groupby(
        "weekday",
        as_index=False
    )
    .agg(
        mean_aqi=("aqi", "mean"),
        median_aqi=("aqi", "median"),
        valid_hours=("aqi", "size")
    )
)


weekday["weekday"] = pd.Categorical(
    weekday["weekday"],
    categories=WEEKDAY_ORDER,
    ordered=True
)

weekday = weekday.sort_values(
    "weekday"
)


fig = px.bar(
    weekday,
    x="weekday",
    y="mean_aqi",
    hover_data=[
        "median_aqi",
        "valid_hours"
    ],
    title="Mean AQI by Day of Week"
)

fig.update_layout(
    xaxis_title="Day of Week",
    yaxis_title="Mean AQI"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# -------------------------------------------------
# WEEKDAY × HOUR HEATMAP
# -------------------------------------------------

st.subheader(
    "Weekday × Hour Pattern"
)


heatmap_df = (
    valid
    .groupby(
        [
            "weekday",
            "hour"
        ],
        as_index=False
    )
    .agg(
        mean_aqi=("aqi", "mean")
    )
)


heatmap_df["weekday"] = pd.Categorical(
    heatmap_df["weekday"],
    categories=WEEKDAY_ORDER,
    ordered=True
)


heatmap_pivot = (
    heatmap_df
    .pivot(
        index="weekday",
        columns="hour",
        values="mean_aqi"
    )
    .reindex(
        WEEKDAY_ORDER
    )
)


fig = px.imshow(
    heatmap_pivot,
    aspect="auto",
    labels={
        "x": "Hour of Day (IST)",
        "y": "Day of Week",
        "color": "Mean AQI"
    },
    title=(
        "Mean AQI by Day of Week "
        "and Hour of Day"
    )
)

st.plotly_chart(
    fig,
    use_container_width=True
)