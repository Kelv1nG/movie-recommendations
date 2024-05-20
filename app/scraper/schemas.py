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


class MovieDetails(BaseModel):
    movie_url: str
    movie_slug: str
    description: str
    directors: list[str]
    genres: list[str]
    release_date: str
    duration: str
    casts: list[str]
    production_companies: list[str]
    meta_score: str
    user_score: str
    rating: str
