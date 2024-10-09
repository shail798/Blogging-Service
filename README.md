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

3. **Using Docker**

   3.1. **Build and Run the Services:**

   Use Docker Compose to build and start the services:
         
         docker-compose up --build

   3.2. **Access the Services:**

   - **FastAPI**: Access the API at `http://localhost:8000`.
   - **RabbitMQ Management**: Access RabbitMQ's management interface at `http://localhost:15672` (default username/password: `guest`/`guest`).
   - **Elasticsearch**: Access Elasticsearch at `http://localhost:9200`.

4. **Using Kubernetes:**

   4.1. **Ensure Kubernetes is Running:**

   Make sure your Kubernetes cluster is running and `kubectl` is configured. If using Docker Desktop, enable Kubernetes in the settings.

   4.2. **Apply Kubernetes Manifests:**

   Apply the Kubernetes deployment files to create the services:

         kubectl apply -f fastapi-deployment.yml
         kubectl apply -f consumer-deployment.yml
         kubectl apply -f rabbitmq-deployment.yml
         kubectl apply -f elasticsearch-deployment.yml

   4.3. **Verify the Deployment:**

   Check the status of the pods to ensure everything is running:

         kubectl get pods
   4.4. **Access the Services:**

   - **FastAPI**: Access the API at `http://localhost:30007` when running Kubernetes in Docker.
   
   - **RabbitMQ Management**: Access RabbitMQ’s management interface using its NodePort:

     ```bash
     http://localhost:<RABBITMQ-MANAGEMENT-PORT>
     ```

   - **Elasticsearch**: Access Elasticsearch using its service URL:

     ```bash
     http://localhost:<ELASTICSEARCH-NODE-PORT>
     ```

   Replace `<RABBITMQ-MANAGEMENT-PORT>` and `<ELASTICSEARCH-NODE-PORT>` with the appropriate ports.


  

   

