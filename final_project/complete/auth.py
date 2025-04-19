import uuid
from fastapi import APIRouter, Form, Request, Depends
from fastapi.responses import RedirectResponse
from redis_client import redis_client
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

router = APIRouter()

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})
    
@router.post("/register")
async def register(username: str = Form(...), password: str = Form(...)):
    await redis_client.hset(f"user:{username}", mapping={"password": password})
    return RedirectResponse("/login", status_code=302)

@router.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    stored = await redis_client.hget(f"user:{username}", "password")
    if stored != password:
        return RedirectResponse("/login?error=1", status_code=302)
    token = str(uuid.uuid4())
    await redis_client.set(f"token:{token}", username, ex=3600)
    await redis_client.sadd("online_users", username)
    await redis_client.xadd("stream:room:general", {"user": username, "message": "joined"})
    return RedirectResponse(f"/chat?token={token}", status_code=302)

@router.get("/logout")
async def logout(token: str):
    username = await redis_client.get(f"token:{token}")
    if username:
        await redis_client.delete(f"token:{token}")
        await redis_client.srem("online_users", username)
        await redis_client.xadd("stream:room:general", {"user": username, "message": "left"})
    return RedirectResponse("/login", status_code=302)

async def get_username(token: str):
    return await redis_client.get(f"token:{token}")
