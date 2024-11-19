# Use a Python image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Kafka consumer script
COPY consumer.py .

# Run the consumer
CMD ["python", "consumer.py"]
