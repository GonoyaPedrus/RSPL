from pydantic import BaseModel
import pymysql
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi import HTTPException, status
import uvicorn

app = FastAPI()

# Configuration de la connexion à la base de données AWS RDS
db_host = 'database-1.clq2ucwoa2c5.us-east-1.rds.amazonaws.com'
db_user = 'admin'
db_password = '12345678'
db_name = 'loginperson'

# Templates directory
templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")
# Modèle Pydantic pour les données du formulaire de connexion
class LoginForm(BaseModel):
    username: str
    password: str

# Route pour la page de login
@app.get("/login", response_class=HTMLResponse)
async def get_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Route pour gérer l'authentification
@app.post("/login")
async def login(login_form: LoginForm):
    # Connexion à la base de données
    connection = pymysql.connect(host=db_host,
                                 user=db_user,
                                 password=db_password,
                                 database=db_name,
                                 cursorclass=pymysql.cursors.DictCursor)

    try:
        with connection.cursor() as cursor:
            # Exemple de requête pour vérifier les informations de connexion
            sql = "SELECT * FROM person WHERE username = %s AND password = %s"
            cursor.execute(sql, (login_form.username, login_form.password))
            result = cursor.fetchone()
            if result:
                return {"message": "Login successful"}
            else:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    finally:
        connection.close()


class SignupForm(BaseModel):
    username: str
    password: str
# Route pour la page d'inscription
@app.get("/inscription", response_class=HTMLResponse)
async def get_inscription(request: Request):
    return templates.TemplateResponse("inscription.html", {"request": request})

# Route pour gérer l'inscription
@app.post("/inscription")
async def inscription(signup_form: SignupForm):
    # Connexion à la base de données
    connection = pymysql.connect(host=db_host,
                                 user=db_user,
                                 password=db_password,
                                 database=db_name,
                                 cursorclass=pymysql.cursors.DictCursor)

    try:
        with connection.cursor() as cursor:
            # Insérer les informations d'inscription dans la base de données
            sql = "INSERT INTO person (username, password) VALUES (%s, %s)"
            cursor.execute(sql, (signup_form.username, signup_form.password))
            connection.commit()
            return {"message": "Inscription successful"}
    finally:
        connection.close()

if __name__ == "__main__":
    uvicorn.run(app)
