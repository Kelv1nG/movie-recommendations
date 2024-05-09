import asyncio
from urllib.parse import quote

import bs4
from bs4 import BeautifulSoup

from app.domain.scraper import schemas
from app.domain.scraper.abstract_scraper import AbstractMovieScraper
from app.domain.scraper.metacritic import selectors

from .helpers import (extract_movie_details, fetch_details_with_requests,
                      fetch_search_results_with_playwright)


class MetacriticScraper(AbstractMovieScraper):
    @property
    def site_url(self):
        return "https://www.metacritic.com"

    async def search_movie_title(self, title: str) -> list:
        response = await self._fetch_search_results_html(title)
        parsed_results = await self._parse_search_results(response)
        return [
            details for details in parsed_results if self._is_result_item_movie(details)
        ]

    def get_movie_details(self, movie_slug: str) -> dict:
        encoded_query = quote(f"/movie/{movie_slug}")
        url = f"{self.site_url}{encoded_query}"
        soup = BeautifulSoup(
            fetch_details_with_requests(url=url), features="html.parser"
        )
        details = extract_movie_details(soup)
        return {"movie_url": url, "movie_slug": movie_slug, **details}

    async def _fetch_search_results_html(self, title: str) -> str:
        """
        Search for the given title on metacritic.com
        :param title: A string, the title to search for.
        :return: The HTML content of the search results page.
        """
        encoded_query = quote(f"/search/{title}")
        url = f"{self.site_url}{encoded_query}"
        content = await self._get_search_page_content(url=url)
        return content

    async def _parse_search_results(self, html_text: str) -> list[dict]:
        """
        Parse the search results from the given HTML text.
        :param html_text: The HTML content of the search results page.
        :return: A list of dictionaries, each dictionary representing a search result.
        """

        def has_image_element(element):
            """
            Check if the given HTML element contains an image element matching RESULT_IMAGE_SELECTOR.
            :param element: BeautifulSoup element
            :return: True if the element contains an image element, False otherwise.
            """
            image_element = element.find(
                selectors.RESULT_IMAGE_SELECTOR.tag, selectors.RESULT_IMAGE_SELECTOR.css
            )
            return image_element is not None

        soup = BeautifulSoup(html_text, features="html.parser")
        result_set = soup.find_all(
            selectors.SEARCH_RESULTS_SELECTOR.tag,
            selectors.SEARCH_RESULTS_SELECTOR.css,
        )
        filtered_result_set = filter(has_image_element, result_set)
        parsed_results = [
            await self._get_result_details_from_element(result)
            for result in filtered_result_set
        ]
        return parsed_results

    @staticmethod
    def _is_result_item_movie(result: dict) -> bool:
        """
        Determine if the given result is a movie.
        :param result: A dictionary representing a search result.
        :return: True if the result is a movie, False otherwise.
        """
        return result["type"] == "movie"

    async def _get_result_details_from_element(self, tag: bs4.element.Tag) -> dict:
        """
        Extract the details from the given tag.
        :param tag: A BeautifulSoup pageElement representing a search result.
        :return: A dictionary containing the details of the search result.
        """

        async def extract_text(element_tag, selector):
            result_tag = element_tag.find(selector.tag, selector.css)
            return result_tag.text.strip() if result_tag is not None else None

        async def extract_image_thumbnail_url(element_tag, selector):
            result_tag = element_tag.find(selector.tag, selector.css)
            if result_tag:
                image_tag = result_tag.find("img")
                return image_tag["src"] if image_tag else None
            return None

        movie_url = f'{self.site_url}{tag.get("href")}'
        thumbnail_url, title, type_, date, rating = await asyncio.gather(
            extract_image_thumbnail_url(tag, selectors.RESULT_IMAGE_SELECTOR),
            extract_text(tag, selectors.RESULT_NAME_SELECTOR),
            extract_text(tag, selectors.RESULT_TYPE_SELECTOR),
            extract_text(tag, selectors.RESULT_DATE_SELECTOR),
            extract_text(tag, selectors.RESULT_RATING_SELECTOR),
        )
        return {
            "movie_url": movie_url,
            "thumbnail_url": thumbnail_url,
            "title": title,
            "type": type_,
            "date": date,
            "rating": rating,
        }

    @staticmethod
    async def _get_search_page_content(url) -> str:
        return await fetch_search_results_with_playwright(url)
