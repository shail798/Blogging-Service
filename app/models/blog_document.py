from app.constants.blog_constants import BLOG_INDEX_NAME
from elasticsearch_dsl import Document, Text

class BlogDocument(Document):
    blog_title = Text()
    blog_text = Text()

    class Index:
        name = BLOG_INDEX_NAME