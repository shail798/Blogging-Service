import time
import json
import logging
from elasticsearch_dsl.connections import connections
from app.services.rabbitmq_service import RabbitMQService
from app.services.blog_service import save_blog_to_elasticsearch
from app.constants.blog_constants import BLOG_INDEX_NAME, BLOG_RESPONSE_FIELDS
from app.constants.rabbitmq_constants import MAX_RETRIES,RETRY_DELAY,MAX_REQUEUE_ATTEMPTS
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


def process_blog(ch, method, properties, body):
    try:
        blog_data = json.loads(body.decode('utf-8'))
        
        if isinstance(blog_data, str):
            blog_data = json.loads(blog_data)

        logging.info(f"Parsed blog data: {blog_data}")

        if BLOG_RESPONSE_FIELDS['title'] not in blog_data or BLOG_RESPONSE_FIELDS['text'] not in blog_data:
            raise ValueError("Missing required fields in blog data.")

        save_blog_to_elasticsearch(blog_data)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except ValueError as ve:
        logging.error(f"Validation error: {ve}. Rejecting message.")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    except Exception as e:
        # Check if properties and headers exist before accessing them
        requeue_count = properties.headers.get('x-requeue-count', 0) if properties and properties.headers else 0
        if requeue_count < MAX_REQUEUE_ATTEMPTS:
            # Increment the requeue count and add it to message headers
            headers = properties.headers or {}
            headers['x-requeue-count'] = requeue_count + 1
            logging.error(f"Error: {e}. Requeuing message (attempt {requeue_count + 1}).")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        else:
            logging.error(f"Maximum requeue attempts reached for message. Discarding message: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

if __name__ == "__main__":
    # Connect to Elasticsearch with retry
    connect_to_elasticsearch()

    # Connect to RabbitMQ with retry
    rabbitmq_service = connect_to_rabbitmq()

    try:
        rabbitmq_service.channel.basic_consume(queue=rabbitmq_service.queue_name, on_message_callback=process_blog)
        logging.info("Waiting for messages from RabbitMQ...")
        rabbitmq_service.channel.start_consuming()
    except Exception as e:
        logging.error(f"Unexpected error in the consumer: {e}")
        raise SystemExit("Critical failure in the consumer.")
