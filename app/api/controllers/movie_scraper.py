from collections.abc import Generator

from litestar import Controller, get, post
from litestar.di import Provide
from pydantic import BaseModel

from app.scraper import schemas
from app.scraper.abstract_scraper import AbstractMovieScraper
from app.scraper.metacritic_scraper import MetacriticScraper


def generate_movie_scraper() -> Generator[AbstractMovieScraper, None, None]:
    yield MetacriticScraper()


class TitleSearchInput(BaseModel):
    title: str


class MovieScraperController(Controller):
    path = "/api/movie"
    dependencies = {"movie_scraper": Provide(generate_movie_scraper)}

    @post(path="search_title", sync_to_thread=True)
    def search_movie(
        self, data: TitleSearchInput, movie_scraper: AbstractMovieScraper
    ) -> list[schemas.Movie]:
        return movie_scraper.search_movie_title(data.title)
