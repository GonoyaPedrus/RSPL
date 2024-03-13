from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
import sqlite3

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/statistique")
async def get_stats(request: Request):
    if "user_id" not in request.session:
        return {"error": "User not logged in"}

    user_id = request.session["user_id"] -1
    if "week_num" not in request.session:
        return {"error": "User not logged in"}

    week_num = request.session["week_num"]
    # Connexion à la base de données
    db_connection = sqlite3.connect(f'../database/loginperson.db')
    db_cursor = db_connection.cursor()

    # Récupérer les données de la table user_{user_id}_stats
    db_cursor.execute(f"SELECT * FROM user_{user_id}_stats WHERE week <= ?", (week_num,))
    stats = db_cursor.fetchall()
    #get list of column name
    

    

    # Fermer la connexion à la base de données
    db_connection.close()

    return templates.TemplateResponse(
        "stats.html",
        {"request": request, "stats": stats}
    )
