import time
import logging
import requests
import smtplib
from email.message import EmailMessage
from config.config import (
    FASTAPI_URL,
    RABBITMQ_HOST,
    RABBITMQ_PORT,
    ELASTICSEARCH_HOST,
    EMAIL_HOST,
    EMAIL_PORT,
    EMAIL_USER,
    EMAIL_PASSWORD,
    ALERT_RECIPIENT,
)
from constants.healthcheck_constants import RETRY_DELAY, RETRY_LIMIT

logging.basicConfig(level=logging.INFO)

class HealthChecker:
    def __init__(self):
        self.services = {
            "fastapi": FASTAPI_URL,
            "rabbitmq": f"http://{RABBITMQ_HOST}:{RABBITMQ_PORT}/api/health/checks/alarms",
            "elasticsearch": f"{ELASTICSEARCH_HOST}/_cluster/health"
        }

    def send_alert(self, service_name):
        subject = f"ALERT: {service_name} Service Down"
        body = f"{service_name} is down after multiple retries."

        # Create the email message using Python's built-in EmailMessage
        msg = EmailMessage()
        msg.set_content(body)
        msg['Subject'] = subject
        msg['From'] = EMAIL_USER
        msg['To'] = ALERT_RECIPIENT

        try:
            with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
                server.starttls()
                server.login(EMAIL_USER, EMAIL_PASSWORD)
                server.send_message(msg)
            logging.info(f"Alert email sent for {service_name}.")
        except Exception as e:
            logging.error(f"Failed to send alert email for {service_name}: {e}")

    def check_service(self, service_name, url):
        for attempt in range(1, RETRY_LIMIT + 1):
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    logging.info(f"{service_name} is healthy.")
                    return True
                else:
                    logging.warning(f"{service_name} returned status code {response.status_code}.")
            except requests.RequestException as e:
                logging.error(f"Error checking {service_name}: {e}")

            logging.info(f"Retrying {service_name} in {RETRY_DELAY} seconds... (Attempt {attempt}/{RETRY_LIMIT})")
            time.sleep(RETRY_DELAY)

        # If the service is still down after all retries, send an alert.
        self.send_alert(service_name)
        return False

    def run_checks(self):
        while True:
            for service, url in self.services.items():
                self.check_service(service, url)
            time.sleep(120)  # Run health check every 5 minutes

if __name__ == "__main__":
    health_checker = HealthChecker()
    health_checker.run_checks()
