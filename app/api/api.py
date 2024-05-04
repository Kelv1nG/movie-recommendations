from litestar import Router

from app.api.controllers.movie_scraper import MovieScraperController

router = Router(path="/api", route_handlers=[])

router.register(MovieScraperController)
