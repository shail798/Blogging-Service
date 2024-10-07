# Blogging Service

This is a blogging service that allows users to submit and search blog entries using FastAPI, RabbitMQ, and Elasticsearch.

## Features

- **Blog Submission API**: Accepts blog-title, blog-text, and user-id.
- **Asynchronous Queue**: Uses RabbitMQ for processing blog submissions.
- **Elasticsearch**: Stores and searches blog entries.
- **Docker**: Containerized setup using Docker and Docker Compose.

## Prerequisites

- Docker and Docker Compose installed on your system.

## Setup Instructions

1. **Clone the repository:**

   ```bash
   git clone https://github.com/shail798/Blogging-Service.git
   cd Blogging-Service

2. **Ensure Docker is Running**:

   Make sure Docker is installed and running on your system. If not, download and install Docker from [https://www.docker.com/get-started](https://www.docker.com/get-started).

3. **Build and Run the Services:**

   Use Docker Compose to build and start the services:

   ```bash
   docker-compose up --build

   This will start the following services:

    -FastAPI server at http://localhost:8000
    -RabbitMQ management interface at http://localhost:15672 (default user/pass: guest/guest)
    -Elasticsearch at http://localhost:9200

