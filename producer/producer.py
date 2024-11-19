from confluent_kafka import Producer, KafkaException

# Kafka producer configuration
conf = {
    'bootstrap.servers': 'kafka:9092',  # Kafka broker
}

# Create Kafka producer
producer = Producer(conf)

def delivery_report(err, msg):
    """Callback for message delivery report"""
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to topic: {msg.topic()}, partition: {msg.partition()}, value: {msg.value().decode('utf-8')}")

# Topic name
topic = 'example-topic'

# Produce messages
while True:
    # try:
    for i in range(0, 7):  # Send 10 messages
        message = f"Message-{i}"
        key = str(i % 3)  # Messages with the same key will go to the same partition
        print(f"Producing message: {message}")
        producer.produce(
            topic,
            key=key,
            value=message.encode('utf-8'),
            callback=delivery_report
        )
        producer.flush()  # Ensure delivery of the message

    # except KafkaException as e:
    #     print(f"KafkaException: {e}")
    # except KeyboardInterrupt:
    #     print("Producer interrupted.")
    #     break
