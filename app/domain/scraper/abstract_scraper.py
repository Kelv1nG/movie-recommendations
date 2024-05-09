from abc import ABC, abstractmethod


class AbstractMovieScraper(ABC):
    @property
    @abstractmethod
    def site_url(self):
        raise NotImplementedError

    @abstractmethod
    async def search_movie_title(self, title: str) -> list:
        raise NotImplementedError

    @abstractmethod
    async def get_movie_details(self, movie_slug: str) -> dict:
        raise NotImplementedError
