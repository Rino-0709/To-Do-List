from fastapi import FastAPI, Request, Form, Response, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from uuid import uuid4
import json

from utils import hash_password, verify_password, sign_data, unsign_data

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# В памяти хранятся пользователи (для учебного проекта)
users_db = {}  # "alex": {"password": "$2b$...", "tasks": [...]}

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    user_data = get_user_from_cookie(request)
    if not user_data:
        return RedirectResponse("/login")
    return templates.TemplateResponse("index.html", {"request": request, "user": user_data})

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
async def register(username: str = Form(), password: str = Form()):
    if username in users_db:
        raise HTTPException(400, "Пользователь уже существует")
    users_db[username] = {
        "password": hash_password(password),
        "tasks": []
    }
    response = RedirectResponse("/login", status_code=303)
    return response

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(response: Response, username: str = Form(), password: str = Form()):
    user = users_db.get(username)
    if not user or not verify_password(password, user["password"]):
        raise HTTPException(400, "Неверный логин или пароль")
    
    data = {"username": username, "tasks": user["tasks"]}
    signed = sign_data(data)
    resp = RedirectResponse("/", status_code=303)
    resp.set_cookie(key="user_data", value=signed, httponly=True, max_age=86400*30)
    return resp

@app.post("/logout")
async def logout():
    resp = RedirectResponse("/login", status_code=303)
    resp.delete_cookie("user_data")
    return resp

@app.post("/add")
async def add_task(request: Request, text: str = Form()):
    user_data = get_user_from_cookie(request)
    if not user_data: return RedirectResponse("/login")
    
    new_task = {"id": str(uuid4())[:8], "text": text, "done": False}
    user_data["tasks"].append(new_task)
    update_cookie(request, user_data)
    return RedirectResponse("/", status_code=303)

@app.post("/toggle/{task_id}")
async def toggle_task(task_id: str, request: Request):
    user_data = get_user_from_cookie(request)
    if not user_data: return RedirectResponse("/login")
    
    for task in user_data["tasks"]:
        if task["id"] == task_id:
            task["done"] = not task["done"]
            break
    update_cookie(request, user_data)
    return RedirectResponse("/", status_code=303)

@app.post("/delete/{task_id}")
async def delete_task(task_id: str, request: Request):
    user_data = get_user_from_cookie(request)
    if not user_data: return RedirectResponse("/login")
    
    user_data["tasks"] = [t for t in user_data["tasks"] if t["id"] != task_id]
    update_cookie(request, user_data)
    return RedirectResponse("/", status_code=303)

# Вспомогательные функции
def get_user_from_cookie(request: Request):
    cookie = request.cookies.get("user_data")
    if not cookie:
        return None
    return unsign_data(cookie)

def update_cookie(request: Request, user_data: dict):
    signed = sign_data(user_data)
    # FastAPI не даёт менять response в хендлерах напрямую → просто возвращаем редирект с новой кукой
    # поэтому в каждом POST делаем RedirectResponse с новой кукей
    pass