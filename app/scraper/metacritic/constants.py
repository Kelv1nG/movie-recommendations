COUNT_OF_FIRST_TAGS = 15

WAIT_FOR_FILTER_MOVIES_RESULT = """
    () => {{ 
        const tags = document.querySelectorAll(".c-tagList_item")
        const firstTags = Array.from(tags).slice(0, {count_of_first_tags})
        return Array.from(firstTags).every(tag => tag.innerText === "movie");
    }}
""".format(
    count_of_first_tags=COUNT_OF_FIRST_TAGS
)

WAIT_FOR_MOVIE_IMAGES_TO_LOAD = """
    () => {{
        const images = document.querySelectorAll("img");
        const firstImages = Array.from(images).slice(0, {count_of_first_tags});
        return Promise.all(Array.from(firstImages).map(
            img => new Promise((resolve) => {{
                if (img.complete) {{
                    resolve();
                }} else {{
                    img.onload = resolve;
                }}
            }})
        ));
    }}
""".format(
    count_of_first_tags=COUNT_OF_FIRST_TAGS
)
