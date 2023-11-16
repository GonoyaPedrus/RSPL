import pandas as pd
import requests

BASE_URL = "https://fantasy.premierleague.com/api"
response = requests.get(f"{BASE_URL}/bootstrap-static/")
data = response.json()

element_types = pd.DataFrame(data.get("element_types"))
element_types = element_types[["id", "singular_name_short"]]
element_types.rename(columns={"id": "element_type", "singular_name_short": "position"}, inplace=True)

element_types

teams = pd.DataFrame(data.get("teams"))
teams = teams[["id", "name"]]
teams.rename(columns={"id": "team", "name": "team_name"}, inplace=True)

teams

players = pd.DataFrame(data.get("elements"))
players.dropna(axis=1, how="all", inplace=True)
players = players[players.columns[players.nunique() != 1]]

players = players.merge(element_types, how="left", on="element_type")
players = players.merge(teams, how="left", on="team")

players.head()

players.drop(columns=["team", "team_code", "photo", "element_type"], inplace=True)

players.rename(columns={"team_name": "team"}, inplace=True)
players["name"] = players["first_name"] + " " + players["second_name"]
players.drop(columns=["first_name", "second_name", "code"], inplace=True)

players.head()

first_columns = ["id", "name", "now_cost", "position", "team"]

columns = list(set(players.columns.tolist()).difference(set(first_columns)))

columns = first_columns + columns
players = players[columns]

players

players.to_csv("../data/players_22_23.csv", index=False)