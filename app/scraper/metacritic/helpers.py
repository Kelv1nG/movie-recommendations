import asyncio

import requests
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

from . import selectors
from .constants import WAIT_FOR_FILTER_MOVIES_RESULT, WAIT_FOR_MOVIE_IMAGES_TO_LOAD

WAIT_TIMEOUT = 15000


def extract_text(element_tag, selector):
    result_tag = element_tag.find(selector.tag, selector.css)
    return result_tag.get_text(strip=True) if result_tag is not None else None


def extract_image_thumbnail_url(element_tag, selector):
    result_tag = element_tag.find(selector.tag, class_=selector.css)
    if result_tag:
        image_tag = result_tag.find("img")
        if image_tag and image_tag.has_attr("src"):
            return image_tag["src"]
    return None


def fetch_details_with_requests(url) -> str:
    """
    Fetch page content using Requests for static content.
    :param url: site url
    :return: page content in string format
    """
    response = requests.get(url, headers={"User-agent": "Mozilla/5.0"})
    return response.text


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
        if await page.query_selector(selectors.MOVIES_NAVIGATION_SELECTOR_STRING):
            await page.click(selectors.MOVIES_NAVIGATION_SELECTOR_STRING)
            # Since Metacritic lazily loads images
            await page.mouse.wheel(delta_x=0, delta_y=1350)
            # check if all tags of items are now movies
            wait_for_movie_tag_to_load = page.wait_for_function(
                expression=WAIT_FOR_FILTER_MOVIES_RESULT,
                timeout=WAIT_TIMEOUT,
            )
            wait_for_thumbnail_to_load = page.wait_for_function(
                expression=WAIT_FOR_MOVIE_IMAGES_TO_LOAD,
                timeout=WAIT_TIMEOUT,
            )
            await asyncio.gather(
                wait_for_movie_tag_to_load,
                wait_for_thumbnail_to_load,
            )
            return await page.content()
        return ""


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
        director_text = extract_text(soup, selectors.DETAIL_DIRECTOR_SELECTOR)
        index = director_text.find("Directed By:")
        _directors = [
            director.strip()
            for director in director_text[index + len("Directed By:") :].split(",")
        ]
        return _directors

    genres = {
        genre.get_text(strip=True)
        for genre in soup.find_all(
            selectors.DETAIL_GENRE_SELECTOR.tag, selectors.DETAIL_GENRE_SELECTOR.css
        )
        if genre and genre.get_text(strip=True)
    }

    casts = [
        cast.get_text(strip=True)
        for cast in soup.find_all(
            selectors.DETAIL_CAST_SELECTOR.tag,
            class_=selectors.DETAIL_CAST_SELECTOR.css,
        )
        if cast and cast.get_text(strip=True)
    ]

    description = extract_text(soup, selectors.DETAIL_SUMMARY_SELECTOR)

    meta_score, user_score = [
        score.get_text(strip=True)
        for score in soup.find_all(
            selectors.DETAIL_SCORE_SELECTOR.tag, selectors.DETAIL_SCORE_SELECTOR.css
        )
        if score and score.get_text(strip=True)
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
