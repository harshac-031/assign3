import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Me vs My Friend: Two Countries, One Story")
st.write("Pick your country and a friend's country. See how each one changed from 1952 to 2022, "
         "and how they compare with the rest of the world.")

# Step 1: load real country data (a file that comes with this app)
world_data = pd.read_csv("world_data.csv")

# What each number means, in plain words: (short phrase, label for the charts)
meanings = {
    "Life expectancy (years)": ("the number of years a newborn baby could expect to live", "Years a newborn baby could expect to live"),
    "Money per person (GDP, US dollars)": ("the yearly money earned by the average person (US dollars)", "Money earned per person in a year (US dollars)"),
    "Population (people)": ("the number of people living", "Number of people living there"),
}

# Step 2: the student's choices
indicator_name = st.selectbox("What should we compare?", list(meanings))
meaning_of_number, chart_label = meanings[indicator_name]
st.caption(f"This number means: {meaning_of_number}.")

all_countries = sorted(world_data["Country"].unique())
left_choice, right_choice = st.columns(2)
country_one = left_choice.selectbox("Your country", all_countries, index=0)
country_two = right_choice.selectbox("Your friend's country", all_countries, index=1)
if country_one == country_two:
    st.warning("Pick two different countries to compare!")
    st.stop()                                                # wait until the student picks two different countries

map_year = st.slider("Which year should the map show?", 1952, 2022, 2022)

# Step 3: the world map for the chosen year (the colour shows the number)
year_data = world_data[world_data["Year"] == map_year]
world_map = px.choropleth(year_data, locations="Code", color=indicator_name, hover_name="Country",
                          color_continuous_scale="Viridis")
world_map.update_layout(title=f"{chart_label}, in the year {map_year}", height=450, margin=dict(l=0, r=0, t=50, b=0),
                        coloraxis_colorbar=dict(title="", orientation="h", y=-0.1, thickness=12, len=0.6))

# Step 4: the story of the two countries over time, next to the world average
story = pd.DataFrame({
    country_one: world_data[world_data["Country"] == country_one].set_index("Year")[indicator_name],
    country_two: world_data[world_data["Country"] == country_two].set_index("Year")[indicator_name],
    "World average": world_data.groupby("Year")[indicator_name].mean(),
}).reset_index()
story_chart = px.line(story, x="Year", y=[country_one, country_two, "World average"],
                      labels={"value": chart_label, "variable": "", "Year": "Calendar year"},
                      title=f"{country_one} and {country_two} compared with the world average")
story_chart.update_xaxes(tickformat="d")
story_chart.update_layout(height=450, legend=dict(orientation="h", y=-0.25, title_text=""))

# Step 5: show the map, and the chart under it (each one gets the full width)
st.plotly_chart(world_map)
st.plotly_chart(story_chart)

# Step 6: write the story in words, and say who changed more
st.subheader("The story in words")
changes = {}
for country in [country_one, country_two]:
    values = story[country].dropna()
    if values.empty:
        st.warning(f"We have no data on {meaning_of_number} for {country}. Try another country!")
    else:
        first_year = int(story.loc[values.index[0], "Year"])
        last_year = int(story.loc[values.index[-1], "Year"])
        changes[country] = values.iloc[-1] - values.iloc[0]
        st.write(f"**{country}:** in **{first_year}**, {meaning_of_number} was **{values.iloc[0]:,.0f}**. "
                 f"In **{last_year}** it was **{values.iloc[-1]:,.0f}**. "
                 f"That is a change of **{changes[country]:+,.0f}**.")

if len(changes) == 2:
    if changes[country_one] > changes[country_two]:
        st.success(f"{country_one} changed more than {country_two}: {changes[country_one]:+,.0f} compared with {changes[country_two]:+,.0f}.")
    elif changes[country_two] > changes[country_one]:
        st.success(f"{country_two} changed more than {country_one}: {changes[country_two]:+,.0f} compared with {changes[country_one]:+,.0f}.")
    else:
        st.success("Both countries changed by the same amount!")
