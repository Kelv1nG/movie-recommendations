from litestar import Controller, get
from litestar.di import Provide

from app.scraper import schemas
from app.scraper.abstract_scraper import AbstractMovieScraper
from app.scraper.dependencies import generate_movie_scraper
from app.scraper.metacritic.metacritic_scraper import MetacriticScraper

MOVIE_DETAIL = "/{movie_slug:str}"


class MovieScraperController(Controller):
    path = "/api/movies"
    dependencies = {"movie_scraper": Provide(generate_movie_scraper)}

    @get()
    async def search_movie(
        self, title: str, movie_scraper: AbstractMovieScraper
    ) -> list[schemas.Movie]:
        return [
            schemas.Movie(**details)
            for details in await movie_scraper.search_movie_title(title)
        ]

    @get(path=MOVIE_DETAIL, sync_to_thread=True)
    def movie_details(
        self, movie_slug: str, movie_scraper: MetacriticScraper
    ) -> schemas.MovieDetails:
        return schemas.MovieDetails(**movie_scraper.get_movie_details(movie_slug))
