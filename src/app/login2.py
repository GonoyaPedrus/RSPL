# login.py

from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, status, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import sqlite3

router = APIRouter()

# Templates directory
templates = Jinja2Templates(directory="templates")

router.mount("/static", StaticFiles(directory="static"), name="static")

# Modèle Pydantic pour les données du formulaire de connexion
class LoginForm(BaseModel):
    username: str
    password: str

# Connexion à la base de données SQLite (crée la base de données si elle n'existe pas)
db_connection = sqlite3.connect('../database/loginperson.db')
db_cursor = db_connection.cursor()

# Création de la table person si elle n'existe pas
db_cursor.execute('''
    CREATE TABLE IF NOT EXISTS person (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password TEXT NOT NULL
    )
''')
db_connection.commit()

# Route pour la page de login
@router.get("/login", response_class=HTMLResponse)
async def get_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Route pour gérer l'authentification
@router.post("/login")
async def login(request: Request, login_form: LoginForm):
    # Requête pour vérifier les informations de connexion
    db_cursor.execute("SELECT id FROM person WHERE username = ? AND password = ?", (login_form.username, login_form.password))
    result = db_cursor.fetchone()
    if result:
        # Stocker l'identifiant de l'utilisateur dans la session
        request.session["user_id"] = result[0]
        print(request.session["user_id"])
        return {"message": "Login successful"}
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

# Modèle Pydantic pour les données du formulaire d'inscription
class SignupForm(BaseModel):
    username: str
    password: str

# Route pour la page d'inscription
@router.get("/inscription", response_class=HTMLResponse)
async def get_inscription(request: Request):
    return templates.TemplateResponse("inscription.html", {"request": request})

# Route pour gérer l'inscription
# Route pour gérer l'inscription
@router.post("/inscription")
async def inscription(signup_form: SignupForm):
    # Insérer les informations d'inscription dans la table person
    db_cursor.execute("INSERT INTO person (username, password) VALUES (?, ?)", (signup_form.username, signup_form.password))
    db_connection.commit()

    # Récupérer l'identifiant de l'utilisateur nouvellement inscrit
    db_cursor.execute("SELECT id FROM person WHERE username = ?", (signup_form.username,))
    user_id = db_cursor.fetchone()[0]

    # Créer une nouvelle table de statistiques pour l'utilisateur
    db_cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS user_{user_id}_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            week INTEGER DEFAULT 0,
            money BLOB DEFAULT 1000,
            points BLOB DEFAULT 0
        )
    ''')
    db_connection.commit()

    # Insérer les statistiques initiales de l'utilisateur dans sa table de statistiques
    db_cursor.execute(f"INSERT INTO user_{user_id}_stats DEFAULT VALUES")
    db_connection.commit()

    return {"message": "Inscription successful"}

    