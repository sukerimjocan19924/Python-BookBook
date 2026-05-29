from odmantic import Model
from pydantic import ConfigDict


class BookModel(Model):
    keyword: str
    publisher: str
    price: int
    image: str
    is_favorite: bool = False

    model_config = {"collection": "books"}
