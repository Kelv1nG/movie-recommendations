from datetime import date, datetime
from typing import TYPE_CHECKING, Any
from uuid import UUID

import pytest
from litestar.testing import TestClient

if TYPE_CHECKING:
    from collections import abc

    from litestar import Litestar


@pytest.fixture()
def app() -> "Litestar":
    """Always use this `app` fixture and never do `from app.main import app`
    inside a test module. We need to delay import of the `app.main` module
    until as late as possible to ensure we can mock everything necessary before
    the application instance is constructed.

    Returns:
        The application instance.
    """
    # don't want main imported until everything patched.
    from app.main import create_app

    return create_app(debug=True)


@pytest.fixture()
def client(app: "Litestar") -> "abc.Iterator[TestClient]":
    """Client instance attached to app.

    Args:
        app: The app for testing.

    Returns:
        Test client instance.
    """
    with TestClient(app=app) as c:
        yield c
