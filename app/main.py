from fastapi import FastAPI, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import Optional
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn

from app import db, ml, viz, aws, spotify

app = FastAPI(
    title="Spotify Song Suggester",
    description="Predict songs that you'll like based on what you already like",
    docs_url="/docs",
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/", tags=["Homepage"])
async def homepage(request: Request):
    hidden = "hidden"
    submit_val = "See Artists"
    return templates.TemplateResponse(
        "homepage.html",
        context={"request": request, "hidden": hidden, "submit_val": submit_val},
    )


def modelhere():
    return 'Please insert cassette_158 to load model'


@app.post("/", tags=["Homepage"])
async def homepage(request: Request,
                   artists_option: str = Form(None),
                   song_name: str = Form(...)
                   ):
    #artists = spotify.song_to_artist(song_name)
    artists = ['artist1', 'artist2', 'artist3', 'artist4', 'artist5']
    submit_val = "Submit"
    model_out = ""
    if artists_option is not None:
        model_out = modelhere()
    return templates.TemplateResponse(
        "homepage.html",
        context={
            "request": request,
            "song_name": song_name,
            "artists": artists,
            "selected_artist": artists_option,
            "submit_val": submit_val,
            "model_out": model_out
        },
    )

app.include_router(spotify.router, tags=['Spotify'])
app.include_router(ml.router, tags=["Machine Learning"])
app.include_router(viz.router, tags=["Visualization"])
app.include_router(aws.router, tags=["AWS"])
app.include_router(db.router, tags=["Database"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(app)
