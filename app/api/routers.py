from litestar.types import ControllerRouterHandler

from app.scraper.controllers.movie_scraper import MovieScraperController

route_handlers: list[ControllerRouterHandler] = [
    MovieScraperController,
]
