import streamlit as st
import pandas as pd
import plotly.express as px

from dashboard_utils import (
    load_aqi_data,
    add_short_station_names,
    POLLUTANT_LABELS
)


st.title("🔍 Data Quality and Methodology")

st.markdown(
    """
    Air-quality monitoring datasets frequently contain
    differences in station coverage and pollutant
    availability. This page makes those limitations
    visible rather than hiding them through imputation.
    """
)


df = load_aqi_data()
df = add_short_station_names(df)

df = df[
    df["hour_start"]
    .dt.year
    .isin([2024, 2025])
].copy()


POLLUTANTS = [
    c
    for c in [
        "pm25",
        "pm10",
        "no2",
        "so2",
        "co",
        "o3",
        "nh3"
    ]
    if c in df.columns
]


# -------------------------------------------------
# OVERALL DATASET
# -------------------------------------------------

st.subheader(
    "Dataset Summary"
)


c1, c2, c3, c4 = st.columns(4)


with c1:

    st.metric(
        "Hourly Station Records",
        f"{len(df):,}"
    )


with c2:

    st.metric(
        "Monitoring Stations",
        df[
            "station_short"
        ].nunique()
    )


with c3:

    st.metric(
        "Valid AQI Station-Hours",
        f"{df['aqi_eligible'].sum():,.0f}"
    )


with c4:

    availability = (
        df["aqi_eligible"]
        .mean()
        * 100
    )

    st.metric(
        "AQI Availability",
        f"{availability:.1f}%"
    )


# -------------------------------------------------
# AQI AVAILABILITY BY STATION
# -------------------------------------------------

st.subheader(
    "AQI Availability by Station"
)


station_availability = (
    df
    .groupby(
        "station_short"
    )
    ["aqi_eligible"]
    .agg(
        total_hours="size",
        valid_hours="sum"
    )
    .reset_index()
)


station_availability[
    "availability_pct"
] = (
    station_availability[
        "valid_hours"
    ]
    /
    station_availability[
        "total_hours"
    ]
    * 100
)


fig = px.bar(
    station_availability
    .sort_values(
        "availability_pct"
    ),
    x="availability_pct",
    y="station_short",
    orientation="h",
    title=(
        "Valid AQI Availability "
        "by Monitoring Station"
    )
)

fig.update_layout(
    xaxis_title="Availability (%)",
    yaxis_title="Monitoring Station"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# -------------------------------------------------
# POLLUTANT AVAILABILITY
# -------------------------------------------------

st.subheader(
    "Pollutant Availability by Station"
)


records = []


for station, group in df.groupby(
    "station_short"
):

    for pollutant in POLLUTANTS:

        availability = (
            group[pollutant]
            .notna()
            .mean()
            * 100
        )

        records.append(
            {
                "station_short":
                    station,

                "pollutant":
                    POLLUTANT_LABELS.get(
                        pollutant,
                        pollutant
                    ),

                "availability_pct":
                    availability
            }
        )


availability_df = pd.DataFrame(
    records
)


availability_matrix = (
    availability_df
    .pivot(
        index="station_short",
        columns="pollutant",
        values="availability_pct"
    )
)


fig = px.imshow(
    availability_matrix,
    text_auto=".0f",
    aspect="auto",
    labels={
        "x": "Pollutant",
        "y": "Monitoring Station",
        "color": "Availability (%)"
    },
    title=(
        "Hourly Pollutant Data "
        "Availability (%)"
    )
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# -------------------------------------------------
# METHODOLOGY
# -------------------------------------------------

st.subheader(
    "Methodological Notes"
)


st.markdown(
    """
    **Temporal handling**

    Original timestamps were supplied in UTC and were
    converted to Indian Standard Time before deriving
    local hour, date, month and year.

    **Missing values**

    Missing pollutant measurements were retained as
    missing rather than being replaced with mean or
    median values. This prevents artificial pollution
    observations from being introduced into the data.

    **Aggregation**

    The original monitoring data have a 15-minute
    resolution. Hourly analytical values were derived
    from available observations and measurement counts
    were retained where required for completeness
    assessment.

    **AQI**

    AQI is derived from pollutant measurements using
    the CPCB National Air Quality Index framework.
    AQI availability therefore depends on the
    availability of the required pollutant information.

    **Interpretation**

    Results represent measurements at the included
    monitoring stations. They should not be interpreted
    as continuous measurements covering every location
    in Bengaluru.
    """
)