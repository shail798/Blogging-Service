# Elasticsearch index name
BLOG_INDEX_NAME = "blogs"

# Fields to search in Elasticsearch
BLOG_SEARCH_FIELDS = ["blog_title", "blog_text"]

# Mapping for the fields you want to return in the search result
BLOG_RESPONSE_FIELDS = {
    "title": "blog_title",
    "text": "blog_text"
}
