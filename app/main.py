from fastapi import FastAPI,Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from pathlib import Path

app = FastAPI()


BASE_DIR=Path(__file__).resolve().parent
templates = Jinja2Templates(directory=BASE_DIR/ "templates")


@app.get("/",response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(
        request,
        "index.html",
        {"title":"북북"}
    ) 


@app.get("/search",response_class=HTMLResponse)
async def read_item(request:Request,q:str):
    return templates.TemplateResponse(
        request,
        "index.html",
        {"keyword":q}
    )
