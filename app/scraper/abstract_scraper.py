from abc import ABC, abstractmethod


class AbstractMovieScraper(ABC):
    USER_AGENT = {"User-agent": "Mozilla/5.0"}

    @property
    @abstractmethod
    def site_url(self):
        raise NotImplementedError

    @abstractmethod
    def search_movie_title(self, title: str) -> list:
        raise NotImplementedError

    @abstractmethod
    def get_movie_details(self, movie_slug):
        raise NotImplementedError
