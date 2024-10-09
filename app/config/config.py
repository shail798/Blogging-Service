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


# Email alert configuration
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USER = os.getenv('EMAIL_USER', 'pythonalerts7@gmail.com')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', 'kwjszrxkiuzjggww')  # Replace with your Gmail App Password
ALERT_RECIPIENT = os.getenv('ALERT_RECIPIENT', 'shail.sodhi798@gmail.com')

FASTAPI_URL = os.getenv('FASTAPI_URL', 'http://localhost:8000/health')  # Default for loca
