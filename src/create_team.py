import pandas as pd 
import os 
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates") 
new_saison = "2023-24"
dict_team = [{'name': 'Erling Haaland', 'position': 'FWD', 'team': 'Man City', 'cost': 115, 'predicted_performance': 16.540115}, {'name': 'Bruno Miguel Borges Fernandes', 'position': 'MID', 'team': 'Man Utd', 'cost': 105, 'predicted_performance': 11.457617}, {'name': 'David De Gea Quintana', 'position': 'GK', 'team': 'Man Utd', 'cost': 50, 'predicted_performance': 10.829479}, {'name': 'Alisson Ramses Becker', 'position': 'GK', 'team': 'Liverpool', 'cost': 60, 'predicted_performance': 10.573772}, {'name': 'Bruno Borges Fernandes', 'position': 'MID', 'team': 'Man Utd', 'cost': 100, 'predicted_performance': 10.408141}, {'name': 'Ivan Toney', 'position': 'FWD', 'team': 'Brentford', 'cost': 65, 'predicted_performance': 10.241132}, {'name': 'Cody Gakpo', 'position': 'MID', 'team': 'Liverpool', 'cost': 80, 'predicted_performance': 9.668974}, {'name': 'James Maddison', 'position': 'MID', 'team': 'Leicester', 'cost': 70, 'predicted_performance': 9.51857}, {'name': 'Kaoru Mitoma', 'position': 'MID', 'team': 'Brighton', 'cost': 50, 'predicted_performance': 9.316569}, {'name': 'Romelu Lukaku', 'position': 'FWD', 'team': "nan", 'cost': 90, 'predicted_performance': 9.279969}, {'name': 'Andrew Robertson', 'position': 'DEF', 'team': "nan", 'cost': 45, 'predicted_performance': 8.692561}, {'name': 'Trent Alexander-Arnold', 'position': 'DEF', 'team': "nan", 'cost': 45, 'predicted_performance': 8.22334}, {'name': 'Antonio Rüdiger', 'position': 'DEF', 'team': "nan", 'cost': 60, 'predicted_performance': 8.159134}, {'name': 'Rico Henry', 'position': 'DEF', 'team': 'Brentford', 'cost': 45, 'predicted_performance': 7.671472}]
def new_saison_player_index(new_saison):
    list_player = os.listdir(f"../data/{new_saison}/players")
    #map list_player for split by _ and get first and second name
    dict_index = {}
    for player in list_player:
        dict_index[player.split("_")[0] + " " + player.split("_")[1]] = player.split("_")[-1]
    
    return dict_index
dict_index = new_saison_player_index(new_saison)

def new_saison_player(new_saison,dict_index):
    df = pd.read_csv(f"../data/{new_saison}/cleaned_players.csv")
    df_2 = pd.read_csv(f"../data/{new_saison}/players_raw.csv")
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
            dict_tmp["team"] = df_tmp_2["team"].values[0]
            # add v in dict_player["id"]
            dict_player.append(dict_tmp)
    return dict_player

# Route principale pour afficher la page HTML
@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("create_team.html", {"request": request, "joueurs": new_saison_player(new_saison,dict_index),"dict_team":dict_team})
if __name__ == "__main__":
    uvicorn.run(app)
    #new_saison_player(new_saison,dict_index)