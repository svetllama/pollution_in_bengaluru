# import streamlit as st
# import pandas as pd
# import plotly.express as px
# import plotly.graph_objects as go


# st.set_page_config(
#     page_title="Breathing Bengaluru",
#     page_icon="🌬️",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )


# st.title("🌬️ Breathing Bengaluru")

# st.markdown(
#     """
#     ### Interactive Visual Analytics of Bengaluru Air Quality

#     Explore spatial and temporal variation in air pollution
#     across Bengaluru monitoring stations during 2024–2025.
#     """
# )

# @st.cache_data
# def load_data():

#     df = pd.read_parquet(
#         "processed_data/"
#         "aqi_hourly_with_cpcb_aqi.parquet"
#     )

#     return df

# df = load_data()

# st.sidebar.header(
#     "Dashboard Filters"
# )

# station_options = sorted(
#     df["Station Name"]
#     .dropna()
#     .unique()
# )

# selected_stations = (
#     st.sidebar.multiselect(
#         "Monitoring Station",
#         options=station_options,
#         default=station_options
#     )
# )

# year_options = sorted(
#     df["year"]
#     .dropna()
#     .unique()
# )

# selected_years = (
#     st.sidebar.multiselect(
#         "Year",
#         options=year_options,
#         default=year_options
#     )
# )

# min_date = (
#     df["hour_start"]
#     .dt.date
#     .min()
# )

# max_date = (
#     df["hour_start"]
#     .dt.date
#     .max()
# )

# selected_dates = (
#     st.sidebar.date_input(
#         "Date Range",
#         value=(
#             min_date,
#             max_date
#         ),
#         min_value=min_date,
#         max_value=max_date
#     )
# )

# filtered_df = df[
#     df["Station Name"]
#     .isin(selected_stations)
#     &
#     df["year"]
#     .isin(selected_years)
# ].copy()

# if len(selected_dates) == 2:

#     start_date, end_date = selected_dates

#     filtered_df = filtered_df[
#         (
#             filtered_df["hour_start"]
#             .dt.date
#             >= start_date
#         )
#         &
#         (
#             filtered_df["hour_start"]
#             .dt.date
#             <= end_date
#         )
#     ]

# valid_aqi = filtered_df[
#     filtered_df["aqi_eligible"]
# ].copy()

# col1, col2, col3, col4 = (
#     st.columns(4)
# )

# with col1:

#     st.metric(
#         "Mean AQI",
#         f"{valid_aqi['aqi'].mean():.0f}"
#     )

# with col2:

#     st.metric(
#         "Median AQI",
#         f"{valid_aqi['aqi'].median():.0f}"
#     )

# with col3:

#     st.metric(
#         "Maximum AQI",
#         f"{valid_aqi['aqi'].max():.0f}"
#     )

# with col4:

#     st.metric(
#         "Monitoring Stations",
#         valid_aqi[
#             "Station Name"
#         ].nunique()
#     )

# trend_df = (
#     valid_aqi
#     .set_index("hour_start")
#     .resample("D")["aqi"]
#     .mean()
#     .reset_index()
# )

# fig = px.line(
#     trend_df,
#     x="hour_start",
#     y="aqi",
#     title="Daily Mean of Hourly Running AQI"
# )

# fig.update_layout(
#     xaxis_title="Date",
#     yaxis_title="AQI"
# )

# st.plotly_chart(
#     fig,
#     use_container_width=True
# )

# category_counts = (
#     valid_aqi[
#         "aqi_category"
#     ]
#     .value_counts()
#     .reindex(
#         [
#             "Good",
#             "Satisfactory",
#             "Moderately Polluted",
#             "Poor",
#             "Very Poor",
#             "Severe"
#         ],
#         fill_value=0
#     )
#     .reset_index()
# )

# category_counts.columns = [
#     "AQI Category",
#     "Hours"
# ]

# fig = px.bar(
#     category_counts,
#     x="AQI Category",
#     y="Hours",
#     title="Distribution of AQI Categories"
# )

# st.plotly_chart(
#     fig,
#     use_container_width=True
# )

# dominant_df = (
#     valid_aqi[
#         "dominant_pollutant"
#     ]
#     .value_counts()
#     .reset_index()
# )

# dominant_df.columns = [
#     "Pollutant",
#     "Hours"
# ]

# fig = px.bar(
#     dominant_df,
#     x="Pollutant",
#     y="Hours",
#     title="Pollutants Most Frequently Determining AQI"
# )

# st.plotly_chart(
#     fig,
#     use_container_width=True
# )

# station_chart = (
#     valid_aqi
#     .groupby(
#         "Station Name",
#         as_index=False
#     )
#     .agg(
#         Mean_AQI=("aqi", "mean"),
#         Median_AQI=("aqi", "median"),
#         Valid_Hours=("aqi", "count")
#     )
#     .sort_values(
#         "Mean_AQI",
#         ascending=False
#     )
# )

# fig = px.bar(
#     station_chart,
#     x="Mean_AQI",
#     y="Station Name",
#     orientation="h",
#     hover_data=[
#         "Median_AQI",
#         "Valid_Hours"
#     ],
#     title="Mean AQI by Monitoring Station"
# )

# fig.update_layout(
#     yaxis={
#         "categoryorder": "total ascending"
#     }
# )

# st.plotly_chart(
#     fig,
#     use_container_width=True
# )

# import streamlit as st


# st.set_page_config(
#     page_title="Breathing Bengaluru",
#     page_icon="🌬️",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )


# st.title(
#     "🌬️ Breathing Bengaluru"
# )

# st.subheader(
#     "Interactive Visual Analytics of "
#     "Air Pollution Across Space and Time"
# )


# st.markdown(
#     """
#     This dashboard explores air-quality measurements
#     collected across Bengaluru monitoring stations
#     during 2024–2025.

#     Use the pages in the sidebar to investigate
#     temporal patterns, differences between monitoring
#     stations, pollutant relationships, meteorological
#     associations and high-pollution episodes.
#     """
# )


# st.info(
#     """
#     AQI values shown in this dashboard are calculated
#     from the available monitoring data using the
#     CPCB National Air Quality Index framework.
#     AQI is displayed only where sufficient pollutant
#     information is available.
#     """
# )

import streamlit as st


st.set_page_config(
    page_title="Breathing Bengaluru",
    page_icon="🌬️",
    layout="wide",
    initial_sidebar_state="expanded"
)


st.title("🌬️ Breathing Bengaluru")

st.subheader(
    "Interactive Visual Analytics of "
    "Air Pollution Across Space and Time"
)


st.markdown(
    """
    This dashboard explores air-quality measurements
    collected across Bengaluru monitoring stations
    during **2024–2025**.

    The analysis investigates:

    - temporal patterns in air quality,
    - differences among monitoring stations,
    - relationships among major pollutants,
    - associations between meteorological conditions
      and pollution,
    - AQI patterns and high-pollution episodes, and
    - data availability and monitoring completeness.

    Use the navigation menu to explore the different
    analytical views.
    """
)


st.divider()


st.markdown(
    """
    ### Research Question

    **How does air pollution vary across monitoring
    locations and time in Bengaluru during 2024–2025,
    and what relationships exist among major pollutants
    and meteorological conditions?**
    """
)


st.info(
    """
    AQI values displayed in this dashboard are derived
    from available monitoring measurements using the
    CPCB National Air Quality Index framework.
    Availability differs by station and pollutant,
    and these differences are considered throughout
    the analysis.
    """
)