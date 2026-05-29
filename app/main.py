from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pathlib import Path

from motor.motor_asyncio import AsyncIOMotorClient

from app.models import mongodb
from app.models.book import BookModel
from app.book_scraper import NaverBookScraper

app = FastAPI()


BASE_DIR = Path(__file__).resolve().parent

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
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

    naver_book_scraper = NaverBookScraper()
    books = await naver_book_scraper.search(keyword, 10)

    favorite_books = await mongodb.engine.find(BookModel, BookModel.is_favorite == True)

    favorite_images = [book.image for book in favorite_books]

    book_models = []

    for book in books:
        print(book)
        book_model = BookModel(
            keyword=keyword,
            publisher=book["publisher"],
            price=int(book.get("discount") or 0),
            image=book["image"],
        )

        if book_model.image in favorite_images:
            book_model.is_favorite = True

        book_models.append(book_model)

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"keyword": q, "books": book_models, "next_url": f"/search?q={q}"},
    )


@app.post("/favorites")
async def toggle_favorite(
    request: Request,
    keyword: str = Form(...),
    publisher: str = Form(...),
    price: int = Form(...),
    image: str = Form(...),
    next_url: str = Form("/"),
):
    favorite_book = await mongodb.engine.find_one(
        BookModel,
        (BookModel.keyword == keyword)
        & (BookModel.publisher == publisher)
        & (BookModel.image == image)
        & (BookModel.is_favorite == True),
    )
    if favorite_book:
        await mongodb.engine.delete(favorite_book)

    else:
        book = BookModel(
            keyword=keyword,
            publisher=publisher,
            price=price,
            image=image,
            is_favorite=True,
        )
        await mongodb.engine.save(book)

    return RedirectResponse(url=next_url, status_code=303)


@app.get("/favorites", response_class=HTMLResponse)
async def favorites(request: Request):
    books = await mongodb.engine.find(BookModel, BookModel.is_favorite == True)

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"title": "즐겨찾기 목록", "books": books, "next_url": "/favorites"},
    )


@app.on_event("startup")
async def on_app_start():
    print("hello server")
    mongodb.connect()


@app.on_event("shutdown")
async def on_app_shutdown():
    print("goodbye server")
    mongodb.close()
