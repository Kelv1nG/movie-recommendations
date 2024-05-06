import asyncio
from urllib.parse import quote

import bs4
from bs4 import BeautifulSoup

from app.domain.scraper.abstract_scraper import AbstractMovieScraper
from app.domain.scraper.schemas import HtmlElementSelector, Movie

from .helpers import fetch_search_results_with_playwright

SEARCH_RESULTS_SELECTOR = HtmlElementSelector(
    tag="a", css="c-pageSiteSearch-results-item"
)
# selectors for each result in search results
RESULT_NAME_SELECTOR = HtmlElementSelector(tag="p", css="g-text-medium-fluid")
RESULT_IMAGE_SELECTOR = HtmlElementSelector(tag="picture", css="c-cmsImage")
RESULT_TYPE_SELECTOR = HtmlElementSelector(tag="span", css="c-tagList_button")
RESULT_DATE_SELECTOR = HtmlElementSelector(tag="span", css="u-text-uppercase")
RESULT_RATING_SELECTOR = HtmlElementSelector(tag="div", css="c-siteReviewScore")


class MetacriticScraper(AbstractMovieScraper):
    @property
    def site_url(self):
        return "https://www.metacritic.com"

    async def search_movie_title(self, title: str) -> list:
        response = await self._fetch_search_results_html(title)
        parsed_results = await self._parse_search_results(response)
        return [
            Movie(
                movie_url=details["movie_url"],
                thumbnail_url=details["thumbnail_url"],
                title=details["title"],
                type=details["type"],
                year=details["date"],
                rating=details["rating"],
            )
            for details in parsed_results
            if self._is_result_item_movie(details)
        ]

    def get_movie_details(self, movie_slug):
        pass

    async def _fetch_search_results_html(self, title: str) -> str:
        """
        Search for the given title on metacritic.com
        :param title: A string, the title to search for.
        :return: The HTML content of the search results page.
        """
        encoded_query = quote(f"/search/{title}")
        full_url = f"{self.site_url}{encoded_query}"
        content = await self._get_search_page_content(site_url=full_url)
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
                RESULT_IMAGE_SELECTOR.tag, RESULT_IMAGE_SELECTOR.css
            )
            return image_element is not None

        soup = BeautifulSoup(html_text, features="html.parser")
        result_set = soup.find_all(
            SEARCH_RESULTS_SELECTOR.tag,
            SEARCH_RESULTS_SELECTOR.css,
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
            extract_image_thumbnail_url(tag, RESULT_IMAGE_SELECTOR),
            extract_text(tag, RESULT_NAME_SELECTOR),
            extract_text(tag, RESULT_TYPE_SELECTOR),
            extract_text(tag, RESULT_DATE_SELECTOR),
            extract_text(tag, RESULT_RATING_SELECTOR),
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
    async def _get_search_page_content(site_url) -> str:
        return await fetch_search_results_with_playwright(site_url)
