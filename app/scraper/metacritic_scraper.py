from urllib.parse import quote

import bs4
import requests
from bs4 import BeautifulSoup

from app.scraper.abstract_scraper import AbstractMovieScraper
from app.scraper.schemas import HtmlElementSelector, Movie

SEARCH_RESULTS_SELECTOR = HtmlElementSelector(
    tag="a", css="c-pageSiteSearch-results-item"
)
# selectors for each result in search results
RESULT_NAME_SELECTOR = HtmlElementSelector(tag="p", css="g-text-medium-fluid")
RESULT_TYPE_SELECTOR = HtmlElementSelector(tag="span", css="c-tagList_button")
RESULT_DATE_SELECTOR = HtmlElementSelector(tag="span", css="u-text-uppercase")
RESULT_RATING_SELECTOR = HtmlElementSelector(tag="div", css="c-siteReviewScore")


class MetacriticScraper(AbstractMovieScraper):
    @property
    def site_url(self):
        return "https://www.metacritic.com/"

    def search_movie_title(self, title: str) -> list:
        response = self._search_title(title)
        parsed_results = self._parse_search_results(response)
        return [
            Movie(
                url=details["url"],
                name=details["name"],
                type=details["type"],
                year=int(details["date"]),
                rating=details["rating"],
            )
            for details in parsed_results
            if self._is_result_movie(details)
        ]

    def get_movie_details(self, movie_slug):
        pass

    def _search_title(self, title: str) -> str:
        """
        Search for the given title on metacritic.com
        :param title: A string, the title to search for.
        :return: The HTML content of the search results page.
        """
        encoded_query = quote(f"search/{title}")
        full_url = f"{self.site_url}{encoded_query}"
        response = requests.get(full_url, headers=self.USER_AGENT)
        return response.text

    def _parse_search_results(self, html_text: str) -> list[dict]:
        """
        Parse the search results from the given HTML text.
        :param html_text: The HTML content of the search results page.
        :return: A list of dictionaries, each dictionary representing a search result.
        """
        soup = BeautifulSoup(html_text, "html.parser")
        result_set = soup.find_all(
            SEARCH_RESULTS_SELECTOR.tag,
            SEARCH_RESULTS_SELECTOR.css,
        )
        parsed_results = [
            self._get_result_details_from_element(result) for result in result_set
        ]
        return parsed_results

    @staticmethod
    def _is_result_movie(result: dict) -> bool:
        """
        Determine if the given result is a movie.
        :param result: A dictionary representing a search result.
        :return: True if the result is a movie, False otherwise.
        """
        return result["type"] == "movie"

    @staticmethod
    def _get_result_details_from_element(tag: bs4.element.Tag) -> dict:
        """
        Extract the details from the given tag.
        :param tag: A BeautifulSoup pageElement representing a search result.
        :return: A dictionary containing the details of the search result.
        """

        def extract_text(element_tag, selector):
            result_tag = element_tag.find(selector.tag, selector.css)
            return result_tag.text.strip() if result_tag is not None else None

        url = tag.get("href")
        name = extract_text(tag, RESULT_NAME_SELECTOR)
        type_ = extract_text(tag, RESULT_TYPE_SELECTOR)
        date = extract_text(tag, RESULT_DATE_SELECTOR)
        rating = extract_text(tag, RESULT_RATING_SELECTOR)
        return {"url": url, "name": name, "type": type_, "date": date, "rating": rating}
