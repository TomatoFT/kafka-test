# Use a Python image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Kafka producer script
COPY producer.py .

# Run the producer
CMD ["python", "producer.py"]
