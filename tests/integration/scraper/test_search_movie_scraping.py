from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from httpx import AsyncClient

from app.scraper.metacritic import constants

if TYPE_CHECKING:
    from httpx import AsyncClient


async def test_search_results_meets_image_loaded_criteria(client: AsyncClient):
    async def search_title_and_assert_results(title: str):
        response = await client.get("api/movies?title={}".format(title))
        content = response.json()[: constants.COUNT_OF_FIRST_TAGS]

        assert all(item["thumbnail_url"] is not None for item in content)
        assert response.status_code == 200

    search_list = ["hotel", "spider", "god"]
    await asyncio.gather(
        *[search_title_and_assert_results(title) for title in search_list]
    )


async def test_get_movie_details(client: AsyncClient):
    async def get_details_and_assert_structure(slug: str):
        response = await client.get("api/movies/{}".format(slug))
        assert response.status_code == 200
        movie_data = response.json()

        for key, value in movie_data.items():
            assert key in [
                "movie_url",
                "movie_slug",
                "directors",
                "description",
                "genres",
                "release_date",
                "duration",
                "casts",
                "production_companies",
                "meta_score",
                "user_score",
                "rating",
            ]
            assert value, f"{key} is blank"

    search_list = ["toy-story", "the-grand-budapest-hotel", "ratatouille"]
    await asyncio.gather(
        *[get_details_and_assert_structure(slug) for slug in search_list]
    )
