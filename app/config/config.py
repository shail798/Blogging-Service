from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# RabbitMQ configuration (environment-based)
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
RABBITMQ_PORT = int(os.getenv('RABBITMQ_PORT', 5672))  # Default to port 5672
RABBITMQ_QUEUE_NAME = os.getenv('RABBITMQ_QUEUE_NAME', 'blog_queue')

# Elasticsearch configuration (environment-based)
ELASTICSEARCH_HOST = os.getenv('ELASTICSEARCH_HOST', 'http://localhost:9200')
