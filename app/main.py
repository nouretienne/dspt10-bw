from fastapi import FastAPI, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn

from app import db, ml, viz, aws

app = FastAPI(
    title="Spotify Song Suggester",
    description="Predict songs that you'll like based on what you already like",
    docs_url="/docs",
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", tags=["Homepage"])
async def homepage(request: Request):
    return templates.TemplateResponse("homepage.html", context={"request": request})


@app.post("/", tags=["Homepage"])
async def homepage(
    request: Request,
    song_name: str = Form(...),
    genre: str = Form(...),
    release_date: int = Form(...),
    explicit: int = Form(...)
):

    return templates.TemplateResponse(
        "homepage.html",
        context={
            "request": request,
            "song_name": song_name,
            "genre": genre,
            "release_date": release_date,
            "explicit": explicit,
        })


app.include_router(db.router, tags=["Database"])
app.include_router(aws.router, tags=["AWS S3"])
app.include_router(ml.router, tags=["Machine Learning"])
app.include_router(viz.router, tags=["Visualization"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(app)
