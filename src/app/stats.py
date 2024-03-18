from fastapi import APIRouter, Request, HTTPException, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import sqlite3
import matplotlib.pyplot as plt
import io
import pandas as pd
import base64
import os 
router = APIRouter()
templates = Jinja2Templates(directory="templates")
new_saison = "2023-24"
def new_saison_player(new_saison):
    list_player = os.listdir(f"../data/{new_saison}/players")
    #map list_player for split by _ and get first and second name
    dict_index = {}
    for player in list_player:
        id = player.split("_")[-1]
    

        dict_index[id] = player
    return dict_index
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
                        dict_team[name] = id # Ajouter l'ID à la liste correspondante dans le dictionnaire
                        
                        # Associer la liste des noms de joueurs à la liste d'IDs dans le dictionnaire
    return dict_team


def get_weeks_of_player(dict_index,player,id, new_saison):

    try : 

        df = pd.read_csv(f"../data/{new_saison}/players/{dict_index[id]}/gw.csv")
        return df
    except:
        print("player not in list")
        print(player)
        return False

def get_stats_player(week_num,dict_index,dict_team, new_saison):
    dict_stats = {}
    df_id  = pd.read_csv(f"../data/{new_saison}/player_idlist.csv")
    df_name = pd.read_csv(f"../data/{new_saison}/players_raw.csv")
    df_team = pd.read_csv(f"../data/{new_saison}/teams.csv")
    df_position = pd.read_csv(f"../data/{new_saison}/cleaned_players.csv")
    list_all_player = df_position["first_name"].str.cat(df_position["second_name"], sep=" ").tolist()
    liste_element = df_position["element_type"].tolist()
    list_player = list(dict_team.keys())
    for player,id in dict_team.items():
        
        df = get_weeks_of_player(dict_index,player,id, new_saison)

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


dict_index = new_saison_player(new_saison)
@router.get("/statistique", response_class=HTMLResponse)
async def get_stats(request: Request):
    # Vérifier si l'utilisateur est connecté
    if "user_id" not in request.session:
        return {"error": "User not logged in"}

    # Vérifier si la semaine est définie dans la session
    if "week_num" not in request.session:
        return {"error": "Week number not defined"}

    # Récupérer l'identifiant de l'utilisateur et le numéro de semaine depuis la session
    user_id = request.session["user_id"]
    week_num = request.session["week_num"]

    # Connexion à la base de données
    db_connection = sqlite3.connect(f'../database/loginperson.db')
    db_cursor = db_connection.cursor()

    # Récupérer les données de la table user_{user_id}_stats
    db_cursor.execute(f"SELECT * FROM user_{user_id}_stats WHERE week <= ?", (week_num,))
    stats = db_cursor.fetchall()

    # Fermer la connexion à la base de données
    db_connection.close()

    # Créer des listes pour stocker les données
    weeks = []
    money_values = []
    points_values = []

    # Remplir les listes avec les données de la base de données
    for stat in stats:
        weeks.append(stat[1])
        money_values.append(stat[2])
        points_values.append(stat[3])

    # Créer les graphiques avec Matplotlib
    plt.figure(figsize=(12, 6))

    # Graphique pour la valeur de l'équipe
    plt.plot(weeks, money_values, label='Money')
    plt.xlabel('Week')
    plt.ylabel('Value')
    plt.title('Team Value')
    plt.legend()

    # Convertir le graphique en image et le sauvegarder dans un buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_team_value_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    plt.close()

    # Nouveau graphique pour les points
    plt.figure(figsize=(12, 6))

    # Graphique pour les points
    plt.plot(weeks, points_values, label='Points', color='green')
    plt.xlabel('Week')
    plt.ylabel('Points')
    plt.title('User Points')
    plt.legend()

    # Convertir le graphique en image et le sauvegarder dans un buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_user_points_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    plt.close()

    # Retourner le HTML avec les graphiques insérés
    return templates.TemplateResponse(
        "stats.html",
        {"request": request, "stats": stats, "image_team_value": image_team_value_base64, "image_user_points": image_user_points_base64}
    )


@router.get("/statistique_player", response_class=HTMLResponse)
async def get_stats_for_players(request: Request):
    # Vérifier si l'utilisateur est connecté
    if "user_id" not in request.session:
        return {"error": "User not logged in"}

    # Vérifier si la semaine est définie dans la session
    if "week_num" not in request.session:
        return {"error": "Week number not defined"}
    
    user_id = request.session["user_id"]
    week_num = request.session["week_num"]

    # Ouvrir la connexion à la base de données
    db_connection_team = sqlite3.connect("../database/team_database.db")
    db_cursor_team = db_connection_team.cursor()

    #requet sql
    db_cursor_team.execute(f"SELECT * FROM user_{user_id}_team ORDER BY ROWID DESC LIMIT 1;")
    row = db_cursor_team.fetchall()
    dict_team = get_id_for_team(row, dict_index)
    dict_stats = get_stats_player(week_num, dict_index, dict_team, new_saison)
    print(dict_stats)
    # Séparation des joueurs par position
    positions = {}
    for player, data in dict_stats.items():
        position = data[2]
        if position not in positions:
            positions[position] = []
        positions[position].append((player, data[0]))

    # Création des graphiques par position
    image_buffers = {}
    for position, player_data in positions.items():
        plt.figure(figsize=(10, 6))
        plt.title(f'Performances des joueurs ({position})')
        plt.xlabel('Semaine')
        plt.ylabel('Performance')
        for player, performance in player_data:
            plt.plot(range(1, len(performance) + 1), performance, label=player)
        plt.legend(loc='upper left')
        plt.grid(True)
        plt.xticks(range(1, len(performance) + 1))
        plt.tight_layout()

        # Sauvegarder le graphique dans un buffer
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)

        # Convertir l'image en base64
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        image_buffers[position] = image_base64

        # Fermer la figure pour libérer la mémoire
        plt.close()
        
        # Retourner le HTML avec les graphiques insérés
    return templates.TemplateResponse(
        "stats_player.html",
        {"request": request, "image_buffers": image_buffers}
    )