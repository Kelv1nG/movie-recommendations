import asyncio

import requests
from playwright.async_api import async_playwright

from .constants import WAIT_FOR_FILTER_MOVIES_RESULT, WAIT_FOR_MOVIE_IMAGES_TO_LOAD


async def fetch_search_results_with_playwright(url) -> str:
    """
    Fetch page content using Playwright for dynamic content.
    :param url: site url
    :return: page content in string format
    """
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto(url, wait_until="domcontentloaded")

        # filter movies only
        movies_navigation_selector = (
            'li.c-productSubpageNavigation_menu_item span:has-text("Movies")'
        )
        if await page.query_selector(movies_navigation_selector):
            await page.click(movies_navigation_selector)
            # Since Metacritic lazily loads images
            await page.mouse.wheel(delta_x=0, delta_y=1350)
            # check if all tags of items are now movies
            wait_for_movie_tag_to_load = page.wait_for_function(
                expression=WAIT_FOR_FILTER_MOVIES_RESULT,
                timeout=10000,
            )
            wait_for_thumbnail_to_load = page.wait_for_function(
                expression=WAIT_FOR_MOVIE_IMAGES_TO_LOAD,
                timeout=10000,
            )
            await asyncio.gather(
                wait_for_movie_tag_to_load,
                wait_for_thumbnail_to_load,
            )
            return await page.content()
        return ""


def fetch_search_results_with_requests(url):
    """
    Fetch page content using Requests for static content.
    :param url: site url
    :return: page content in string format
    """
    response = requests.get(url, headers={"User-agent": "Mozilla/5.0"})
    return response.text
