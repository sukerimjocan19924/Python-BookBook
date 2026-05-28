from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from pathlib import Path

from motor.motor_asyncio import AsyncIOMotorClient

from app.models import mongodb
from app.models.book import BookModel
from app.book_scraper import NaverBookScraper

app = FastAPI()


BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    # book=BookModel(
    #     keyword="python",
    #     publisher="lizb",
    #     price=1200,
    #     image="me.png"
    # )
    # save_book = await mongodb.engine.save(book)
    # print(save_book.model_dump(), flush=True)
    return templates.TemplateResponse(request, "index.html", {"title": "북북"})


@app.get("/search", response_class=HTMLResponse)
async def read_item(request: Request, q: str):
    keyword = q

    if not keyword:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={"message": "검색어를 입력해주세요"},
        )
    naver_book_scraper = NaverBookScraper()

    books = await naver_book_scraper.search(keyword, 10)

    book_models = []

    for book in books:
        print(book)
        book_model = BookModel(
            keyword=keyword,
            publisher=book["publisher"],
            price=int(book.get("discount") or 0),
            image=book["image"],
        )
        book_models.append(book_model)

    await mongodb.engine.save_all(book_models)

    return templates.TemplateResponse(
        request=request, name="index.html", context={"keyword": q, "books": book_models}
    )


@app.on_event("startup")
async def on_app_start():
    print("hello server")
    mongodb.connect()


@app.on_event("shutdown")
async def on_app_shutdown():
    print("goodbye server")
    mongodb.close()
