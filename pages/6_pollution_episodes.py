import streamlit as st
import plotly.express as px

from dashboard_utils import (
    load_aqi_data,
    add_short_station_names,
    POLLUTANT_LABELS
)


st.title("🚨 Pollution Episodes")

st.markdown(
    """
    Investigate high-AQI observations and the pollutants
    associated with the most severe monitored episodes.
    """
)


df = load_aqi_data()
df = add_short_station_names(df)

df = df[
    df["hour_start"]
    .dt.year
    .isin([2024, 2025])
].copy()


valid = df[
    df["aqi_eligible"]
].copy()


# -------------------------------------------------
# CATEGORY FILTER
# -------------------------------------------------

categories = [
    "Moderately Polluted",
    "Poor",
    "Very Poor",
    "Severe"
]


selected_categories = st.sidebar.multiselect(
    "AQI Categories",
    categories,
    default=[
        "Poor",
        "Very Poor",
        "Severe"
    ]
)


episodes = valid[
    valid["aqi_category"]
    .isin(selected_categories)
].copy()


if episodes.empty:

    st.warning(
        "No observations match the selected "
        "AQI categories."
    )

    st.stop()


# -------------------------------------------------
# KPIs
# -------------------------------------------------

c1, c2, c3, c4 = st.columns(4)


with c1:

    st.metric(
        "Selected Station-Hours",
        f"{len(episodes):,}"
    )


with c2:

    st.metric(
        "Maximum AQI",
        f"{episodes['aqi'].max():.0f}"
    )


with c3:

    st.metric(
        "Stations Affected",
        episodes[
            "station_short"
        ].nunique()
    )


with c4:

    most_common = (
        episodes[
            "dominant_pollutant"
        ]
        .mode()
        .iloc[0]
    )

    st.metric(
        "Most Frequent Driver",
        POLLUTANT_LABELS.get(
            most_common,
            most_common
        )
    )


# -------------------------------------------------
# TIMELINE
# -------------------------------------------------

fig = px.scatter(
    episodes,
    x="hour_start",
    y="aqi",
    color="aqi_category",
    hover_data=[
        "station_short",
        "dominant_pollutant"
    ],
    title=(
        "Timeline of High-AQI "
        "Station-Hour Observations"
    )
)

fig.update_layout(
    xaxis_title="Date and Time",
    yaxis_title="AQI"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# -------------------------------------------------
# STATION COUNTS
# -------------------------------------------------

station_episodes = (
    episodes[
        "station_short"
    ]
    .value_counts()
    .rename_axis(
        "Monitoring Station"
    )
    .reset_index(
        name="Station-Hours"
    )
)


fig = px.bar(
    station_episodes,
    x="Station-Hours",
    y="Monitoring Station",
    orientation="h",
    title=(
        "High-AQI Observations "
        "by Monitoring Station"
    )
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# -------------------------------------------------
# DRIVERS
# -------------------------------------------------

driver_counts = (
    episodes[
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


driver_counts["Pollutant"] = (
    driver_counts["Pollutant"]
    .map(POLLUTANT_LABELS)
)


fig = px.bar(
    driver_counts,
    x="Pollutant",
    y="Station-Hours",
    title=(
        "Pollutants Determining "
        "High-AQI Observations"
    )
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# -------------------------------------------------
# TOP OBSERVATIONS
# -------------------------------------------------

st.subheader(
    "Highest AQI Observations"
)


display_columns = [
    "hour_start",
    "station_short",
    "aqi",
    "aqi_category",
    "dominant_pollutant"
]


top_events = (
    episodes[
        display_columns
    ]
    .sort_values(
        "aqi",
        ascending=False
    )
    .head(100)
)


st.dataframe(
    top_events,
    use_container_width=True,
    hide_index=True
)


st.warning(
    """
    Extremely high observations should be interpreted
    as high-concentration episodes recorded by the
    monitoring network. Additional quality-control
    evidence would be required before attributing an
    individual extreme value to a specific emission
    event or source.
    """
)