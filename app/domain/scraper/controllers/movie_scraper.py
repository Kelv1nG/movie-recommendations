from collections.abc import Generator

from litestar import Controller, get
from litestar.di import Provide

from app.domain.scraper import schemas, urls
from app.domain.scraper.abstract_scraper import AbstractMovieScraper
from app.domain.scraper.metacritic.metacritic_scraper import MetacriticScraper


def generate_movie_scraper() -> Generator[AbstractMovieScraper, None, None]:
    yield MetacriticScraper()


class MovieScraperController(Controller):
    dependencies = {"movie_scraper": Provide(generate_movie_scraper)}

    @get(path=urls.MOVIE_SEARCH_LIST)
    async def search_movie(
        self, title: str, movie_scraper: AbstractMovieScraper
    ) -> list[schemas.Movie]:
        return [
            schemas.Movie(**details)
            for details in await movie_scraper.search_movie_title(title)
        ]

    @get(path=urls.MOVIE_DETAIL, sync_to_thread=True)
    def movie_details(
        self, movie_slug: str, movie_scraper: MetacriticScraper
    ) -> schemas.MovieDetails:
        return schemas.MovieDetails(**movie_scraper.get_movie_details(movie_slug))
