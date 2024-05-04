from litestar import Litestar

from app.api.api import router as api_router

app = Litestar(
    debug=True,
)

app.register(api_router)
