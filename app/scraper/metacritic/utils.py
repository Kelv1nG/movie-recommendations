import requests
from playwright.sync_api import sync_playwright


def fetch_search_results_with_playwright(url) -> str:
    """
    Fetch page content using Playwright for dynamic content.
    :param url: site url
    :return: page content in string format
    """
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_load_state("load")

        # filter movies only
        movies_navigation_selector = (
            'li.c-productSubpageNavigation_menu_item span:has-text("Movies")'
        )
        if page.query_selector(movies_navigation_selector):
            page.click(movies_navigation_selector)
            # Since Metacritic lazily loads images
            page.keyboard.down("End")
            # check if all tags of items are now movies
            page.wait_for_function(
                expression="""
                    () => { 
                        const tags = document.querySelectorAll(".c-tagList_item")
                        return Array.from(tags).every(tag => tag.innerText === "movie");
                    }
                    """,
                timeout=10000,
            )
            page.wait_for_function(
                expression="""
                    () => { 
                        const images = document.querySelectorAll("img");
                        const lastImages = Array.from(images).slice(-2);
                        return lastImages.some(img => img.src !== ""); 
                    }
                    """,
                timeout=10000,
            )
            return page.content()
        return ""


def fetch_search_results_with_requests(url):
    """
    Fetch page content using Requests for static content.
    :param url: site url
    :return: page content in string format
    """
    response = requests.get(url, headers={"User-agent": "Mozilla/5.0"})
    return response.text
