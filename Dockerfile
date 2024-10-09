# Dockerfile

# Use Python image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Set a default command to run FastAPI
ARG APP_TYPE=fastapi
ENV APP_TYPE=${APP_TYPE}
ENV PYTHONPATH=/app 

# Expose FastAPI port
EXPOSE 8000

# Conditional entry point
CMD ["sh", "-c", "if [ \"$APP_TYPE\" = 'consumer' ] ; then python app/consumer.py; else uvicorn app.main:app --host 0.0.0.0 --port 8000; fi"]
