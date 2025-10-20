from fastapi import FastAPI, Form, UploadFile, File, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import shutil
import face_recognition
from blockchain import Blockchain
from face_recognition_utils import save_face_encoding

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

blockchain = Blockchain()
registered_users = {}

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
async def register_user(name: str = Form(...), voter_id: str = Form(...), image: UploadFile = File(...)):
    path = f"static/{image.filename}"
    with open(path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    encoding = save_face_encoding(path)
    registered_users[voter_id] = {"name": name, "encoding": encoding}
    return RedirectResponse("/", status_code=303)

@app.get("/vote", response_class=HTMLResponse)
async def vote_page(request: Request):
    return templates.TemplateResponse("vote.html", {"request": request})

@app.post("/vote")
async def cast_vote(voter_id: str = Form(...), candidate: str = Form(...), image: UploadFile = File(...)):
    path = f"static/{image.filename}"
    with open(path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    unknown_encoding = save_face_encoding(path)
    user = registered_users.get(voter_id)

    if user and face_recognition.compare_faces([user["encoding"]], unknown_encoding)[0]:
        blockchain.add_block(voter_id, candidate)
        return RedirectResponse("/results", status_code=303)
    return {"error": "Face verification failed!"}

@app.get("/results", response_class=HTMLResponse)
async def show_results(request: Request):
    results = blockchain.count_votes()
    return templates.TemplateResponse("results.html", {"request": request, "results": results})
