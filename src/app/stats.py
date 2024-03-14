from fastapi import APIRouter, Request , HTTPException, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import sqlite3

router = APIRouter()
templates = Jinja2Templates(directory="templates")
@router.get("/statistique", response_class=HTMLResponse)
async def get_stats(request: Request):
    # Vérifier si l'utilisateur est connecté
    print(request.session)
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

    return templates.TemplateResponse(
        "stats.html",
        {"request": request, "stats": stats}
    )
