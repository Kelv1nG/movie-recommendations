from dataclasses import dataclass

from pydantic import BaseModel


@dataclass(frozen=True)
class HtmlElementSelector:
    tag: str
    css: str


class Movie(BaseModel):
    movie_url: str
    thumbnail_url: str | None
    title: str
    type: str
    year: int | None
    rating: str
