from app.api.controllers.movie_scraper import MovieScraperController
from litestar import Router

router = Router(path="/api")

router.register(MovieScraperController)

