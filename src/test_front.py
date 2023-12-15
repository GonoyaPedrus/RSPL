import pandas as pd 
import os 
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
app = FastAPI()

templates = Jinja2Templates(directory="templates") 
dict_team = {"FWD":[],
             "MID":[],
             "DEF":[],
             "GK":[],}
new_saison = "2023-24"
dict_max = {"FWD":3,
             "MID":5,
             "DEF":5,
             "GK":2,}
def get_cheapest_players(new_saison, dict_team):
    print(f"Getting cheapest players for {new_saison}")
    df = pd.read_csv(f"../data/{new_saison}/cleaned_players.csv")
    cost = 0
    for k, v in dict_team.items():
        df_tmp = df[df["element_type"] == k].sort_values(by=["now_cost"]).head(1)
        cost += df_tmp["now_cost"].values[0]
        print(df_tmp["first_name"].values[0])
        print(df_tmp["second_name"].values[0])
        name  = df_tmp["first_name"].values[0] + " " + df_tmp["second_name"].values[0]
        dict_team[k].append(name)
    print(dict_team)
    print(cost)
    return dict_team, cost

def get_best_players(new_saison, dict_team, dict_max,cost ):
    df = pd.read_csv(f"../data/{new_saison}/cleaned_players.csv")
    for k, v in dict_max.items():
        df_tmp = df[df["element_type"] == k].sort_values(by=["total_points"], ascending=False).head(v)
        for i in range(v-1):
            name  = df_tmp["first_name"].values[i] + " " + df_tmp["second_name"].values[i]

            dict_team[k].append(name)
            cost += df_tmp["now_cost"].values[i]
    print(dict_team)
    return dict_team,cost

def new_saison_player(new_saison,dict_team):
    list_player = os.listdir(f"../data/{new_saison}/players")

    print(list_player)
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
def get_weeks_of_player(dict_index,player, new_saison, week_num):
    list_player = os.listdir(f"../data/{new_saison}/players")
    try : 
        df = pd.read_csv(f"../data/{new_saison}/players/{list_player[dict_index[player]]}/gw.csv")
        return df
    except:
        print("player not in list")
        return False
def get_stats(week_num,dict_index,dict_team, new_saison):
    dict_stats = {}
    for position,player in dict_team.items():
        for player in player:
            df = get_weeks_of_player(dict_index,player, new_saison, week_num)
            if df is False:
                return False
            else:
                dict_stats[player] = [df["bps"].iloc[week_num],df["value"].iloc[week_num]]
    return dict_stats

equipe, cost = get_cheapest_players(new_saison, dict_team)

equipe, cost = get_best_players(new_saison, equipe, dict_max,cost)
dict_index =  new_saison_player(new_saison,dict_team)

dict_stats = get_stats(0,dict_index,dict_team, new_saison)
print(dict_stats)
        


app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/equipe")
async def get_equipe(request: Request):
    return templates.TemplateResponse("equipe.html", {"request": request, "equipe": equipe})
@app.get("/equipe/{week_num}")
async def get_equipe(request: Request, week_num: int):
    dict_stats = get_stats(week_num, dict_index, dict_team, new_saison)

    return templates.TemplateResponse(
        "equipe_week.html", {"request": request, "equipe": equipe, "dict_stats": dict_stats}
    )


if __name__ == "__main__":
    uvicorn.run(app)
