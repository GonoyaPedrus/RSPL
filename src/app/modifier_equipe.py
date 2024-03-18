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

top_players = pd.read_csv("../data/2023-24/top_players.csv")
top_players.rename(columns={'position': 'element_type'}, inplace=True)
top_players.rename(columns={'now_cost': 'cost'}, inplace=True)

def new_saison_player_index(new_saison):
    list_player = os.listdir(f"../data/{new_saison}/players")
    #map list_player for split by  and get first and second name
    dict_index = {}
    for player in list_player:
        dict_index[player.split("_")[0] + " " + player.split("_")[1]] = player.split("_")[-1]

    return dict_index
def new_saison_player(new_saison,dict_index):
    df = pd.read_csv(f"../data/{new_saison}/cleaned_players.csv")
    df_2 = pd.read_csv(f"../data/{new_saison}/players_raw.csv")
    df_teams = pd.read_csv(f"../data/{new_saison}/teams.csv")
    #get a liste of player with column first_name and second_name
    list_player = top_players["name"].tolist()
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
            dict_tmp["predicted_performance"] = top_players["predicted_performance"][(top_players["name"] == k)].values[0]
            # add v in dict_player["id"]
            dict_player.append(dict_tmp)
    return dict_player

templates = Jinja2Templates(directory="templates")
new_saison = "2023-24"
dict_index = new_saison_player_index(new_saison)
dict_player = new_saison_player(new_saison, dict_index)
def get_weeks_of_player(dict_index,player,id, new_saison):

    try :

        df = pd.read_csv(f"../data/{new_saison}/players/{dict_index[id]}/gw.csv")
        return df
    except:
        print("player not in list")
        print(player)
        return False

def get_stats_player(week_num,dict_id_name,dict_team, new_saison):
    dict_stats = {}
    df_id  = pd.read_csv(f"../data/{new_saison}/player_idlist.csv")
    df_name = pd.read_csv(f"../data/{new_saison}/players_raw.csv")
    df_team = pd.read_csv(f"../data/{new_saison}/teams.csv")
    df_position = pd.read_csv(f"../data/{new_saison}/cleaned_players.csv")
    list_all_player = df_position["first_name"].str.cat(df_position["second_name"], sep=" ").tolist()
    liste_element = df_position["element_type"].tolist()
    list_player = list(dict_team.keys())
    for player,id in dict_team.items():

        df = get_weeks_of_player(dict_id_name,player,id, new_saison)

        if df is not False:
            df_tmp = df_id[df_id["id"] == int(id)]
            first_name = df_tmp["first_name"].values[0]
            second_name = df_tmp["second_name"].values[0]
            df_tmp_2 = df_name[(df_name["first_name"] == first_name) & (df_name["second_name"] == second_name)]
            id_team = df_tmp_2["team"].values[0]
            team = df_team[df_team["id"] == id_team]["name"].values[0]
            dict_stats[player] = [df["total_points"].iloc[:week_num+1].tolist(),df["value"].iloc[:week_num+1].tolist(),liste_element[list_all_player.index(player)],team]

        else:
            return False
    return dict_stats
def get_equipe(dict_team, new_saison):
    print("getting team")
    df_id = pd.read_csv(f"../data/{new_saison}/player_idlist.csv")
    list_player = os.listdir(f"../data/{new_saison}/players")
    df = pd.read_csv(f"../data/{new_saison}/players_raw.csv")
    df_team = pd.read_csv(f"../data/{new_saison}/teams.csv")

    df_position = pd.read_csv(f"../data/{new_saison}/cleaned_players.csv")
    list_player = df_position["first_name"].str.cat(df_position["second_name"], sep=" ").tolist()
    liste_element = df_position["element_type"].tolist()
    print(df_team.columns)
    equipe = []
    for k, v in dict_team.items():
        dict_tmp = {}

        player_id = v

        df_tmp = df_id[df_id["id"] == int(player_id)]
        first_name = df_tmp["first_name"].values[0]
        second_name = df_tmp["second_name"].values[0]
        dict_tmp["name"] = k
        dict_tmp["element_type"] = liste_element[list_player.index(k)]
        dict_tmp["id"] = player_id
        # get row of df where first_name and second_name are equal to first_name and second_name
        df_tmp_2 = df[(df["first_name"] == first_name) & (df["second_name"] == second_name)]
        id_team = df_tmp_2["team"].values[0]
        dict_tmp["team"] = df_team[df_team["id"] == id_team]["name"].values[0]
        dict_tmp["cost"] = df_tmp_2["cost"].values[0]

        equipe.append(dict_tmp)

    return equipe
def get_id_for_team(table_row, dict_index):
    dict_team = {}
    for ids_tuple in table_row:
        for ids in ids_tuple:
            id_list = ids.split(', ')  # Diviser la chaîne d'IDs en une liste
            for id in id_list:
                for ids, player in dict_index.items():
                    if id == ids:
                        # Ajouter le nom du joueur correspondant à l'ID à la liste
                        name = player.split("_")[0] + " " + player.split("_")[1]
                        dict_team[name] = id  # Ajouter l'ID à la liste correspondante dans le dictionnaire

                        # Associer la liste des noms de joueurs à la liste d'IDs dans le dictionnaire
    return dict_team


def id_name(new_saison):
    list_player = os.listdir(f"../data/{new_saison}/players")
    # map list_player for split by _ and get first and second name
    dict_id_name = {}
    for player in list_player:
        id = player.split("_")[-1]

        dict_id_name[id] = player
    return dict_id_name
dict_id_name = id_name(new_saison)
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
    print(row)
    dict_team = get_id_for_team(row, dict_id_name)
    print(dict_team)
    equipe = get_equipe(dict_team, new_saison)
    print(equipe)
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
