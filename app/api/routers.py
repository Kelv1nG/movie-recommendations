from litestar.types import ControllerRouterHandler

from app.domain.scraper.controllers.movie_scraper import MovieScraperController

route_handlers: list[ControllerRouterHandler] = [
    MovieScraperController,
]
