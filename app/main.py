from litestar import Litestar

from app.api.routers import route_handlers


def create_app(**kwargs: any) -> Litestar:
    return Litestar(
        route_handlers=route_handlers,
        **kwargs,
    )


app = create_app(debug=True)
