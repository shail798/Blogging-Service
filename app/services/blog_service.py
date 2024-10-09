# blog_service.py

import json
import logging
from app.models.blog import Blog
from app.services.rabbitmq_service import RabbitMQService
from app.constants.blog_constants import BLOG_INDEX_NAME, BLOG_SEARCH_FIELDS, BLOG_RESPONSE_FIELDS
from elasticsearch import Elasticsearch
from app.config.config import ELASTICSEARCH_HOST
from elasticsearch import ConnectionError, TransportError, NotFoundError, RequestError
from app.utils.json_encoder import UUIDEncoder

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
            serialized_data = json.dumps(blog_data, cls=UUIDEncoder)
            self.rabbitmq_service.send_message(serialized_data)
            logging.info("Blog submission successful, blog data queued.")
        except json.JSONDecodeError as jde:
            logging.error(f"JSON serialization error while submitting blog: {jde}")
        except ConnectionError as ce:
            logging.error(f"Connection error while sending blog to RabbitMQ: {ce}")
        except Exception as e:
            logging.error(f"Unexpected error during blog submission to RabbitMQ: {e}")

    async def search_blog(self, user_id: str = None, text: str = None):
        try:
            search_query = {
                "bool": {
                    "must": [
                        {"match": {"user_id": user_id}} if user_id else {},
                        {"match": {"blog_text": text}} if text else {}
                    ]
                }
            }

            # Clean up the search query to remove empty conditions
            search_query["bool"]["must"] = [q for q in search_query["bool"]["must"] if q]

            # Perform the search
            s = self.es_client.search(
                index=BLOG_INDEX_NAME,
                query=search_query
            )
            logging.info(f"Search completed successfully for user_id: {user_id}, text: {text}")

            # Dynamically map the response using BLOG_RESPONSE_FIELDS
            return [
                {response_key: hit["_source"].get(source_key) for response_key, source_key in BLOG_RESPONSE_FIELDS.items()}
                for hit in s["hits"]["hits"]
            ]
        except ConnectionError as ce:
            logging.error(f"Elasticsearch connection error: {ce}")
            return {"error": "Failed to connect to Elasticsearch"}
        except NotFoundError as nfe:
            logging.error(f"Elasticsearch resource not found: {nfe}")
            return {"error": "Resource not found in Elasticsearch"}
        except RequestError as re:
            logging.error(f"Bad Elasticsearch request: {re}")
            return {"error": "Bad request to Elasticsearch"}
        except TransportError as te:
            logging.error(f"Elasticsearch transport error: {te}")
            return {"error": "Elasticsearch transport error"}
        except Exception as e:
            logging.error(f"Unexpected error during search: {e}")
            return {"error": "An unexpected error occurred"}

def save_blog_to_elasticsearch(blog_data):
    try:
        document_body = {
            "blog_title": blog_data.get("blog_title"),
            "blog_text": blog_data.get("blog_text"),
            "user_id": blog_data.get("user_id")
        }

        es_client = Elasticsearch(hosts=[ELASTICSEARCH_HOST])
        response = es_client.index(
            index=BLOG_INDEX_NAME,
            document=document_body,
            refresh=True
        )
        logging.info(f"Blog entry saved to Elasticsearch with ID: {response['_id']}")
    except Exception as e:
        logging.error(f"Error saving blog to Elasticsearch: {e}")
        raise e