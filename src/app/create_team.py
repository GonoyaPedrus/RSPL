import pandas as pd 
import os 
from fastapi import FastAPI, Request, APIRouter, HTTPException, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
from pydantic import BaseModel
from typing import Dict

router = APIRouter()

templates = Jinja2Templates(directory="templates") 
new_saison = "2023-24"
dict_team = [{'name': 'Kai Havertz',
  'element_type': 'MID',
  'team': 'Arsenal',
  'cost': 71,
  'predicted_performance': 19.310514668537042},
 {'name': 'Phil Foden',
  'element_type': 'MID',
  'team': 'Man City',
  'cost': 81,
  'predicted_performance': 19.248851617795275},
 {'name': 'Rodrigo Muniz Carvalho',
  'element_type': 'FWD',
  'team': 'Fulham',
  'cost': 45,
  'predicted_performance': 16.305604342547653},
 {'name': 'Harry Wilson',
  'element_type': 'MID',
  'team': 'Fulham',
  'cost': 53,
  'predicted_performance': 16.221667231488183},
 {'name': 'Timo Werner',
  'element_type': 'FWD',
  'team': 'Spurs',
  'cost': 63,
  'predicted_performance': 15.942504463894986},
 {'name': 'Martin Ødegaard',
  'element_type': 'MID',
  'team': 'Arsenal',
  'cost': 85,
  'predicted_performance': 15.890662428901994},
 {'name': 'Edson Álvarez Velázquez',
  'element_type': 'MID',
  'team': 'West Ham',
  'cost': 50,
  'predicted_performance': 15.73184482872646},
 {'name': 'Ollie Watkins',
  'element_type': 'FWD',
  'team': 'Aston Villa',
  'cost': 89,
  'predicted_performance': 15.271087737945109},
 {'name': 'Mads Roerslev Rasmussen',
  'element_type': 'DEF',
  'team': 'Brentford',
  'cost': 44,
  'predicted_performance': 14.026874342855244},
 {'name': 'Benjamin White',
  'element_type': 'DEF',
  'team': 'Arsenal',
  'cost': 56,
  'predicted_performance': 12.656241324713791},
 {'name': 'Cristian Romero',
  'element_type': 'DEF',
  'team': 'Spurs',
  'cost': 49,
  'predicted_performance': 11.461738925893238},
 {'name': 'Axel Disasi',
  'element_type': 'DEF',
  'team': 'Chelsea',
  'cost': 49,
  'predicted_performance': 11.447518012425016},
 {'name': 'Fabian Schär',
  'element_type': 'DEF',
  'team': 'Newcastle',
  'cost': 54,
  'predicted_performance': 10.76548614686531},
 {'name': 'Alphonse Areola',
  'element_type': 'GK',
  'team': 'West Ham',
  'cost': 42,
  'predicted_performance': 9.913099371946307},
 {'name': 'Caoimhin Kelleher',
  'element_type': 'GK',
  'team': 'Liverpool',
  'cost': 37,
  'predicted_performance': 8.669551933556857}]
def new_saison_player_index(new_saison):
    list_player = os.listdir(f"../data/{new_saison}/players")
    #map list_player for split by  and get first and second name
    dict_index = {}
    for player in list_player:
        dict_index[player.split("_")[0] + " " + player.split("_")[1]] = player.split("_")[-1]

    return dict_index
dict_index = new_saison_player_index(new_saison)

def get_id_for_team(dict_team,dict_index):
    for player in dict_team:
        for k,v in dict_index.items():
            if k == player["name"]:
                player["id"] = v
    return dict_team
dict_team = get_id_for_team(dict_team,dict_index)

def new_saison_player(new_saison,dict_index):
    df = pd.read_csv(f"../data/{new_saison}/cleaned_players.csv")
    df_2 = pd.read_csv(f"../data/{new_saison}/players_raw.csv")
    df_teams = pd.read_csv(f"../data/{new_saison}/teams.csv")
    #get a liste of player with column first_name and second_name
    list_player = df["first_name"].str.cat(df["second_name"], sep=" ").tolist()
    liste_element = df["element_type"].tolist()
    dict_player = []

    for k,v in dict_index.items():
        if k in list_player:
            dict_tmp = {}
            dict_tmp["Name"] = k
            dict_tmp["id"] = v
            dict_tmp["element_type"] = liste_element[list_player.index(k)]
            df_tmp_2 = df_2[(df_2["id"] == int(v))]
            dict_tmp["cost"] = df_tmp_2["now_cost"].values[0]
            df_tmp_3 = df_teams[(df_teams["id"] == int(df_tmp_2["team"].values[0]))]
            dict_tmp["team"] = df_tmp_3["name"].values[0]
            dict_tmp["predicted_performance"] = 0
            # add v in dict_player["id"]
            dict_player.append(dict_tmp)
    return dict_player

# Route principale pour afficher la page HTML
@router.get("/create_team", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("create_team.html", {"request": request, "joueurs": new_saison_player(new_saison,dict_index),"dict_team":dict_team})


teams_players_dict = {}  # Dictionnaire pour stocker les associations team_id - joueur_ids

import sqlite3
from fastapi.responses import JSONResponse

@router.post("/create_team", response_class=JSONResponse)
async def save_team(request: Request): 
    if "user_id" not in request.session:
        return {"error": "User not logged in"}
    
    user_id = request.session["user_id"]
    print("ok")
    data = await request.json()
    print("Data:", data)
    print(data)
    # Ouvrir la connexion à la base de données
    db_connection_team = sqlite3.connect("../database/team_database.db")
    db_cursor_team = db_connection_team.cursor()

    # Concaténer les listes d'identifiants pour chaque element_type en une seule chaîne
    fwd_ids = ', '.join(data["FWD"])
    mid_ids = ', '.join(data["MID"])
    def_ids = ', '.join(data["DEF"])
    gk_ids = ', '.join(data["GK"])

    # Insérer les tuples d'IDs des joueurs dans la table de l'équipe
    db_cursor_team.execute(f'''
        INSERT INTO user_{user_id}_team (FWD, MID, DEF, GK)
        VALUES (?, ?, ?, ?)
    ''', (fwd_ids, mid_ids, def_ids, gk_ids))
    db_connection_team.commit()  # Valider les changements dans la base de données
    #db_connection_team.close()  # Fermer la connexion à la base de données
    #show table
    db_cursor_team.execute(f"SELECT * FROM user_{user_id}_team")
    rows = db_cursor_team.fetchall()
    print(rows)
    


    return {"message": "Team saved successfully"}


@router.get("/search", response_class=JSONResponse)
async def search_players(request: Request, query: str):
    if not query:
        return {"error": "Empty search query"}

    # Convertir la requête de recherche en minuscules pour une recherche insensible à la casse
    query = query.lower()

    # Filtrer les joueurs dont le nom contient le terme de recherche
    matching_players = [player for player in dict_team if query in player["Name"].lower()]

    return matching_players
