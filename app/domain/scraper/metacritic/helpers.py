import asyncio

import requests
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

from app.domain.scraper.metacritic import selectors

from .constants import (WAIT_FOR_FILTER_MOVIES_RESULT,
                        WAIT_FOR_MOVIE_IMAGES_TO_LOAD)


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


def fetch_details_with_requests(url) -> str:
    """
    Fetch page content using Requests for static content.
    :param url: site url
    :return: page content in string format
    """
    response = requests.get(url, headers={"User-agent": "Mozilla/5.0"})
    return response.text


def extract_movie_details(soup: BeautifulSoup) -> dict:
    def extract_details() -> dict:
        _details_dict = {}
        details = soup.find_all(
            selectors.DETAIL_DETAILS_SELECTOR.tag, selectors.DETAIL_DETAILS_SELECTOR.css
        )
        production_companies, release_date, duration, rating, *_ = [
            detail.text.strip() for detail in details
        ]
        _details_dict["production_companies"] = [
            company.strip()
            for company in production_companies.replace("Production Company", "").split(
                ","
            )
        ]
        _details_dict["release_date"] = release_date.replace("Release Date", "").strip()
        _details_dict["duration"] = duration.replace("Duration", "").strip()
        _details_dict["rating"] = rating.replace("Rating", "").strip()

        return _details_dict

    def extract_directors() -> list:

        director_text = soup.find(
            selectors.DETAIL_DIRECTOR_SELECTOR.tag,
            selectors.DETAIL_DIRECTOR_SELECTOR.css,
        ).text.strip()
        index = director_text.find("Directed By:")
        _directors = [
            director.strip()
            for director in director_text[index + len("Directed By:") :].split(",")
        ]
        return _directors

    genres = {
        genre.text.strip()
        for genre in soup.find_all(
            selectors.DETAIL_GENRE_SELECTOR.tag, selectors.DETAIL_GENRE_SELECTOR.css
        )
    }

    casts = [
        cast.text.strip()
        for cast in soup.find_all(
            selectors.DETAIL_CAST_SELECTOR.tag, selectors.DETAIL_CAST_SELECTOR.css
        )
    ]

    description = soup.find(
        selectors.DETAIL_SUMMARY_SELECTOR.tag, selectors.DETAIL_SUMMARY_SELECTOR.css
    ).text.strip()

    meta_score, user_score = [
        score.text.strip()
        for score in soup.find_all(
            selectors.DETAIL_SCORE_SELECTOR.tag, selectors.DETAIL_SCORE_SELECTOR.css
        )
    ]

    details_dict = extract_details()
    directors = extract_directors()

    return {
        "genres": genres,
        "casts": casts,
        "description": description,
        "directors": directors,
        "meta_score": meta_score,
        "user_score": user_score,
        **details_dict,
    }
