from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from redis_client import redis_client
from auth import get_username
import time

router = APIRouter()

@router.get("/chat", response_class=HTMLResponse)
async def chat_page(token: str, request: Request):
    username = await get_username(token)
    if not username:
        return RedirectResponse("/login")
    messages = await redis_client.xrange("stream:room:general", count=50)
    context = {"request": request, "username": username, "token": token, "messages": messages}
    return request.app.state.templates.TemplateResponse("chat.html", context)

@router.post("/chat/send")
async def send_message(token: str = Form(...), message: str = Form(...)):
    username = await get_username(token)
    if not username:
        return RedirectResponse("/login")
    await redis_client.xadd("stream:room:general", {"user": username, "message": message, "ts": str(int(time.time()))})
    await redis_client.publish("room:general", f"{username}: {message}")
    return RedirectResponse(f"/chat?token={token}", status_code=302)

@router.get("/chat/online")
async def get_online():
    return await redis_client.smembers("online_users")
