from __future__ import annotations

from typing import TYPE_CHECKING

from httpx import AsyncClient

from app.domain.scraper.metacritic import constants

if TYPE_CHECKING:
    from httpx import AsyncClient

import asyncio


async def test_search_results_meets_image_loaded_criteria(client: AsyncClient):
    async def search_title_and_assert_results(title: str):
        response = await client.get("api/movies?title={}".format(title))
        content = response.json()[:constants.COUNT_OF_FIRST_TAGS]

        assert all(item["thumbnail_url"] is not None for item in content)
        assert response.status_code == 200

    search_list = ["hotel", "spider", "god"]
    await asyncio.gather(
        *[search_title_and_assert_results(title) for title in search_list]
    )
