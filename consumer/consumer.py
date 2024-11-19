from confluent_kafka import Consumer, KafkaError

# Kafka consumer configuration
conf = {
    'bootstrap.servers': 'kafka:9092',          # Kafka broker
    'group.id': 'example-group',                # Consumer group ID
    'auto.offset.reset': 'earliest',            # Start from the beginning if no offset is found
    'partition.assignment.strategy': 'roundrobin',  # Can be 'range', 'roundrobin', or 'sticky'
}

# Create Kafka consumer
consumer = Consumer(conf)

# Subscribe to the topic
topic = 'example-topic'
consumer.subscribe([topic])

try:
    while True:
        msg = consumer.poll(timeout=1.0)
        if msg is None:
            continue  # No message
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                print(f"End of partition reached: {msg.topic()}[{msg.partition()}]")
            else:
                print(f"Error: {msg.error()}")
            continue

        # Process the message
        print(f"Consumed message: {msg.value().decode('utf-8')} from partition: {msg.partition()}")

except KeyboardInterrupt:
    print("Consumer interrupted.")
finally:
    consumer.close()
