# Use an official Apache Airflow image as the base
FROM apache/airflow:2.2.3

# Set the working directory inside the container
WORKDIR /opt/airflow

# Copy requirements.txt to install additional Python libraries
COPY requirements.txt .

USER root

# Install system dependencies (e.g., gcloud CLI for Google Cloud)
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    gnupg && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - && \
    echo "deb http://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    apt-get update && apt-get install -y google-cloud-sdk && \
    apt-get clean

USER airflow

# Install Python dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir sqlalchemy psycopg2-binary
