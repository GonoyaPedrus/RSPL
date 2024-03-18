from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from app import login2, create_team, test_front, stats, modifier_equipe
from fastapi.staticfiles import StaticFiles
import uvicorn

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(login2.router, prefix="/api")
app.include_router(create_team.router, prefix="/api")
app.include_router(test_front.router, prefix="/api")
app.include_router(stats.router, prefix="/api")
app.include_router(modifier_equipe.router, prefix="/api")

# Ajout du middleware de session
app.add_middleware(SessionMiddleware, secret_key="azerty")
# Redirection vers /api/login lors de l'accès à la racine
@app.get("/")
async def redirect_to_login():
    return RedirectResponse(url="/api/login")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
