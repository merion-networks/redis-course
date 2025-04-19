from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from auth import router as auth_router
from chat import router as chat_router
from ws import router as ws_router

app = FastAPI()
app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(ws_router)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.state.templates = Jinja2Templates(directory="templates")
