from fastapi import FastAPI, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
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


# What displays when you first load up the homepage
# hidden is for hidden tag, submit_val is the text that
# displays on the button
@app.get("/", tags=["Homepage"])
async def homepage(request: Request):
    hidden = "hidden"
    submit_val = "See Artists"
    return templates.TemplateResponse(
        "homepage.html",
        context={"request": request, "hidden": hidden, "submit_val": submit_val,"track_list": None, "selected_artist": None, 'usr_sel': None},
    )


# allows the homepage to update elements
# has forms to send user data to functions
@app.post("/", tags=["Homepage"])
async def homepage(
        request: Request,
        artists_option: str = Form(None),
        song_name: str = Form(...)
        ):
    model_out, track_list, usr_sel = "", None, None
    submit_val = "Submit"
    artists = spotify.song_to_artist(song_name)
    if artists_option is not None:
        usr_sel = spotify.same_name_songs(song_name, artists_option)
        model_out = spotify.suggestion(usr_sel[0]['features'])

    return templates.TemplateResponse(
        "homepage.html",
        context={
            "request": request,
            "selected_artist": artists_option,
            "artists": artists,
            "track_list": model_out[2:],
            "submit_val": submit_val,
            "usr_sel": usr_sel,
        },
    )

# Allows /docs to have and group endpoints
# Able to interact with endpoints via links or /docs page
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
