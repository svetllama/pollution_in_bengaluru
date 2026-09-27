import streamlit as st
import pandas as pd
import plotly.express as px

from dashboard_utils import (
    load_aqi_data,
    add_short_station_names,
    POLLUTANT_LABELS
)


st.title("🧪 Pollutant Explorer")

st.markdown(
    """
    Explore individual pollutant concentrations and
    relationships among pollutants using hourly
    monitoring data.
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
    col
    for col in [
        "pm25",
        "pm10",
        "no2",
        "so2",
        "co",
        "o3",
        "nh3"
    ]
    if col in df.columns
]


# -------------------------------------------------
# FILTERS
# -------------------------------------------------

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


selected_pollutant = st.sidebar.selectbox(
    "Pollutant",
    options=POLLUTANTS,
    format_func=lambda x:
        POLLUTANT_LABELS.get(x, x)
)


filtered = df[
    df["station_short"]
    .isin(selected_stations)
].copy()


# -------------------------------------------------
# TIME SERIES
# -------------------------------------------------

st.subheader(
    "Pollutant Concentration Over Time"
)


daily = (
    filtered
    .set_index("hour_start")
    .groupby(
        "station_short"
    )[selected_pollutant]
    .resample("D")
    .mean()
    .reset_index()
)


fig = px.line(
    daily,
    x="hour_start",
    y=selected_pollutant,
    color="station_short",
    title=(
        f"Daily Mean "
        f"{POLLUTANT_LABELS.get(selected_pollutant)} "
        f"Concentration"
    )
)

fig.update_layout(
    xaxis_title="Date",
    yaxis_title=(
        POLLUTANT_LABELS.get(
            selected_pollutant,
            selected_pollutant
        )
    ),
    legend_title="Station"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# -------------------------------------------------
# STATION DISTRIBUTION
# -------------------------------------------------

st.subheader(
    "Concentration Distribution by Station"
)


fig = px.box(
    filtered,
    x=selected_pollutant,
    y="station_short",
    orientation="h",
    points=False,
    title=(
        f"Distribution of "
        f"{POLLUTANT_LABELS.get(selected_pollutant)}"
    )
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# -------------------------------------------------
# CORRELATION
# -------------------------------------------------

st.subheader(
    "Relationships Among Pollutants"
)


corr = (
    filtered[
        POLLUTANTS
    ]
    .corr(
        method="spearman",
        min_periods=100
    )
)


fig = px.imshow(
    corr,
    text_auto=".2f",
    aspect="auto",
    labels={
        "color":
            "Spearman Correlation"
    },
    title=(
        "Spearman Correlation Among "
        "Hourly Pollutant Concentrations"
    )
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# -------------------------------------------------
# TWO-POLLUTANT EXPLORER
# -------------------------------------------------

st.subheader(
    "Two-Pollutant Relationship Explorer"
)


c1, c2 = st.columns(2)

with c1:

    x_pollutant = st.selectbox(
        "X-axis pollutant",
        POLLUTANTS,
        index=0,
        format_func=lambda x:
            POLLUTANT_LABELS.get(x, x)
    )


with c2:

    default_y = (
        1
        if len(POLLUTANTS) > 1
        else 0
    )

    y_pollutant = st.selectbox(
        "Y-axis pollutant",
        POLLUTANTS,
        index=default_y,
        format_func=lambda x:
            POLLUTANT_LABELS.get(x, x)
    )


scatter_data = (
    filtered[
        [
            x_pollutant,
            y_pollutant,
            "station_short"
        ]
    ]
    .dropna()
)


if len(scatter_data) > 20000:

    scatter_data = (
        scatter_data
        .sample(
            20000,
            random_state=42
        )
    )


fig = px.scatter(
    scatter_data,
    x=x_pollutant,
    y=y_pollutant,
    color="station_short",
    opacity=0.4,
    title=(
        f"{POLLUTANT_LABELS.get(x_pollutant)} "
        f"vs "
        f"{POLLUTANT_LABELS.get(y_pollutant)}"
    )
)

st.plotly_chart(
    fig,
    use_container_width=True
)


st.caption(
    """
    Correlation indicates statistical association and
    should not be interpreted as evidence that one
    pollutant causes another.
    """
)