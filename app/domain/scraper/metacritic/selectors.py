from app.domain.scraper.schemas import HtmlElementSelector

SEARCH_RESULTS_SELECTOR = HtmlElementSelector(
    tag="a", css="c-pageSiteSearch-results-item"
)
# selectors for each result in search results
RESULT_NAME_SELECTOR = HtmlElementSelector(tag="p", css="g-text-medium-fluid")
RESULT_IMAGE_SELECTOR = HtmlElementSelector(tag="picture", css="c-cmsImage")
RESULT_TYPE_SELECTOR = HtmlElementSelector(tag="span", css="c-tagList_button")
RESULT_DATE_SELECTOR = HtmlElementSelector(tag="span", css="u-text-uppercase")
RESULT_RATING_SELECTOR = HtmlElementSelector(tag="div", css="c-siteReviewScore")

# selectors for specific movie
DETAIL_NAME_SELECTOR = HtmlElementSelector(tag="div", css="c-productHero_title")
DETAIL_SUMMARY_SELECTOR = HtmlElementSelector(
    tag="span", css="c-productDetails_description"
)
DETAIL_GENRE_SELECTOR = HtmlElementSelector(tag="li", css="c-genreList_item")
DETAIL_CAST_SELECTOR = HtmlElementSelector(tag="h3", css="c-globalPersonCard_name")
DETAIL_DIRECTOR_SELECTOR = HtmlElementSelector(
    tag="div", css="c-productDetails_staff_directors"
)
DETAIL_DETAILS_SELECTOR = HtmlElementSelector(
    tag="div", css="c-movieDetails_sectionContainer"
)
DETAIL_SCORE_SELECTOR = HtmlElementSelector(
    tag="div", css="c-productScoreInfo_scoreNumber u-float-right"
)
