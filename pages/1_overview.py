import streamlit as st
import pandas as pd
import plotly.express as px

from dashboard_utils import (load_aqi_data, add_short_station_names, AQI_CATEGORY_ORDER, POLLUTANT_LABELS)

st.title("📊 Air Quality Overview")


df = load_aqi_data()
df = add_short_station_names(df)

# Restrict dashboard to the defined
# local-time study period: 2024–2025

df = df[
    df["hour_start"]
    .dt.year
    .isin([2024, 2025])
].copy()

# -------------------------------------------------
# SIDEBAR FILTERS
# -------------------------------------------------

st.sidebar.header(
    "Filters"
)


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

years = sorted(
    df["hour_start"]
    .dt.year
    .unique()
)

selected_years = st.sidebar.multiselect(
    "Year",
    options=years,
    default=years
)

min_date = (
    df["hour_start"]
    .dt.date
    .min()
)

max_date = (
    df["hour_start"]
    .dt.date
    .max()
)


selected_dates = st.sidebar.date_input(
    "Date Range",
    value=(
        min_date,
        max_date
    ),
    min_value=min_date,
    max_value=max_date
)

# years = sorted(
#     df["hour_start"]
#     .dt.year
#     .unique()
# )


# selected_years = st.sidebar.multiselect(
#     "Year",
#     options=years,
#     default=years
# )

filtered = df[
    df["station_short"]
    .isin(selected_stations)
    &
    df["hour_start"]
    .dt.year
    .isin(selected_years)
].copy()


if len(selected_dates) == 2:

    start_date, end_date = selected_dates

    filtered = filtered[
        (
            filtered["hour_start"]
            .dt.date
            >= start_date
        )
        &
        (
            filtered["hour_start"]
            .dt.date
            <= end_date
        )
    ].copy()

# filtered = df[
#     df["station_short"]
#     .isin(selected_stations)
#     &
#     df["hour_start"]
#     .dt.year
#     .isin(selected_years)
# ].copy()


valid = filtered[
    filtered["aqi_eligible"]
].copy()

if valid.empty:

    st.warning(
        "No valid AQI observations are available "
        "for the selected filters."
    )

    st.stop()

# c1, c2, c3, c4, c5 = st.columns(5)

c1, c2, c3, c4, c5, c6 = st.columns(6)

availability_pct = (
    filtered["aqi_eligible"].mean()
    * 100
)


# with c1:

#     st.metric(
#         "Valid AQI Station-Hours",
#         f"{len(valid):,}"
#     )


# with c2:

#     st.metric(
#         "Mean AQI",
#         f"{valid['aqi'].mean():.1f}"
#     )


# with c3:

#     st.metric(
#         "Median AQI",
#         f"{valid['aqi'].median():.0f}"
#     )


# with c4:

#     st.metric(
#         "Stations",
#         valid["station_short"].nunique()
#     )


# with c5:

#     dominant = (
#         valid["dominant_pollutant"]
#         .mode()
#         .iloc[0]
#     )

#     st.metric(
#         "Most Frequent AQI Driver",
#         POLLUTANT_LABELS.get(
#             dominant,
#             dominant
#         )
#     )
with c1:

    st.metric(
        "Valid AQI Station-Hours",
        f"{len(valid):,}"
    )


with c2:

    st.metric(
        "AQI Availability",
        f"{availability_pct:.1f}%"
    )


with c3:

    st.metric(
        "Mean AQI",
        f"{valid['aqi'].mean():.1f}"
    )


with c4:

    st.metric(
        "Median AQI",
        f"{valid['aqi'].median():.0f}"
    )


with c5:

    st.metric(
        "Stations",
        valid["station_short"].nunique()
    )


with c6:

    dominant = (
        valid["dominant_pollutant"]
        .mode()
        .iloc[0]
    )

    st.metric(
        "Most Frequent AQI Driver",
        POLLUTANT_LABELS.get(
            dominant,
            dominant
        )
    )

category_df = (
    valid["aqi_category"]
    .value_counts()
    .reindex(
        AQI_CATEGORY_ORDER,
        fill_value=0
    )
    .rename_axis(
        "AQI Category"
    )
    .reset_index(
        name="Hours"
    )
)


category_df["Percentage"] = (
    category_df["Hours"]
    / category_df["Hours"].sum()
    * 100
)

fig_category = px.bar(
    category_df,
    x="AQI Category",
    y="Hours",
    text="Percentage",
    title="Distribution of Valid AQI Observations",
    category_orders={
        "AQI Category":
            AQI_CATEGORY_ORDER
    }
)


fig_category.update_traces(
    texttemplate="%{text:.1f}%",
    textposition="outside"
)


fig_category.update_layout(
    xaxis_title="AQI Category",
    yaxis_title="Station-Hours"
)


st.plotly_chart(
    fig_category,
    use_container_width=True
)

valid["month"] = (
    valid["hour_start"]
    .dt.month
)

valid["month_name"] = (
    valid["hour_start"]
    .dt.month_name()
)


monthly = (
    valid
    .groupby(
        ["month", "month_name"],
        as_index=False
    )
    .agg(
        mean_aqi=("aqi", "mean"),
        median_aqi=("aqi", "median"),
        valid_hours=("aqi", "size")
    )
    .sort_values("month")
)

fig_month = px.line(
    monthly,
    x="month_name",
    y="mean_aqi",
    markers=True,
    hover_data=[
        "median_aqi",
        "valid_hours"
    ],
    title="Mean AQI by Month"
)


fig_month.update_layout(
    xaxis_title="Month",
    yaxis_title="Mean AQI"
)


st.plotly_chart(
    fig_month,
    use_container_width=True
)

dominant_df = (
    valid[
        "dominant_pollutant"
    ]
    .value_counts()
    .rename_axis(
        "Pollutant"
    )
    .reset_index(
        name="Station-Hours"
    )
)


dominant_df["Percentage"] = (
    dominant_df["Station-Hours"]
    / dominant_df["Station-Hours"].sum()
    * 100
)


dominant_df["Pollutant"] = (
    dominant_df["Pollutant"]
    .map(POLLUTANT_LABELS)
)

fig_dominant = px.bar(
    dominant_df,
    x="Pollutant",
    y="Percentage",
    text="Percentage",
    title=(
        "Pollutants Most Frequently "
        "Determining AQI"
    )
)


fig_dominant.update_traces(
    texttemplate="%{text:.1f}%",
    textposition="outside"
)


fig_dominant.update_layout(
    yaxis_title=(
        "Share of Valid AQI "
        "Station-Hours (%)"
    )
)


st.plotly_chart(
    fig_dominant,
    use_container_width=True
)

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
        )
    )
)


station_summary[
    "AQI Availability (%)"
] = (
    station_summary[
        "valid_hours"
    ]
    /
    station_summary[
        "total_hours"
    ]
    * 100
)

fig_station = px.bar(
    station_summary.sort_values(
        "mean_aqi"
    ),
    x="mean_aqi",
    y="station_short",
    orientation="h",
    hover_data={
        "median_aqi": ":.1f",
        "valid_hours": ":,",
        "AQI Availability (%)": ":.1f"
    },
    title=(
        "Mean Calculated AQI "
        "by Monitoring Station"
    )
)


fig_station.update_layout(
    xaxis_title="Mean AQI",
    yaxis_title="Monitoring Station"
)


st.plotly_chart(
    fig_station,
    use_container_width=True
)

st.subheader(
    "Key Observations"
)


dominant_pollutant = (
    dominant_df
    .sort_values(
        "Percentage",
        ascending=False
    )
    .iloc[0]
)


lowest_month = (
    monthly
    .sort_values(
        "mean_aqi"
    )
    .iloc[0]
)


highest_month = (
    monthly
    .sort_values(
        "mean_aqi",
        ascending=False
    )
    .iloc[0]
)


st.markdown(
    f"""
    - **{dominant_pollutant['Pollutant']}**
      was the most frequent pollutant determining
      calculated AQI, accounting for approximately
      **{dominant_pollutant['Percentage']:.1f}%**
      of valid station-hour observations.

    - Mean AQI was lowest in
      **{lowest_month['month_name']}**
      ({lowest_month['mean_aqi']:.1f})
      and highest in
      **{highest_month['month_name']}**
      ({highest_month['mean_aqi']:.1f})
      for the currently selected data.

    - Results describe the included monitoring
      stations and available observations;
      they should not be interpreted as continuous
      measurements of every location in Bengaluru.
    """
)

