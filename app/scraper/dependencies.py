from collections.abc import Generator

from app.scraper.abstract_scraper import AbstractMovieScraper
from app.scraper.metacritic.metacritic_scraper import MetacriticScraper


def generate_movie_scraper() -> Generator[AbstractMovieScraper, None, None]:
    yield MetacriticScraper()
