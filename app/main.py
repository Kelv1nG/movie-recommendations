from litestar import Litestar

from app.api.controllers.movie_scraper import MovieScraperController

app = Litestar(route_handlers=[MovieScraperController], debug=True)
