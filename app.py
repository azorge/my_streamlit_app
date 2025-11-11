import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from urllib.request import urlopen
import json
from copy import deepcopy


st.title("Internet Usage Worldwide (1990–2020)")
st.subheader("Percentage of Individuals Using the Internet by Country")


internet_df_raw = pd.read_csv('data/share-of-individuals-using-the-internet.csv')
internet_df = deepcopy(internet_df_raw)
with open('data/countries.geojson') as f:
    internet_json = json.load(f)

internet_df = internet_df.rename(columns={
    "Entity": "country",
    "Code": "iso_code",
    "Year": "year",
    "Individuals using the Internet (% of population)": "internet_users"
})


internet_df['year'] = internet_df['year'].astype(int)
internet_df['iso_code'] = internet_df['iso_code'].str.strip()
internet_df['internet_users'] = internet_df['internet_users'].fillna(0)
internet_df = internet_df.sort_values(['country', 'year'])



selected_countries = st.multiselect(
    'Select countries to compare:',
    internet_df['country'].unique(),
    default=['Switzerland', 'United States', 'European Union', 'China', 'India']
)

filtered_df = internet_df[internet_df['country'].isin(selected_countries)]
filtered_df = filtered_df[filtered_df['year'].between(1990, 2020)]

years = sorted(filtered_df['year'].unique())

fig = go.Figure()
for country in selected_countries:
    fig.add_trace(go.Scatter(x=[], y=[], mode='lines+markers', name=country))

# Frames for animation
frames = []
for year in years:
    data = []
    for country in selected_countries:
        country_data = filtered_df[(filtered_df['country'] == country) & (filtered_df['year'] <= year)]
        data.append(go.Scatter(
            x=country_data['year'],
            y=country_data['internet_users'],
            mode='lines+markers',
            name=country
        ))
    frames.append(go.Frame(data=data, name=str(year)))

fig.frames = frames

sliders = [dict(
    steps=[dict(method='animate',
                args=[[str(year)],
                      dict(mode='immediate', frame=dict(duration=500, redraw=True), transition=dict(duration=0))],
                label=str(year)) for year in years],
    transition=dict(duration=0),
    x=0.15,
    y=-0.1,
    currentvalue=dict(prefix="Year: "),
    len=0.8
)]

fig.update_layout(
    xaxis=dict(range=[1990, 2020], title='Year'),
    yaxis=dict(range=[0, 100], title='Internet Users (% of population)'),
    template='plotly_white',
    updatemenus=[dict(
        type="buttons",
        showactive=False,
        x=0,         
        y=-0.2,      
        xanchor="right",
        yanchor="top",
        buttons=[dict(label="Play",
                      method="animate",
                      args=[None, {"frame": {"duration": 100, "redraw": True},
                                   "fromcurrent": True, "transition": {"duration": 0}}]),
                 dict(label="Pause",
                      method="animate",
                      args=[[None], {"frame": {"duration": 0, "redraw": False},
                                     "mode": "immediate",
                                     "transition": {"duration": 0}}])]
    )],
    sliders=sliders
)


# Display the animated line chart
st.plotly_chart(fig)


# Static line chart for all countries with selected countries visible
fig_l = go.Figure()

all_countries = internet_df['country'].unique()
for country in all_countries:
    country_data = internet_df[internet_df['country'] == country]
    fig_l.add_trace(go.Scatter(
        x=country_data['year'],
        y=country_data['internet_users'],
        mode='lines+markers',
        name=country,
        visible='legendonly' if country not in selected_countries else True
    ))

fig_l.update_layout(
    title='Internet Usage Over Time (1990–2020)',
    xaxis_title='Year',
    yaxis_title='Internet Users (% of population)',
    template='plotly_white',
    height=600,
    width=1000,
    legend_title_text='Country',
    margin={"r": 40, "t": 60, "l": 40, "b": 40}
)


st.write("## Static Line Chart")

# Display the static line chart
st.plotly_chart(fig_l)


# Choropleth map for internet usage
fig = px.choropleth_map(
    internet_df[(internet_df['year'] >= 2010) & (internet_df['year'] <= 2011)],
    geojson=internet_json,
    height=800,
    locations='iso_code',
    featureidkey='properties.ISO_A3',
    color='internet_users',
    hover_name='country',
    color_continuous_scale=[[0, "white"], [1, "darkblue"]],
    range_color=(0, 100),
    animation_frame='year',
    map_style='open-street-map',
    zoom=0.5,
    center={"lat": 20, "lon": 0},
    opacity=0.7
)

fig.update_layout(margin={"r":0,"t":30,"l":0,"b":0})

st.write("## Internet Usage Worldwide on Map (2010–2011)")
st.write('only 2 years because it is slow')
st.plotly_chart(fig)
