import pandas as pd
import os
from fastapi import FastAPI, Request, APIRouter, HTTPException, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
from pydantic import BaseModel
from typing import Dict
from create_team import new_saison_player, new_saison_player_index
from test_front import get_id_for_team, get_equipe
router = APIRouter()

templates = Jinja2Templates(directory="templates")
new_saison = "2023-24"
dict_index = new_saison_player_index(new_saison)
dict_player = new_saison_player(new_saison, dict_index)

def new_saison_player_index(new_saison):
    list_player = os.listdir(f"../data/{new_saison}/players")
    # map list_player for split by  and get first and second name
    dict_index = {}
    for player in list_player:
        dict_index[player.split("_")[0] + " " + player.split("_")[1]] = player.split("_")[-1]

    return dict_index


dict_index = new_saison_player_index(new_saison)


def get_id_for_team(dict_team, dict_index):
    for player in dict_team:
        for k, v in dict_index.items():
            if k == player["name"]:
                player["id"] = v
    return dict_team

def new_saison_player(new_saison, dict_index):
    df = pd.read_csv(f"../data/{new_saison}/cleaned_players.csv")
    df_2 = pd.read_csv(f"../data/{new_saison}/players_raw.csv")
    df_teams = pd.read_csv(f"../data/{new_saison}/teams.csv")
    # get a liste of player with column first_name and second_name
    list_player = df["first_name"].str.cat(df["second_name"], sep=" ").tolist()
    liste_element = df["element_type"].tolist()
    dict_player = []

    for k, v in dict_index.items():
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
@router.get("/modifier_equipe", response_class=HTMLResponse)
async def read_root(request: Request):
    # Obtenez les statistiques de la semaine pour l'équipe
    if "user_id" not in request.session:
        return {"error": "User not logged in"}
    user_id = request.session["user_id"]
    # Ouvrir la connexion à la base de données
    db_connection_team = sqlite3.connect("../database/team_database.db")
    db_cursor_team = db_connection_team.cursor()
    # requet sql
    db_cursor_team.execute(f"SELECT * FROM user_{user_id}_team ORDER BY ROWID DESC LIMIT 1;")
    row = db_cursor_team.fetchall()
    dict_team = get_id_for_team(row, dict_index)
    equipe = get_equipe(dict_team, new_saison)
    return templates.TemplateResponse("update_team.html",
                                      {"request": request, "joueurs": new_saison_player(new_saison, dict_index),
                                       "dict_team": equipe})


teams_players_dict = {}  # Dictionnaire pour stocker les associations team_id - joueur_ids

import sqlite3
from fastapi.responses import JSONResponse


@router.post("/modifier_equipe", response_class=JSONResponse)
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
    # db_connection_team.close()  # Fermer la connexion à la base de données
    # show table
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
    matching_players = [player for player in dict_player if query in player["name"].lower()]

    return matching_players
