from fastapi import APIRouter, Request, HTTPException, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import sqlite3
import matplotlib.pyplot as plt
import io
import base64

router = APIRouter()
templates = Jinja2Templates(directory="templates")

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
