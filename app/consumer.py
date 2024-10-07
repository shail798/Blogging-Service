import time
import json
import logging
from elasticsearch_dsl import Document, Text
from elasticsearch_dsl.connections import connections
from app.services.rabbitmq_service import RabbitMQService
from app.constants.blog_constants import BLOG_INDEX_NAME, BLOG_RESPONSE_FIELDS
from app.constants.rabbitmq_constants import MAX_RETRIES,RETRY_DELAY
from app.config.config import ELASTICSEARCH_HOST
from elasticsearch import ConnectionError, TransportError, NotFoundError, RequestError

from pika.exceptions import AMQPConnectionError, ChannelClosed

# Set up logging
logging.basicConfig(level=logging.INFO)


def connect_to_elasticsearch():
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            # Try to connect to Elasticsearch using the provided host
            connections.create_connection(hosts=[ELASTICSEARCH_HOST])
            logging.info("Connected to Elasticsearch successfully.")
            return
        except ConnectionError as e:  # Handle connection issues specifically
            logging.error(f"Error connecting to Elasticsearch (attempt {attempt}/{MAX_RETRIES}): {e}")
        except TransportError as e:  # Handle other transport-related issues (e.g., timeouts)
            logging.error(f"Elasticsearch transport error (attempt {attempt}/{MAX_RETRIES}): {e}")
        except Exception as e:  # Catch any other exceptions
            logging.error(f"Unexpected error occurred while connecting to Elasticsearch (attempt {attempt}/{MAX_RETRIES}): {e}")

        if attempt < MAX_RETRIES:
            logging.info(f"Retrying connection to Elasticsearch in {RETRY_DELAY} seconds...")
            time.sleep(RETRY_DELAY)
        else:
            raise SystemExit("Failed to connect to Elasticsearch after multiple attempts.")

def connect_to_rabbitmq():
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            # Initialize RabbitMQ service
            rabbitmq_service = RabbitMQService()
            logging.info("Connected to RabbitMQ successfully.")
            return rabbitmq_service
        except AMQPConnectionError as amqp_err:
            logging.error(f"Error connecting to RabbitMQ (attempt {attempt}/{MAX_RETRIES}): {amqp_err}")
        except ChannelClosed as channel_err:
            logging.error(f"RabbitMQ channel was closed (attempt {attempt}/{MAX_RETRIES}): {channel_err}")
        except Exception as e:
            logging.error(f"Unexpected error in RabbitMQ (attempt {attempt}/{MAX_RETRIES}): {e}")

        if attempt < MAX_RETRIES:
            logging.info(f"Retrying connection to RabbitMQ in {RETRY_DELAY} seconds...")
            time.sleep(RETRY_DELAY)
        else:
            raise SystemExit("Failed to connect to RabbitMQ after multiple attempts.")

# Define the Elasticsearch document for blogs
class BlogDocument(Document):
    blog_title = Text()
    blog_text = Text()

    class Index:
        name = BLOG_INDEX_NAME  # Use constant for index name

# Function to process a message and store it in Elasticsearch
def process_blog(ch, method, properties, body):
    try:
        blog_data = json.loads(body)

        # Validate the presence of necessary fields based on the constant map
        if BLOG_RESPONSE_FIELDS['title'] not in blog_data or BLOG_RESPONSE_FIELDS['text'] not in blog_data:
            raise ValueError("Missing required fields in blog data.")

        # Save blog entry to Elasticsearch
        blog = BlogDocument(
            blog_title=blog_data[BLOG_RESPONSE_FIELDS['title']], 
            blog_text=blog_data[BLOG_RESPONSE_FIELDS['text']]
        )
        blog.save()
        logging.info(f"Blog entry saved to Elasticsearch: {blog_data[BLOG_RESPONSE_FIELDS['title']]}")

        # Acknowledge the message in RabbitMQ
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except ValueError as ve:
        logging.error(f"Validation error: {ve}. Rejecting message.")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)  # Do not requeue invalid messages
    except RequestError as re:  # Handle query errors in Elasticsearch
        logging.error(f"Request error with Elasticsearch: {re}. Requeuing message.")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)  # Requeue messages in case of Elasticsearch failure
    except NotFoundError as nf_err:  # Handle not-found errors (e.g., missing index)
        logging.error(f"Index or document not found in Elasticsearch: {nf_err}. Requeuing message.")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    except TransportError as te:  # Handle transport errors
        logging.error(f"Transport error with Elasticsearch: {te}. Requeuing message.")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    except Exception as e:
        logging.error(f"Unexpected error occurred while processing message: {e}. Requeuing message.")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

if __name__ == "__main__":
    # Connect to Elasticsearch with retry
    connect_to_elasticsearch()

    # Connect to RabbitMQ with retry
    rabbitmq_service = connect_to_rabbitmq()

    # Start consuming messages from the queue
    try:
        rabbitmq_service.channel.basic_consume(queue=rabbitmq_service.queue_name, on_message_callback=process_blog)
        logging.info("Waiting for messages from RabbitMQ...")
        rabbitmq_service.channel.start_consuming()
    except Exception as e:
        logging.error(f"Unexpected error in the consumer: {e}")
        raise SystemExit("Critical failure in the consumer.")
