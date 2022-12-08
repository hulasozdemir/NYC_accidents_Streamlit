import streamlit as st
import pandas as pd
import numpy as np
import os
import pydeck as pdk
import plotly.express as px


current_dir = os.getcwd()

data_location = (current_dir + "/data/Motor_Vehicle_Collisions_-_Crashes.csv")

st.title("Motor Vehicle Collisions in New York City")
st.markdown("This application is a streamlit dashboard that can be used to analyze motor vehicle colliosns in NYC.")


column_subset = ['CRASH DATE', 
				'CRASH TIME', 
				'BOROUGH',
				'LATITUDE',
       			'LONGITUDE',
       			'NUMBER OF PERSONS INJURED',
       			'NUMBER OF PERSONS KILLED', 
       			'NUMBER OF PEDESTRIANS INJURED',
       			'NUMBER OF PEDESTRIANS KILLED', 
       			'NUMBER OF CYCLIST INJURED',
       			'NUMBER OF CYCLIST KILLED', 
       			'NUMBER OF MOTORIST INJURED',
       			'NUMBER OF MOTORIST KILLED']


@st.cache(persist=True)
def preproessing(frac = 0.1):
	data = pd.read_csv(data_location, usecols = column_subset, parse_dates = [["CRASH DATE", "CRASH TIME"]])
	data = data.sample(frac=frac)
	data = data.dropna(subset = ['LATITUDE', 'LONGITUDE'])
	data = data.rename(columns={"LATITUDE": "lat", "LONGITUDE": "lon"}) #st.map looks for column with names "lat" and "lon"
	return data

data = preproessing()

st.header("Where are the most people injured in NYC?")
injured_people = st.slider("Number of persons injured", 0, int(data["NUMBER OF PERSONS INJURED"].max(axis=0)))
data_queried =  data.query("`NUMBER OF PERSONS INJURED` >= @injured_people")
st.map(data_queried[["lat","lon"]]) # Pick incidents with min

if st.checkbox("Show Raw Data", False):
	st.subheader("Raw Data")
	st.write(data_queried)



st.header("How many collisions occur during a given time of day?")
hour = st.sidebar.slider("Hour to look at", 0, 23)
data_hour_filter = data.loc[data["CRASH DATE_CRASH TIME"].dt.hour == hour]
midpoint = (data['lat'].median(),data['lon'].median())


st.markdown(f"Vehicle collisions between {hour} and {hour+1}")

st.write(pdk.Deck(
	initial_view_state = {
						"latitude": midpoint[0], 
						"longitude": midpoint[1],
						"zoom": 11,
						"pitch": 50
						},
	layers = [
			pdk.Layer(
				"HexagonLayer", 
				data = data_hour_filter[["CRASH DATE_CRASH TIME", "lat", "lon"]],
				get_position = ["lon","lat"],
				radius = 200,
				extruded = True,
				pickable = True,
				elevation_scale = 4,
				elevation_rate = [0,100],
				),
	],
	)
)

st.subheader(f"Breakdown by minute between {hour} and {hour+1}.")
filtered_by_minute_by_hour = data[(data["CRASH DATE_CRASH TIME"].dt.hour >= hour) & (data["CRASH DATE_CRASH TIME"].dt.hour < (hour+1))]
hist = np.histogram(filtered_by_minute_by_hour["CRASH DATE_CRASH TIME"].dt.minute, bins = 60)[0]


chart_data = pd.DataFrame({'minute': range(60), 'crashes': hist})
fig = px.bar(chart_data, x = "minute", y = "crashes", hover_data = ['minute','crashes'])
st.write(fig)

 

if st.checkbox("Show Raw Data by Hour", False):
	st.subheader("Raw Data Filtered by Hour")
	st.write(data_hour_filter)






