import streamlit as st
import pandas as pd
import plotly.express as px

st.title("My Family Time Machine")
st.write("How many people live in your family's country? Let's travel back in time to the day your grandparent, "
         "your parent and YOU were born, and see how many people lived there then!")

# Step 1: load real country data (a file that comes with this app)
world_data = pd.read_csv("world_data.csv")
people_column = "Population (people)"

def say(number):                                             # write a big number in easy words
    if number >= 1_000_000_000:
        return f"{number / 1_000_000_000:.1f} billion"
    if number >= 1_000_000:
        return f"{number / 1_000_000:.1f} million"
    return f"{number:,.0f}"

# Step 2: tell the time machine about your family (our data starts in 1952)
st.subheader("Step 1: Your family")
name = st.text_input("Your name", placeholder="Type your name here") or "Explorer"
country = st.selectbox("Which country is your family from?", sorted(world_data["Country"].unique()), index=None, placeholder="Choose a country")
first, second, third = st.columns(3)
grandparent_year = first.slider("Grandparent's birth year", 1952, 2022, 1955)
parent_year = second.slider("Parent's birth year", 1952, 2022, 1985)
my_year = third.slider("Your birth year", 1952, 2022, 2012)
st.caption("Our data starts in 1952. If someone was born earlier, choose 1952.")
if country is None:
    st.info("Choose your family's country to start the time machine!")
    st.stop()                                                # wait for the country
if not grandparent_year < parent_year < my_year:
    st.warning("Check the years: your grandparent was born first, then your parent, then you!")
    st.stop()
births = {"Grandparent": grandparent_year, "Parent": parent_year, name: my_year}
people = world_data[world_data["Country"] == country].set_index("Year")[people_column]     # people in this country, for every year

# Step 3: guess first, then reveal
st.subheader("Step 2: Make a guess")
times = people[my_year] / people[grandparent_year]                  # how many times as many people?
choices = {f"Fewer people than in {grandparent_year}": (0, 0.9), "About the same number of people": (0.9, 1.5),
           "About 2 times as many people": (1.5, 2.5), "About 3 times as many people": (2.5, 3.5),
           "4 or more times as many people": (3.5, 1_000_000)}
guess = st.radio(f"In {grandparent_year}, when your grandparent was born, {country} had {say(people[grandparent_year])} people. "
                 f"How many people do you think lived in {country} in {my_year}, when {name} was born?", list(choices), index=None)
if guess is None:
    st.stop()                                                # wait for the guess
result = f"In {my_year}, {country} had {say(people[my_year])} people. That is {times:.1f} times as many as in {grandparent_year}."
low, high = choices[guess]
if low <= times < high:
    st.success("Right! " + result)
else:
    st.error("Not quite! " + result)

# Step 4: the three birthdays side by side
st.subheader("Step 3: Your family through time")
for box, (person, year) in zip(st.columns(3), births.items()):
    box.metric(f"{person}, born {year}", say(people[year]))
bars = px.bar(x=[f"{person}, born {year}" for person, year in births.items()], y=[people[year] for year in births.values()],
              text=[say(people[year]) for year in births.values()],
              labels={"x": "Family birthday", "y": f"Number of people living in {country}"})
st.plotly_chart(bars)

# Step 5: the world map for the birthday you choose
st.subheader("Step 4: The whole world on a birthday")
who = st.radio("Which birthday should the map show?", list(births), horizontal=True)
year_data = world_data[world_data["Year"] == births[who]]
world_map = px.choropleth(year_data, locations="Code", color=people_column, hover_name="Country", color_continuous_scale="Viridis")
world_map.update_layout(title=f"How many people lived in each country, in {births[who]}", height=450, margin=dict(l=0, r=0, t=50, b=0),
                        coloraxis_colorbar=dict(title="", orientation="h", y=-0.1, thickness=12, len=0.6))
st.plotly_chart(world_map)
place = year_data.set_index("Country")[people_column].rank(ascending=False)[country]
st.caption(f"Dark purple = fewer people. Bright yellow = more people. In {births[who]}, {country} was number {place:.0f} out of {len(year_data)} countries.")
