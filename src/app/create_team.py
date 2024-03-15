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
dict_team = [{'name': 'Erling Haaland', 'element_type': 'FWD', 'team': 'Man City', 'cost': 115, 'predicted_performance': 16.540115}, {'name': 'Bruno Miguel Borges Fernandes', 'element_type': 'MID', 'team': 'Man Utd', 'cost': 105, 'predicted_performance': 11.457617}, {'name': 'David De Gea Quintana', 'element_type': 'GK', 'team': 'Man Utd', 'cost': 50, 'predicted_performance': 10.829479}, {'name': 'Alisson Ramses Becker', 'element_type': 'GK', 'team': 'Liverpool', 'cost': 60, 'predicted_performance': 10.573772}, {'name': 'Bruno Borges Fernandes', 'element_type': 'MID', 'team': 'Man Utd', 'cost': 100, 'predicted_performance': 10.408141}, {'name': 'Ivan Toney', 'element_type': 'FWD', 'team': 'Brentford', 'cost': 65, 'predicted_performance': 10.241132}, {'name': 'Cody Gakpo', 'element_type': 'MID', 'team': 'Liverpool', 'cost': 80, 'predicted_performance': 9.668974}, {'name': 'James Maddison', 'element_type': 'MID', 'team': 'Leicester', 'cost': 70, 'predicted_performance': 9.51857}, {'name': 'Kaoru Mitoma', 'element_type': 'MID', 'team': 'Brighton', 'cost': 50, 'predicted_performance': 9.316569}, {'name': 'Romelu Lukaku', 'element_type': 'FWD', 'team': "Chelsea", 'cost': 90, 'predicted_performance': 9.279969}, {'name': 'Andrew Robertson', 'element_type': 'DEF', 'team': "Liverpool", 'cost': 45, 'predicted_performance': 8.692561}, {'name': 'Trent Alexander-Arnold', 'element_type': 'DEF', 'team': "Liverpool", 'cost': 45, 'predicted_performance': 8.22334}, {'name': 'Antonio Rüdiger', 'element_type': 'DEF', 'team': "Chelsea", 'cost': 60, 'predicted_performance': 8.159134}, {'name': 'Rico Henry', 'element_type': 'DEF', 'team': 'Brentford', 'cost': 45, 'predicted_performance': 7.671472}]
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
    
    data = await request.json()
    print("Data:", data)
    
    # Ouvrir la connexion à la base de données
    db_connection_team = sqlite3.connect("../database/team_database.db")
    db_cursor_team = db_connection_team.cursor()

    # Insérer les IDs des joueurs dans la table de l'équipe
    for position, ids in data.items():
        ids_str =   ', '.join(map(str, ids))
        db_cursor_team.execute(f'''
            INSERT INTO user_{user_id}_team ({position})
            VALUES (?)
        ''', (ids_str,))
    
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
