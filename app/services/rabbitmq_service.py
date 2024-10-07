import pika
import json
import logging
from app.config.config import RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_QUEUE_NAME
from app.constants.rabbitmq_constants import QUEUE_DURABLE, PERSISTENT_DELIVERY_MODE

logging.basicConfig(level=logging.INFO)

class RabbitMQService:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.queue_name = RABBITMQ_QUEUE_NAME
        try:
            # Establish RabbitMQ connection with host and port, with retries and timeout
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=RABBITMQ_HOST,
                    port=RABBITMQ_PORT,
                    connection_attempts=5,  # Number of connection attempts
                    retry_delay=10  # Delay in seconds between attempts
                )
            )
            self.channel = self.connection.channel()

            # Declare the queue with durable property
            self.channel.queue_declare(queue=RABBITMQ_QUEUE_NAME, durable=QUEUE_DURABLE)
            logging.info(f"Connected to RabbitMQ, declared queue: {RABBITMQ_QUEUE_NAME}")
        except pika.exceptions.AMQPConnectionError as e:
            logging.error(f"Failed to connect to RabbitMQ: {e}")
            raise SystemExit("Failed to connect to RabbitMQ.")
        except Exception as e:
            logging.error(f"Unexpected error occurred during RabbitMQ initialization: {e}")
            raise SystemExit("Unexpected failure in RabbitMQ setup.")

    def send_message(self, message):
        try:
            # Publish the message with persistent delivery mode
            self.channel.basic_publish(
                exchange='',
                routing_key=RABBITMQ_QUEUE_NAME,
                body=json.dumps(message),
                properties=pika.BasicProperties(delivery_mode=PERSISTENT_DELIVERY_MODE)
            )
            logging.info(f"Message sent to queue: {RABBITMQ_QUEUE_NAME}")
        except pika.exceptions.AMQPError as e:
            logging.error(f"Failed to publish message to RabbitMQ: {e}")
        except Exception as e:
            logging.error(f"Unexpected error occurred during message publishing: {e}")

    def close_connection(self):
        try:
            if self.connection:
                self.connection.close()
                logging.info("RabbitMQ connection closed")
        except pika.exceptions.AMQPError as e:
            logging.error(f"Failed to close RabbitMQ connection: {e}")
        except Exception as e:
            logging.error(f"Unexpected error occurred while closing RabbitMQ connection: {e}")
