from fastapi import FastAPI, Request, Form, Response, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from uuid import uuid4

from utils import hash_password, verify_password, sign_data, unsign_data

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

users_db = {} 

def get_user_from_cookie(request: Request):
    user_data = request.cookies.get("user_data")
    if not user_data:
        return None
    return unsign_data(user_data)

def set_user_cookie(response: Response, user_data: dict):
    signed = sign_data(user_data)
    response.set_cookie(
        key="user_data",
        value=signed,
        httponly=True,
        max_age=86400*30,
        samesite="lax"
    )

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    user = get_user_from_cookie(request)
    if not user:
        return RedirectResponse("/login")
    return templates.TemplateResponse("index.html", {"request": request, "user": user})

@app.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def register_get(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
async def register_post(username: str = Form(), password: str = Form()):
    if username in users_db:
        raise HTTPException(400, "Пользователь уже существует")
    users_db[username] = {"password": hash_password(password), "tasks": []}
    return RedirectResponse("/login", status_code=303)

@app.post("/login")
async def login_post(username: str = Form(), password: str = Form()):
    user = users_db.get(username)
    if not user or not verify_password(password, user["password"]):
        raise HTTPException(400, "Неверный логин или пароль")
    resp = RedirectResponse("/", status_code=303)
    set_user_cookie(resp, {"username": username, "tasks": user["tasks"][:]})
    return resp

@app.post("/logout")
async def logout():
    resp = RedirectResponse("/login", status_code=303)
    resp.delete_cookie("user_data")
    return resp

@app.post("/add")
async def add_task(request: Request, text: str = Form()):
    user = get_user_from_cookie(request)
    if not user: return RedirectResponse("/login")
    user["tasks"].append({"id": str(uuid4())[:8], "text": text.strip(), "done": False})
    resp = RedirectResponse("/", status_code=303)
    set_user_cookie(resp, user)
    return resp

@app.post("/toggle/{task_id}")
async def toggle(task_id: str, request: Request):
    user = get_user_from_cookie(request)
    if not user: return RedirectResponse("/login")
    for t in user["tasks"]:
        if t["id"] == task_id:
            t["done"] = not t["done"]
    resp = RedirectResponse("/", status_code=303)
    set_user_cookie(resp, user)
    return resp






@app.post("/delete/{task_id}")
async def delete(task_id: str, request: Request):
    user = get_user_from_cookie(request)
    if not user: return RedirectResponse("/login")
    user["tasks"] = [t for t in user["tasks"] if t["id"] != task_id]
    resp = RedirectResponse("/", status_code=303)
    set_user_cookie(resp, user)
    return resp