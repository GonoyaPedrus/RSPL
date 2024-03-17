
import pandas as pd 
import os 
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
from fastapi import APIRouter
import sqlite3
db_connection = sqlite3.connect('../database/loginperson.db')
db_cursor = db_connection.cursor()
router = APIRouter()

templates = Jinja2Templates(directory="templates") 
new_saison = "2023-24"


def new_saison_player_index(new_saison):
    list_player = os.listdir(f"../data/{new_saison}/players")
    #map list_player for split by  and get first and second name
    dict_index = {}
    for player in list_player:
        dict_index[player.split("_")[0] + " " + player.split("_")[1]] = player.split("_")[-1]

    return dict_index
dict_index = new_saison_player_index(new_saison)

def get_id_for_team(table_row, dict_index):
    dict_team = {}
    for ids in table_row:
        id_list = ids.split(', ')  # Diviser la chaîne d'IDs en une liste
        for id in id_list:
            for name, player_id in dict_index.items():
                if player_id == id:
                      # Ajouter le nom du joueur correspondant à l'ID à la liste
                    
                    dict_team[name] = id_list 
                    break # Associer la liste des noms de joueurs à la liste d'IDs dans le dictionnaire
    return dict_team 

def new_saison_player(new_saison,dict_team):
    list_player = os.listdir(f"../data/{new_saison}/players")
    #map list_player for split by _ and get first and second name
    list_player = [player.split("_")[0] + " " + player.split("_")[1] for player in list_player]
    dict_index = {}
    for k, v in dict_team.items():
        for player in v:
             
            if player not in list_player:
                print(player)
                print(k)
                print(v)
                


                print("not in list player")
                return False
            else:

                dict_index[player] = list_player.index(player)
    return dict_index    
def get_weeks_of_player(dict_index,player, new_saison):
    list_player = os.listdir(f"../data/{new_saison}/players")

    try : 
        df = pd.read_csv(f"../data/{new_saison}/players/{list_player[dict_index[player]]}/gw.csv")
        return df
    except:
        print("player not in list")
        return False
def get_team(dict_index,equipe, new_saison):
    print("getting team")
    print(dict_index)
    df_id  = pd.read_csv(f"../data/{new_saison}/player_idlist.csv")
    list_player = os.listdir(f"../data/{new_saison}/players")
    df = pd.read_csv(f"../data/{new_saison}/players_raw.csv")
    df_team = pd.read_csv(f"../data/{new_saison}/teams.csv")
    print(df_team.columns)
    dict_team = {}
    for k, v in dict_index.items():
    

        player_id = list_player[v].split("_")[-1]

        #get row of de_id where player_id is equal to player_id
        df_tmp = df_id[df_id["id"] == int(player_id)]
        first_name = df_tmp["first_name"].values[0]
        second_name = df_tmp["second_name"].values[0]
        #get row of df where first_name and second_name are equal to first_name and second_name
        df_tmp_2 = df[(df["first_name"] == first_name) & (df["second_name"] == second_name)]
        id_team = df_tmp_2["team"].values[0]
        team_name = df_team[df_team["id"] == id_team]["name"].values[0]
        dict_team[k] = team_name
    
    return dict_team



def get_stats(week_num,dict_index,dict_team, new_saison):
    dict_stats = {}
    for position,player in dict_team.items():
        for player in player:
            df = get_weeks_of_player(dict_index,player, new_saison)
            if df is False:
                return False
            else:
                dict_stats[player] = [df["total_points"].iloc[week_num],df["value"].iloc[week_num]]
    return dict_stats


#dict_index =  new_saison_player(new_saison,dict_team)

#dict_stats = get_stats(0,dict_index,dict_team, new_saison)
#print(dict_stats)
#dict_team_by_player = get_team(dict_index,equipe, new_saison)

#print(dict_team_by_player)




@router.get("/equipe")
async def get_equipe(request: Request):
    return templates.TemplateResponse("equipe.html", {"request": request, "equipe": equipe})
@router.get("/equipe/{week_num}", response_class=HTMLResponse)
async def get_equipe(request: Request, week_num: int):
    # Obtenez les statistiques de la semaine pour l'équipe
    if "user_id" not in request.session:
        return {"error": "User not logged in"}
    user_id = request.session["user_id"]
    # Vérifier si la semaine est définie dans la session
    request.session["week_num"] = week_num

    
    # Ouvrir la connexion à la base de données
    db_connection_team = sqlite3.connect("../database/team_database.db")
    db_cursor_team = db_connection_team.cursor()
    #requet sql
    db_cursor_team.execute(f"SELECT * FROM user_id_team ORDER BY ROWID DESC LIMIT 1;")
    row = db_cursor_team.fetchall()
    dict_team = get_id_for_team(row, dict_index)
    dict_stats = get_stats(week_num, dict_index, dict_team, new_saison)
    
    # Calculez le nombre total de points et la valeur totale de l'équipe
    total_points = sum(v[0] for v in dict_stats.values())
    total_value = sum(v[1] for v in dict_stats.values())

    # Mettez à jour les statistiques de l'utilisateur dans sa table de statistiques
    
    
    # Vérifier si une ligne pour cette semaine existe déjà dans la table
    db_cursor.execute(f"SELECT * FROM user_{user_id}_stats WHERE week = ?", (week_num,))
    existing_row = db_cursor.fetchone()
    if existing_row:
        # Si une ligne existe, mettez à jour les valeurs
        db_cursor.execute(f'''
            UPDATE user_{user_id}_stats
            SET money = ?, points = ?
            WHERE week = ?
        ''', (int(total_value), int(total_points), week_num))
    else:
        # Sinon, insérez une nouvelle ligne
        db_cursor.execute(f'''
            INSERT INTO user_{user_id}_stats (week, money, points)
            VALUES (?, ?, ?)
        ''', (week_num, int(total_value), int(total_points)))
    db_connection.commit()

    #print table user_{user_id}_stats
    rows = db_cursor.execute(f'SELECT * FROM user_{user_id}_stats').fetchall()

    for row in rows:
        print(row)
    
 
    # Renvoie le template HTML avec les nouvelles statistiques
    return templates.TemplateResponse(
        "equipe_week.html", 
        {"request": request, "equipe": equipe, "dict_stats": dict_stats, "total_points": total_points, "week_num": week_num, "total_value": total_value, "dict_team": dict_team_by_player}
    )


    """ 
    if __name__ == "__main__":
        uvicorn.run(app) """
