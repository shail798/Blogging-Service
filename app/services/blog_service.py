# blog_service.py

import logging
from app.models.blog import Blog
from app.services.rabbitmq_service import RabbitMQService
from app.constants.blog_constants import BLOG_INDEX_NAME, BLOG_SEARCH_FIELDS, BLOG_RESPONSE_FIELDS
from elasticsearch import Elasticsearch
from app.config.config import ELASTICSEARCH_HOST
from elasticsearch import ConnectionError, TransportError, NotFoundError, RequestError

# Set up logging for better visibility
logging.basicConfig(level=logging.INFO)

class BlogService:
    def __init__(self):
        try:
            self.rabbitmq_service = RabbitMQService()
            self.es_client = Elasticsearch(hosts=[ELASTICSEARCH_HOST])
            logging.info("BlogService initialized successfully.")
        except Exception as e:
            logging.error(f"Error initializing BlogService: {e}")

    def submit_blog(self, blog: Blog):
        try:
            blog_data = blog.dict()
            # Send the blog data to RabbitMQ
            self.rabbitmq_service.send_message(blog_data)
            logging.info("Blog submission successful, blog data queued.")
        except Exception as e:
            logging.error(f"Error submitting blog to RabbitMQ: {e}")
            # Handle error (could also raise an exception depending on requirements)

    def search_blog(self, query: str):
        try:
            # Search the Elasticsearch index using constants for the fields and index
            s = self.es_client.search(
                index=BLOG_INDEX_NAME,
                query={"multi_match": {"query": query, "fields": BLOG_SEARCH_FIELDS}}
            )
            logging.info(f"Search completed successfully for query: {query}")

            # Dynamically map the response using BLOG_RESPONSE_FIELDS
            return [
                {response_key: hit["_source"].get(source_key) for response_key, source_key in BLOG_RESPONSE_FIELDS.items()}
                for hit in s["hits"]["hits"]
            ]
        except ConnectionError as ce:  # Catch connection-related errors
            logging.error(f"Elasticsearch connection error: {ce}")
            return {"error": "Failed to connect to Elasticsearch"}
        except NotFoundError as nfe:  # Catch not-found errors (e.g., index or document not found)
            logging.error(f"Elasticsearch resource not found: {nfe}")
            return {"error": "Resource not found in Elasticsearch"}
        except RequestError as re:  # Catch issues with the query itself (e.g., malformed query)
            logging.error(f"Bad Elasticsearch request: {re}")
            return {"error": "Bad request to Elasticsearch"}
        except TransportError as te:  # Catch transport-related errors (e.g., bad requests, HTTP issues)
            logging.error(f"Elasticsearch transport error: {te}")
            return {"error": "Elasticsearch transport error"}
        except Exception as e:  # Catch any other unexpected exceptions
            logging.error(f"Unexpected error during search: {e}")
            return {"error": "An unexpected error occurred"}