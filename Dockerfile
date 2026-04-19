# Use required Spark base image
FROM apache/spark:3.5.0

# Switch to root to install packages
USER root

# Install Python3 and pip
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies except pyspark (provided by Spark image)
RUN grep -v '^pyspark==' requirements.txt > requirements-docker.txt && \
    pip3 install --no-cache-dir -r requirements-docker.txt

# Ensure pyspark Python module is available and aligned with Spark 3.5.0
RUN pip3 install --no-cache-dir pyspark==3.5.0

# Copy application code
COPY . .

# Expose ports
EXPOSE 5000 7077 8080

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV SPARK_LOCAL_IP=127.0.0.1

# Run Flask API
CMD ["python3", "backend/api/app.py"]
