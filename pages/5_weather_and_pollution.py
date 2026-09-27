import streamlit as st
import pandas as pd
import plotly.express as px

from dashboard_utils import (
    load_aqi_data,
    add_short_station_names,
    POLLUTANT_LABELS
)


st.title("🌦️ Weather and Pollution")

st.markdown(
    """
    Explore statistical associations between
    meteorological conditions and hourly pollutant
    concentrations across Bengaluru monitoring stations.

    These relationships are descriptive and should
    not be interpreted as evidence of causation.
    """
)


# -------------------------------------------------
# LOAD DATA
# -------------------------------------------------

df = load_aqi_data()
df = add_short_station_names(df)


# -------------------------------------------------
# VARIABLES
# -------------------------------------------------

POLLUTANTS = [
    "pm25",
    "pm10",
    "no2",
    "so2",
    "co",
    "o3",
    "nh3"
]


WEATHER_LABELS = {
    "temperature":
        "Temperature (°C)",

    "relative_humidity":
        "Relative Humidity (%)",

    "wind_speed":
        "Wind Speed (m/s)",

    "rainfall":
        "Rainfall (mm)",

    "solar_radiation":
        "Solar Radiation",

    "pressure":
        "Pressure (mmHg)"
}


WEATHER_VARIABLES = list(
    WEATHER_LABELS.keys()
)


# -------------------------------------------------
# FILTERS
# -------------------------------------------------

st.sidebar.header(
    "Weather Analysis Filters"
)


stations = sorted(
    df["station_short"]
    .dropna()
    .unique()
)


selected_stations = (
    st.sidebar.multiselect(
        "Monitoring Stations",
        options=stations,
        default=stations
    )
)


years = sorted(
    df["year"]
    .dropna()
    .unique()
)


selected_years = (
    st.sidebar.multiselect(
        "Year",
        options=years,
        default=years
    )
)


pollutant = (
    st.sidebar.selectbox(
        "Pollutant",
        options=POLLUTANTS,
        format_func=lambda x:
            POLLUTANT_LABELS.get(
                x,
                x
            )
    )
)


weather_variable = (
    st.sidebar.selectbox(
        "Weather Variable",
        options=WEATHER_VARIABLES,
        format_func=lambda x:
            WEATHER_LABELS.get(
                x,
                x
            )
    )
)


filtered = df[
    df["station_short"]
    .isin(selected_stations)
    &
    df["year"]
    .isin(selected_years)
].copy()


# -------------------------------------------------
# DATA AVAILABILITY
# -------------------------------------------------

st.subheader(
    "Selected Variable Availability"
)


pollutant_available = (
    filtered[pollutant]
    .notna()
    .mean()
    * 100
)


weather_available = (
    filtered[weather_variable]
    .notna()
    .mean()
    * 100
)


paired = (
    filtered[
        [
            pollutant,
            weather_variable,
            "station_short",
            "hour_start"
        ]
    ]
    .dropna()
)


c1, c2, c3 = st.columns(3)


with c1:

    st.metric(
        (
            f"{POLLUTANT_LABELS.get(pollutant)} "
            "Availability"
        ),
        f"{pollutant_available:.1f}%"
    )


with c2:

    st.metric(
        (
            f"{WEATHER_LABELS.get(weather_variable)} "
            "Availability"
        ),
        f"{weather_available:.1f}%"
    )


with c3:

    st.metric(
        "Paired Station-Hours",
        f"{len(paired):,}"
    )


if paired.empty:

    st.warning(
        "No paired observations are available "
        "for the selected variables and filters."
    )

    st.stop()


# -------------------------------------------------
# SCATTER PLOT
# -------------------------------------------------

st.subheader(
    "Pollution–Weather Relationship"
)


scatter_data = paired.copy()


# Sampling is used only for rendering performance.
# Correlations below use the complete paired data.
if len(scatter_data) > 25000:

    scatter_data = (
        scatter_data
        .sample(
            25000,
            random_state=42
        )
    )


fig = px.scatter(
    scatter_data,
    x=weather_variable,
    y=pollutant,
    color="station_short",
    opacity=0.35,
    hover_data=[
        "hour_start"
    ],
    title=(
        f"{POLLUTANT_LABELS.get(pollutant)} "
        f"vs "
        f"{WEATHER_LABELS.get(weather_variable)}"
    )
)


fig.update_layout(
    xaxis_title=(
        WEATHER_LABELS.get(
            weather_variable
        )
    ),
    yaxis_title=(
        POLLUTANT_LABELS.get(
            pollutant
        )
    ),
    legend_title=(
        "Monitoring Station"
    )
)


st.plotly_chart(
    fig,
    use_container_width=True
)


# -------------------------------------------------
# OVERALL SPEARMAN CORRELATION
# -------------------------------------------------

st.subheader(
    "Spearman Association"
)


rho = (
    paired[
        [
            pollutant,
            weather_variable
        ]
    ]
    .corr(
        method="spearman"
    )
    .iloc[0, 1]
)


st.metric(
    "Spearman's ρ",
    f"{rho:.3f}"
)


st.caption(
    """
    Spearman correlation measures monotonic
    association. A positive value indicates that
    higher values of one variable tend to accompany
    higher values of the other; a negative value
    indicates an inverse tendency. Correlation does
    not establish causality.
    """
)


# -------------------------------------------------
# CORRELATION MATRIX
# -------------------------------------------------

st.subheader(
    "Pollutant–Weather Correlation Matrix"
)


analysis_columns = (
    POLLUTANTS
    +
    WEATHER_VARIABLES
)


corr = (
    filtered[
        analysis_columns
    ]
    .corr(
        method="spearman",
        min_periods=100
    )
)


pollution_weather_corr = (
    corr
    .loc[
        POLLUTANTS,
        WEATHER_VARIABLES
    ]
    .copy()
)


pollution_weather_corr.index = [
    POLLUTANT_LABELS.get(
        x,
        x
    )
    for x
    in pollution_weather_corr.index
]


pollution_weather_corr.columns = [
    WEATHER_LABELS.get(
        x,
        x
    )
    for x
    in pollution_weather_corr.columns
]


fig = px.imshow(
    pollution_weather_corr,
    text_auto=".2f",
    aspect="auto",
    labels={
        "x":
            "Meteorological Variable",

        "y":
            "Pollutant",

        "color":
            "Spearman ρ"
    },
    title=(
        "Spearman Correlation Between "
        "Pollutants and Weather Variables"
    )
)


st.plotly_chart(
    fig,
    use_container_width=True
)


# -------------------------------------------------
# STATION-SPECIFIC CORRELATION
# -------------------------------------------------

st.subheader(
    "Association by Monitoring Station"
)


station_correlations = []


for station, group in filtered.groupby(
    "station_short"
):

    pair = (
        group[
            [
                pollutant,
                weather_variable
            ]
        ]
        .dropna()
    )

    if len(pair) >= 100:

        station_rho = (
            pair
            .corr(
                method="spearman"
            )
            .iloc[0, 1]
        )

        station_correlations.append(
            {
                "Monitoring Station":
                    station,

                "Spearman rho":
                    station_rho,

                "Paired Hours":
                    len(pair)
            }
        )


station_corr_df = pd.DataFrame(
    station_correlations
)


if not station_corr_df.empty:

    station_corr_df = (
        station_corr_df
        .sort_values(
            "Spearman rho"
        )
    )


    fig = px.bar(
        station_corr_df,
        x="Spearman rho",
        y="Monitoring Station",
        orientation="h",
        hover_data={
            "Paired Hours": ":,"
        },
        title=(
            f"Station-Specific Association: "
            f"{POLLUTANT_LABELS.get(pollutant)} "
            f"vs "
            f"{WEATHER_LABELS.get(weather_variable)}"
        )
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


else:

    st.info(
        "Insufficient paired observations "
        "for station-specific correlations."
    )


st.info(
    """
    Meteorological conditions can affect pollutant
    dispersion, accumulation and atmospheric
    processes. However, the relationships displayed
    here are observational associations and do not
    demonstrate that a weather variable directly
    caused a change in pollutant concentration.
    """
)